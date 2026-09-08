"""Unit tests for AURA's core components.

Run with the standard library only::

    python -m unittest discover -s tests -v

``pytest`` is deliberately not required: the framework must be runnable by anyone with
Python and numpy.
"""

from __future__ import annotations

import math
import os
import tempfile
import unittest

import numpy as np

from aura import hashing, integrity, seeds, statistics
from aura.errors import (
    GateError,
    RegistryError,
    StatisticalError,
    StatusTransitionError,
)
from aura.evidence import EvidenceClass, Statement, check_statements, partition
from aura.failures import FailureRecord, FailureRegistry, FailureStatus
from aura.gates import GATE_REGISTRY, Outcome, Phase, summarise
from aura.montecarlo import run as mc_run
from aura.retention import Artefact, DataTier, RetentionClass, plan_cleanup
from aura.status import Status, transition


class TestSeeds(unittest.TestCase):
    """Deterministic seed derivation."""

    def test_deterministic(self) -> None:
        self.assertEqual(seeds.derive_seed(7, "a", 1.0), seeds.derive_seed(7, "a", 1.0))

    def test_order_independence_of_other_cells(self) -> None:
        """Adding a cell must not change any existing cell's seed."""
        base = 20260908
        first = seeds.derive_seed(base, "FC-1", 2.0)
        _other = seeds.derive_seed(base, "FC-9", 5.0)
        self.assertEqual(first, seeds.derive_seed(base, "FC-1", 2.0))

    def test_type_distinctness(self) -> None:
        """1, 1.0 and '1' must not collide: they are different experimental cells."""
        a = seeds.derive_seed(1, 1)
        b = seeds.derive_seed(1, 1.0)
        c = seeds.derive_seed(1, "1")
        self.assertEqual(len({a, b, c}), 3)

    def test_label_boundary(self) -> None:
        """('a','bc') and ('ab','c') must not collide."""
        self.assertNotEqual(seeds.derive_seed(1, "a", "bc"), seeds.derive_seed(1, "ab", "c"))

    def test_rejects_bad_base(self) -> None:
        with self.assertRaises(TypeError):
            seeds.derive_seed("nope")  # type: ignore[arg-type]
        with self.assertRaises(ValueError):
            seeds.derive_seed(-1)

    def test_seed_in_numpy_range(self) -> None:
        for i in range(200):
            self.assertLess(seeds.derive_seed(12345, i), 1 << 63)


class TestStatistics(unittest.TestCase):
    """Estimators checked against published reference values."""

    def test_probit_reference_values(self) -> None:
        self.assertAlmostEqual(statistics.normal_quantile(0.975), 1.959963984540054, places=10)
        self.assertAlmostEqual(statistics.normal_quantile(0.995), 2.5758293035489004, places=10)
        self.assertAlmostEqual(statistics.normal_quantile(0.5), 0.0, places=12)

    def test_probit_cdf_roundtrip(self) -> None:
        for p in (0.001, 0.01, 0.25, 0.5, 0.75, 0.99, 0.999):
            self.assertAlmostEqual(statistics.normal_cdf(statistics.normal_quantile(p)), p, places=12)

    def test_chi2_reference(self) -> None:
        # Wilson-Hilferty: documented as better than ~0.5% for dof >= 10.
        self.assertLess(abs(statistics.chi2_quantile(0.95, 20) - 31.4104) / 31.4104, 0.005)
        self.assertLess(abs(statistics.chi2_quantile(0.99, 50) - 76.1539) / 76.1539, 0.005)

    def test_chi2_refuses_small_dof(self) -> None:
        """It must refuse rather than return a silently inaccurate critical value."""
        with self.assertRaises(StatisticalError):
            statistics.chi2_quantile(0.95, 5)

    def test_wilson_stays_in_unit_interval(self) -> None:
        for k, n in ((0, 100), (100, 100), (1, 10000)):
            iv = statistics.proportion_ci(k, n)
            self.assertGreaterEqual(iv.low, 0.0)
            self.assertLessEqual(iv.high, 1.0)

    def test_wilson_coverage(self) -> None:
        """Empirical coverage of the Wilson interval should be near nominal."""
        rng = np.random.default_rng(seeds.derive_seed(99, "coverage"))
        p, n, trials = 0.3, 200, 400
        covered = 0
        for _ in range(trials):
            k = int(rng.binomial(n, p))
            iv = statistics.proportion_ci(k, n, 0.95)
            covered += iv.low <= p <= iv.high
        self.assertGreater(covered / trials, 0.90)

    def test_required_n_reference(self) -> None:
        self.assertEqual(statistics.required_n_proportion(0.01), 9604)
        self.assertEqual(statistics.required_n_mean(0.1, 1.0), 385)

    def test_required_n_rejects_bad_input(self) -> None:
        with self.assertRaises(StatisticalError):
            statistics.required_n_proportion(0.0)
        with self.assertRaises(StatisticalError):
            statistics.required_n_mean(0.1, -1.0)

    def test_mean_ci_rejects_nonfinite(self) -> None:
        with self.assertRaises(StatisticalError):
            statistics.mean_ci([1.0, float("nan"), 3.0])


