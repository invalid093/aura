"""Integration tests: specification validation, the full run lifecycle, reporting.

These exercise the framework end to end in a temporary repository root, so they neither
read nor write the real research record.
"""

from __future__ import annotations

import io
import json
import os
import tempfile
import unittest

import yaml

from aura.compare import compare
from aura.errors import SpecificationError
from aura.evidence import EvidenceClass, Statement
from aura.gates import summarise
from aura.provenance import capture, trace
from aura.registry import Registry
from aura.report import generate as generate_report
from aura.runner import ExecutionResult, run
from aura.spec import ExperimentSpec
from aura.status import Status
from aura.validation import validate_spec


def make_git_root(root: str) -> bool:
    """Initialise ``root`` as a git working copy so provenance can be certified.

    Returns False if git is unavailable, letting callers skip rather than assert a
    weaker property. Provenance completeness genuinely depends on a code version being
    recordable, so the happy path must be tested inside a repository.
    """
    import subprocess

    try:
        for args in (
            ["init", "-q"],
            ["config", "user.email", "test@example.invalid"],
            ["config", "user.name", "test"],
            ["commit", "-q", "--allow-empty", "-m", "fixture"],
        ):
            r = subprocess.run(["git", *args], cwd=root, capture_output=True, timeout=30)
            if r.returncode != 0:
                return False
    except (OSError, subprocess.SubprocessError):
        return False
    return True


def minimal_spec(**overrides) -> dict:
    """A specification that passes validation, as a mutable mapping."""
    data = {
        "experiment_id": "DEMO-9001",
        "title": "Integration fixture",
        "kind": "infrastructure",
        "research_question": "Does the framework validate and execute a specification end to end?",
        "hypothesis": "A well-formed specification runs to completion and passes its gates.",
        "prediction": "All declared gates return PASS and a conclusion is emitted.",
        "variables": {
            "independent": {"level": 1.0},
            "dependent": ["value"],
            "controlled": {"mode": "fixture"},
        },
        "metrics": ["value"],
        "model": {
            "identifier": "fixture-model",
            "version": "1.0",
            "validity_envelope": {"level": [0.0, 10.0]},
        },
        "datasets": [{"identifier": "DS-FIX", "version": "1.0", "role": "output"}],
        "assumptions": ["The fixture model is deterministic."],
        "gates": ["provenance_complete", "model_validity_envelope", "numerical_validity",
                  "data_completeness"],
        "randomisation": {"enabled": False},
        "frozen_test": {"enabled": False},
        "output_dir": "results/DEMO-9001",
        "status": "PLANNED",
    }
    data.update(overrides)
    return data