class TestHashing(unittest.TestCase):
    def test_canonical_order_independent(self) -> None:
        self.assertEqual(hashing.hash_object({"a": 1, "b": 2}), hashing.hash_object({"b": 2, "a": 1}))

    def test_type_sensitive(self) -> None:
        self.assertNotEqual(hashing.hash_object({"a": 1}), hashing.hash_object({"a": 1.0}))

    def test_rejects_nan(self) -> None:
        with self.assertRaises(ValueError):
            hashing.hash_object({"a": float("nan")})

    def test_line_ending_normalisation(self) -> None:
        """A config must hash identically checked out on Windows and Linux."""
        with tempfile.TemporaryDirectory() as d:
            crlf, lf = os.path.join(d, "a.yaml"), os.path.join(d, "b.yaml")
            with open(crlf, "wb") as fh:
                fh.write(b"key: 1\r\nother: 2\r\n")
            with open(lf, "wb") as fh:
                fh.write(b"key: 1\nother: 2\n")
            self.assertEqual(
                hashing.hash_file(crlf, normalise_text=True),
                hashing.hash_file(lf, normalise_text=True),
            )
            self.assertNotEqual(hashing.hash_file(crlf), hashing.hash_file(lf))

    def test_checksum_detects_modification(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            target = os.path.join(d, "data.txt")
            with open(target, "w", encoding="utf-8") as fh:
                fh.write("original")
            manifest = os.path.join(d, "checksums.txt")
            hashing.write_checksums({"data.txt": hashing.hash_file(target)}, manifest)
            self.assertEqual(hashing.verify_checksums(manifest, root=d), [])
            with open(target, "w", encoding="utf-8") as fh:
                fh.write("tampered")
            self.assertEqual(hashing.verify_checksums(manifest, root=d), ["changed: data.txt"])


class TestStatus(unittest.TestCase):
    def test_legal_transition_records_reason(self) -> None:
        new, hist = transition(Status.PLANNED, Status.RUNNING, "starting")
        self.assertIs(new, Status.RUNNING)
        self.assertEqual(hist[-1].reason, "starting")

    def test_illegal_transition_rejected(self) -> None:
        with self.assertRaises(StatusTransitionError):
            transition(Status.COMPLETED, Status.RUNNING, "rewind")

    def test_archived_is_terminal(self) -> None:
        for target in Status:
            with self.assertRaises(StatusTransitionError):
                transition(Status.ARCHIVED, target, "any")

    def test_reason_is_mandatory(self) -> None:
        with self.assertRaises(ValueError):
            transition(Status.PLANNED, Status.RUNNING, "   ")

    def test_completed_can_be_invalidated_later(self) -> None:
        """A defect found after the fact must be able to invalidate a completed run."""
        new, _ = transition(Status.COMPLETED, Status.INVALID, "defect discovered")
        self.assertIs(new, Status.INVALID)

    def test_invalid_is_not_interpretable(self) -> None:
        from aura.status import is_interpretable

        self.assertFalse(is_interpretable(Status.INVALID))
        self.assertFalse(is_interpretable(Status.FAILED))
        self.assertTrue(is_interpretable(Status.COMPLETED))


class TestMonteCarlo(unittest.TestCase):
    def test_determinism(self) -> None:
        def t(rng, _labels):
            return float(rng.normal())

        a = mc_run(t, n=200, base_seed=5, labels={"c": 1})
        b = mc_run(t, n=200, base_seed=5, labels={"c": 1})
        self.assertTrue(np.array_equal(a.samples, b.samples))

    def test_failed_trials_recorded_not_dropped(self) -> None:
        def t(rng, labels):
            if labels["trial"] % 10 == 0:
                raise RuntimeError("synthetic failure")
            return float(rng.normal())

        r = mc_run(t, n=100, base_seed=5)
        self.assertEqual(r.n_failed, 10)
        self.assertEqual(r.n_completed, 90)
        self.assertEqual(r.n_requested, 100)

    def test_all_failed_raises(self) -> None:
        """Zero samples is not a weak estimate; it is not an estimate."""
        def t(_rng, _labels):
            raise RuntimeError("always")

        with self.assertRaises(StatisticalError):
            mc_run(t, n=10, base_seed=5)

    def test_nonfinite_counts_as_failure(self) -> None:
        def t(_rng, _labels):
            return float("inf")

        with self.assertRaises(StatisticalError):
            mc_run(t, n=5, base_seed=5)

    def test_proportion_estimator_rejects_non_binary(self) -> None:
        def t(_rng, _labels):
            return 0.5

        with self.assertRaises(StatisticalError):
            mc_run(t, n=10, base_seed=5, estimator="proportion")

    def test_recovers_known_proportion(self) -> None:
        """End-to-end: the engine must recover a known Bernoulli parameter."""
        def t(rng, _labels):
            return 1.0 if rng.random() < 0.25 else 0.0

        r = mc_run(t, n=20000, base_seed=11, estimator="proportion")
        self.assertLess(abs(r.interval.point - 0.25), 0.02)
        self.assertLessEqual(r.interval.low, 0.25)
        self.assertGreaterEqual(r.interval.high, 0.25)


class TestGates(unittest.TestCase):
    def test_gate_without_context_raises_never_passes(self) -> None:
        """The critical property: a gate that cannot be evaluated must not return PASS."""
        gate = GATE_REGISTRY["model_validity_envelope"]
        with self.assertRaises(GateError):
            gate.run({})

    def test_envelope_violation_is_invalid(self) -> None:
        class _Spec:
            class model:  # noqa: N801
                validity_envelope = {"alpha_deg": [-5.0, 12.0]}

        gate = GATE_REGISTRY["model_validity_envelope"]
        r = gate.run({"spec": _Spec, "envelope_observations": {"alpha_deg": [-2.0, 31.5]}})
        self.assertEqual(r.outcome, Outcome.INVALID.value)

    def test_envelope_missing_observation_raises(self) -> None:
        """An unobserved envelope variable cannot be certified as in-envelope."""
        class _Spec:
            class model:  # noqa: N801
                validity_envelope = {"alpha_deg": [-5.0, 12.0]}

        gate = GATE_REGISTRY["model_validity_envelope"]
        with self.assertRaises(GateError):
            gate.run({"spec": _Spec, "envelope_observations": {}})

    def test_numerical_dt_divisibility(self) -> None:
        gate = GATE_REGISTRY["numerical_validity"]
        bad = gate.run({"numerical": {"dt": 0.004, "sample_dt": 0.01}})
        self.assertEqual(bad.outcome, Outcome.INVALID.value)
        good = gate.run({"numerical": {"dt": 0.005, "sample_dt": 0.01}})
        self.assertEqual(good.outcome, Outcome.PASS.value)

    def test_data_completeness_detects_count_mismatch(self) -> None:
        gate = GATE_REGISTRY["data_completeness"]
        r = gate.run({"data": {"planned": 72, "actual": 90}})
        self.assertEqual(r.outcome, Outcome.INVALID.value)

    def test_summarise_precedence(self) -> None:
        from aura.gates import GateResult

        results = [
            GateResult("a", "POST", Outcome.PASS.value, ""),
            GateResult("b", "POST", Outcome.INCONCLUSIVE.value, ""),
            GateResult("c", "POST", Outcome.INVALID.value, ""),
        ]
        s = summarise(results)
        self.assertEqual(s["overall"], Outcome.INVALID.value)
        self.assertTrue(s["blocks_conclusion"])

    def test_all_registered_gates_have_a_phase(self) -> None:
        for name, gate in GATE_REGISTRY.items():
            self.assertIsInstance(gate.phase, Phase, msg=name)


class TestEvidence(unittest.TestCase):
    def test_calculation_requires_provenance(self) -> None:
        problems = check_statements([Statement(EvidenceClass.CALCULATION, "x = 1")])
        self.assertTrue(any("provenance" in p for p in problems))

    def test_pure_interpretation_flagged(self) -> None:
        problems = check_statements([Statement(EvidenceClass.INTERPRETATION, "it works")])
        self.assertTrue(any("no measured evidence" in p for p in problems))

    def test_partition_separates_measured_from_inferred(self) -> None:
        measured, inferred = partition([
            Statement(EvidenceClass.CALCULATION, "a", "stats.json"),
            Statement(EvidenceClass.INTERPRETATION, "b"),
            Statement(EvidenceClass.LIMITATION, "c"),
        ])
        self.assertEqual(len(measured), 1)
        self.assertEqual(len(inferred), 2)


class TestFailureRegistry(unittest.TestCase):
    def _record(self, fid: str = "FAIL-0001", **kw) -> FailureRecord:
        base = dict(
            failure_id=fid, experiment_id="EXP-0001", title="t",
            discovered_utc="2026-01-01T00:00:00+00:00",
            detection_mechanism="m", description="d",
            scientific_impact="s", computational_impact="c",
            root_cause="r", correction="fix", verification="verified",
        )
        base.update(kw)
        return FailureRecord(**base)  # type: ignore[arg-type]

    def test_resolved_requires_verification(self) -> None:
        rec = self._record(status=FailureStatus.RESOLVED.value, verification="")
        with self.assertRaises(RegistryError):
            rec.validate()

    def test_bad_id_rejected(self) -> None:
        with self.assertRaises(RegistryError):
            self._record("FAILURE-1").validate()

    def test_no_silent_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            reg = FailureRegistry(d)
            reg.record(self._record("FAIL-0001"))
            with self.assertRaises(RegistryError):
                reg.record(self._record("FAIL-0001"))

    def test_id_allocation_respects_other_formats(self) -> None:
        """Regression: ids must not be re-issued over hand-written Markdown records.

        Found during framework bring-up — the auto-allocator issued FAIL-0001 while a
        historical FAIL-0001.md already documented a different failure.
        """
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "FAIL-0001.md"), "w", encoding="utf-8") as fh:
                fh.write("# FAIL-0001 - a historical, hand-written record\n")
            reg = FailureRegistry(d)
            self.assertEqual(reg.next_id(), "FAIL-0002")
            with self.assertRaises(RegistryError):
                reg.record(self._record("FAIL-0001"))