class TestSpecValidation(unittest.TestCase):
    def test_valid_spec_passes(self) -> None:
        spec = ExperimentSpec.from_mapping(minimal_spec())
        with tempfile.TemporaryDirectory() as root:
            self.assertTrue(validate_spec(spec, root=root).ok)

    def test_missing_hypothesis_rejected_structurally(self) -> None:
        data = minimal_spec()
        del data["hypothesis"]
        with self.assertRaises(SpecificationError):
            ExperimentSpec.from_mapping(data)

    def test_placeholder_hypothesis_rejected(self) -> None:
        spec = ExperimentSpec.from_mapping(minimal_spec(hypothesis="TBD"))
        with tempfile.TemporaryDirectory() as root:
            report = validate_spec(spec, root=root)
        self.assertFalse(report.ok)
        self.assertTrue(any("hypothesis" in str(p) for p in report.errors))

    def test_empty_assumptions_rejected(self) -> None:
        spec = ExperimentSpec.from_mapping(minimal_spec(assumptions=[]))
        with tempfile.TemporaryDirectory() as root:
            self.assertFalse(validate_spec(spec, root=root).ok)

    def test_unknown_gate_rejected(self) -> None:
        spec = ExperimentSpec.from_mapping(minimal_spec(gates=["not_a_gate"]))
        with tempfile.TemporaryDirectory() as root:
            report = validate_spec(spec, root=root)
        self.assertFalse(report.ok)
        self.assertTrue(any("unknown gate" in str(p) for p in report.errors))

    def test_id_collision_rejected(self) -> None:
        spec = ExperimentSpec.from_mapping(minimal_spec())
        with tempfile.TemporaryDirectory() as root:
            report = validate_spec(spec, root=root, known_experiment_ids=["DEMO-9001"])
        self.assertFalse(report.ok)

    def test_absolute_output_path_rejected(self) -> None:
        """No machine-specific paths: a public repository policy requirement."""
        spec = ExperimentSpec.from_mapping(minimal_spec(output_dir="C:/Users/someone/out"))
        with tempfile.TemporaryDirectory() as root:
            self.assertFalse(validate_spec(spec, root=root).ok)

    def test_existing_output_refused(self) -> None:
        """Refuse to overwrite a previous experiment's evidence package."""
        spec = ExperimentSpec.from_mapping(minimal_spec())
        with tempfile.TemporaryDirectory() as root:
            target = os.path.join(root, "results", "DEMO-9001")
            os.makedirs(target)
            with io.open(os.path.join(target, "report.md"), "w", encoding="utf-8") as fh:
                fh.write("previous")
            self.assertFalse(validate_spec(spec, root=root).ok)
            self.assertTrue(validate_spec(spec, root=root, allow_existing_output=True).ok)

    def test_precision_without_randomisation_rejected(self) -> None:
        spec = ExperimentSpec.from_mapping(minimal_spec(
            statistical_precision={"metric": "proportion", "confidence": 0.95, "half_width": 0.01}
        ))
        with tempfile.TemporaryDirectory() as root:
            self.assertFalse(validate_spec(spec, root=root).ok)

    def test_confirmatory_requires_frozen_test(self) -> None:
        spec = ExperimentSpec.from_mapping(minimal_spec(kind="confirmatory"))
        with tempfile.TemporaryDirectory() as root:
            report = validate_spec(spec, root=root)
        self.assertFalse(report.ok)
        self.assertTrue(any("frozen_test" in str(p) for p in report.errors))

    def test_content_hash_ignores_status_and_path(self) -> None:
        a = ExperimentSpec.from_mapping(minimal_spec(status="PLANNED"), source_path="x.yaml")
        b = ExperimentSpec.from_mapping(minimal_spec(status="COMPLETED"), source_path="y.yaml")
        self.assertEqual(a.content_hash, b.content_hash)

    def test_content_hash_detects_scientific_change(self) -> None:
        a = ExperimentSpec.from_mapping(minimal_spec())
        b = ExperimentSpec.from_mapping(minimal_spec(prediction="Something entirely different."))
        self.assertNotEqual(a.content_hash, b.content_hash)