class TestRetention(unittest.TestCase):
    def _artefact(self, path: str, tier: DataTier, retention: RetentionClass) -> Artefact:
        return Artefact(path, tier.value, retention.value, 100, "0" * 64)

    def test_nothing_deletable_before_finalisation(self) -> None:
        arts = [self._artefact("a.npz", DataTier.RAW, RetentionClass.REGENERABLE)]
        plan = plan_cleanup(arts, finalised=False)
        self.assertEqual(plan["eligible"], [])

    def test_permanent_never_deletable(self) -> None:
        arts = [
            self._artefact("report.md", DataTier.RESULTS, RetentionClass.RETAIN_PERMANENT),
            self._artefact("big.npz", DataTier.RAW, RetentionClass.REGENERABLE),
        ]
        plan = plan_cleanup(arts, finalised=True)
        self.assertEqual(plan["eligible"], ["big.npz"])
        self.assertIn("report.md", plan["retained"])


class TestIntegrity(unittest.TestCase):
    """Assertions distilled from real research failures."""

    def test_duplicate_templates_detected(self) -> None:
        """EXP-0011: a silent patch produced nine duplicate nominal templates."""
        with self.assertRaises(integrity.IntegrityError):
            integrity.assert_distinct(["F0"] * 9 + ["F1"], "hypothesis templates")

    def test_no_op_patch_detected(self) -> None:
        """A substitution that matched nothing must not report success."""
        text = "threshold = 1.0"
        with self.assertRaises(integrity.IntegrityError):
            integrity.assert_patch_applied(text, text.replace("MISSING", "x"), "threshold patch")

    def test_reported_n_mismatch_detected(self) -> None:
        """EXP-0002: a label claimed 72 runs while 90 were checked."""
        with self.assertRaises(integrity.IntegrityError):
            integrity.assert_reported_n(72, 90, "determinism check")

    def test_dt_divisibility(self) -> None:
        with self.assertRaises(integrity.IntegrityError):
            integrity.assert_divides(0.004, 0.01, "integration step")
        integrity.assert_divides(0.005, 0.01, "integration step")

    def test_asymmetric_admissible_sets_detected(self) -> None:
        """EXP-0011: one case could select a hypothesis the compared case could not."""
        with self.assertRaises(integrity.IntegrityError):
            integrity.assert_symmetric_sets(["F0", "F1", "F2"], ["F1", "F2"], "admissible set")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