class TestRunLifecycle(unittest.TestCase):
    """The full runner path, in a temporary repository."""

    def _run(self, root: str, spec_data: dict, execution: ExecutionResult):
        if not make_git_root(root):
            self.skipTest("git unavailable; provenance cannot be certified in this environment")
        spec = ExperimentSpec.from_mapping(spec_data)
        os.makedirs(os.path.join(root, "experiments"), exist_ok=True)
        return run(spec, lambda _ctx: execution, root=root, registry=Registry(root))

    def test_valid_run_completes_and_emits_conclusion(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            outcome = self._run(root, minimal_spec(), ExecutionResult(
                statistics={"value": 42},
                envelope_observations={"level": [1.0, 1.0]},
                numerical={"n_nonfinite": 0},
                data={"planned": 10, "actual": 10},
            ))
            self.assertIs(outcome.status, Status.COMPLETED)
            self.assertTrue(outcome.conclusion_emitted)
            for name in ("metadata.json", "provenance.json", "statistics.json",
                         "gates.json", "report.md", "handoff.md", "checksums.txt"):
                self.assertTrue(
                    os.path.exists(os.path.join(root, outcome.package_dir, name)), name
                )

    def test_envelope_violation_invalidates_and_records_failure(self) -> None:
        """The FAIL-0001 lesson, enforced automatically."""
        with tempfile.TemporaryDirectory() as root:
            outcome = self._run(root, minimal_spec(), ExecutionResult(
                statistics={"value": 1.0},
                envelope_observations={"level": [1.0, 31.5]},   # outside [0, 10]
                numerical={"n_nonfinite": 0},
                data={"planned": 10, "actual": 10},
            ))
            self.assertIs(outcome.status, Status.INVALID)
            self.assertFalse(outcome.conclusion_emitted)
            self.assertIsNotNone(outcome.failure_id)
            with io.open(
                os.path.join(root, outcome.package_dir, "report.md"), encoding="utf-8"
            ) as fh:
                report = fh.read()
            self.assertIn("No scientific conclusion is emitted", report)
            self.assertIn("**Nothing.**", report)

    def test_execution_exception_becomes_failed_not_crash(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            if not make_git_root(root):
                self.skipTest("git unavailable")
            spec = ExperimentSpec.from_mapping(minimal_spec())

            def boom(_ctx):
                raise RuntimeError("simulated crash")

            outcome = run(spec, boom, root=root, registry=Registry(root))
            self.assertIs(outcome.status, Status.FAILED)
            self.assertFalse(outcome.conclusion_emitted)

    def test_evidence_package_verifies(self) -> None:
        from aura.hashing import verify_checksums

        with tempfile.TemporaryDirectory() as root:
            outcome = self._run(root, minimal_spec(), ExecutionResult(
                statistics={"value": 1.0},
                envelope_observations={"level": [1.0, 1.0]},
                numerical={"n_nonfinite": 0},
                data={"planned": 5, "actual": 5},
            ))
            pkg = os.path.join(root, outcome.package_dir)
            self.assertEqual(verify_checksums(os.path.join(pkg, "checksums.txt"), root=pkg), [])
            with io.open(os.path.join(pkg, "statistics.json"), "a", encoding="utf-8") as fh:
                fh.write("\ntampered")
            self.assertNotEqual(
                verify_checksums(os.path.join(pkg, "checksums.txt"), root=pkg), []
            )


class TestRegistryLifecycle(unittest.TestCase):
    def test_register_and_transition(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            reg = Registry(root)
            spec = ExperimentSpec.from_mapping(minimal_spec())
            reg.register(spec)
            self.assertIn("DEMO-9001", reg.ids())
            reg.set_status("DEMO-9001", Status.RUNNING, "starting")
            reg.set_status("DEMO-9001", Status.COMPLETED, "gates passed")
            history = reg.history("DEMO-9001")
            self.assertEqual([t.to_status for t in history], ["RUNNING", "COMPLETED"])
            self.assertTrue(all(t.reason for t in history))

    def test_no_silent_overwrite_of_preregistration(self) -> None:
        from aura.errors import RegistryError

        with tempfile.TemporaryDirectory() as root:
            reg = Registry(root)
            reg.register(ExperimentSpec.from_mapping(minimal_spec()))
            with self.assertRaises(RegistryError):
                reg.register(ExperimentSpec.from_mapping(minimal_spec(prediction="changed entirely")))


class TestReportEditorialRules(unittest.TestCase):
    """The report must never convert a number into a conclusion."""

    def _fixture(self, root: str):
        spec = ExperimentSpec.from_mapping(minimal_spec())
        prov = capture(spec, root=root)
        return spec, prov

    def test_researcher_may_not_supply_measured_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            spec, prov = self._fixture(root)
            with self.assertRaises(ValueError):
                generate_report(
                    spec, provenance=prov, status=Status.COMPLETED,
                    gate_summary=summarise([]), statistics={},
                    interpretations=[Statement(EvidenceClass.CALCULATION, "p = 0.5", "x")],
                )

    def test_no_interpretation_means_none_asserted(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            spec, prov = self._fixture(root)
            text = generate_report(
                spec, provenance=prov, status=Status.COMPLETED,
                gate_summary=summarise([]), statistics={"value": 1.0},
            )
            self.assertIn("None supplied. The report therefore asserts no interpretation.", text)
            self.assertIn("no interpretation was supplied", text)

    def test_blocked_report_emits_no_conclusion(self) -> None:
        from aura.gates import GateResult, Outcome

        with tempfile.TemporaryDirectory() as root:
            spec, prov = self._fixture(root)
            blocked = summarise([GateResult("g", "RUNTIME", Outcome.INVALID.value, "bad")])
            text = generate_report(
                spec, provenance=prov, status=Status.INVALID,
                gate_summary=blocked, statistics={"value": 1.0},
                interpretations=[Statement(EvidenceClass.INTERPRETATION, "looks great")],
            )
            self.assertIn("No scientific conclusion is emitted", text)
            self.assertIn("**Nothing.**", text)

    def test_provenance_chain_is_walkable(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            spec, prov = self._fixture(root)
            chain = trace(prov, "value")
            joined = " ".join(chain)
            for link in ("result:", "experiment:", "specification:", "model:", "code:", "seed:"):
                self.assertIn(link, joined)


class TestComparison(unittest.TestCase):
    def test_different_model_version_is_not_comparable(self) -> None:
        """The EXP-0011 lesson: incompatible experiments must not be compared silently."""
        a = ExperimentSpec.from_mapping(minimal_spec())
        b = ExperimentSpec.from_mapping(minimal_spec(
            experiment_id="DEMO-9002",
            model={"identifier": "fixture-model", "version": "2.0",
                   "validity_envelope": {"level": [0.0, 10.0]}},
        ))
        result = compare(a, b)
        self.assertFalse(result.comparable)
        self.assertIn("NOT COMPARABLE", result.render())

    def test_different_controlled_variables_block_comparison(self) -> None:
        a = ExperimentSpec.from_mapping(minimal_spec())
        b = ExperimentSpec.from_mapping(minimal_spec(
            experiment_id="DEMO-9002",
            variables={"independent": {"level": 1.0}, "dependent": ["value"],
                       "controlled": {"mode": "different"}},
        ))
        self.assertFalse(compare(a, b).comparable)

    def test_identical_specs_are_comparable(self) -> None:
        a = ExperimentSpec.from_mapping(minimal_spec())
        b = ExperimentSpec.from_mapping(minimal_spec(experiment_id="DEMO-9002"))
        self.assertTrue(compare(a, b).comparable)


class TestDemonstrations(unittest.TestCase):
    """The two shipped demonstrations must keep behaving as documented."""

    ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def _package(self, experiment_id: str) -> dict:
        path = os.path.join(self.ROOT, "results", experiment_id, "metadata.json")
        if not os.path.exists(path):
            self.skipTest(f"{experiment_id} has not been run in this working copy")
        with io.open(path, encoding="utf-8") as fh:
            return json.load(fh)

    def test_demo_0001_completed_with_conclusion(self) -> None:
        meta = self._package("DEMO-0001")
        self.assertEqual(meta["status"], "COMPLETED")
        self.assertTrue(meta["conclusion_emitted"])

    def test_demo_0001_recovered_closed_form(self) -> None:
        path = os.path.join(self.ROOT, "results", "DEMO-0001", "statistics.json")
        if not os.path.exists(path):
            self.skipTest("DEMO-0001 has not been run")
        with io.open(path, encoding="utf-8") as fh:
            stats = json.load(fh)
        err = stats["absolute_error_vs_closed_form"]
        self.assertLess(err["value"], 0.01)
        self.assertTrue(err["interval_covers_closed_form"])

    def test_demo_0002_invalid_without_conclusion(self) -> None:
        meta = self._package("DEMO-0002")
        self.assertEqual(meta["status"], "INVALID")
        self.assertFalse(meta["conclusion_emitted"])

    def test_shipped_demo_specs_validate(self) -> None:
        for experiment_id in ("DEMO-0001", "DEMO-0002"):
            path = os.path.join(self.ROOT, "experiments", experiment_id, "spec.yaml")
            spec = ExperimentSpec.load(path)
            report = validate_spec(spec, root=self.ROOT, allow_existing_output=True)
            self.assertTrue(report.ok, msg=f"{experiment_id}: {report.errors}")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
