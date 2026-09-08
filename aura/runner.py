"""The experiment runner: the lifecycle, wired together.

::

    specification
        -> preflight validation      (aura.validation)
        -> preflight gates           (aura.gates, PREFLIGHT)
        -> execution                 (the experiment's own module)
        -> runtime gates             (aura.gates, RUNTIME)
        -> post gates                (aura.gates, POST)
        -> statistical gates         (aura.gates, STATISTICAL)
        -> evidence package          (aura.runner.finalise)

An experiment supplies a callable ``execute(context) -> ExecutionResult``. Everything
else — validation, gating, provenance, statistics, packaging, status transitions and
failure recording — is the framework's job, so that an experiment author cannot forget
to do it.
"""

from __future__ import annotations

import io
import json
import os
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Mapping, Optional, Sequence

from . import FRAMEWORK_VERSION
from .errors import GateError
from .evidence import Statement
from .failures import FailureRegistry
from .gates import Outcome, Phase, run_phase, summarise
from .hashing import hash_object, write_checksums
from .provenance import Provenance, capture
from .registry import Registry
from .report import generate as generate_report, write as write_report
from .handoff import generate as generate_handoff, write as write_handoff
from .spec import ExperimentSpec
from .status import Status
from .validation import validate_spec


@dataclass
class ExecutionResult:
    """What an experiment's ``execute`` returns.

    Every field feeds a gate. An experiment that cannot report its envelope
    observations cannot pass the envelope gate — deliberately, since the gate would
    otherwise be certifying something it never saw.
    """

    statistics: Dict[str, Any] = field(default_factory=dict)
    envelope_observations: Dict[str, Sequence[float]] = field(default_factory=dict)
    numerical: Dict[str, Any] = field(default_factory=dict)
    data: Dict[str, Any] = field(default_factory=dict)
    reproducibility: Dict[str, Any] = field(default_factory=lambda: {"checked": False})
    raw_data: Dict[str, Any] = field(default_factory=lambda: {"checked": 0, "modified": []})
    achieved: Dict[str, Any] = field(default_factory=dict)
    convergence: Dict[str, Any] = field(default_factory=dict)
    artefacts: List[str] = field(default_factory=list)
    interpretations: List[Statement] = field(default_factory=list)
    limitations: List[str] = field(default_factory=list)
    deviations: List[str] = field(default_factory=list)


#: An experiment module exposes ``execute(context) -> ExecutionResult``.
ExecuteFn = Callable[[Mapping[str, Any]], ExecutionResult]


@dataclass
class RunOutcome:
    """Everything the runner produced."""

    experiment_id: str
    status: Status
    gate_summary: Dict[str, Any]
    provenance: Provenance
    statistics: Dict[str, Any]
    package_dir: Optional[str]
    failure_id: Optional[str] = None
    validation: Dict[str, Any] = field(default_factory=dict)

    @property
    def conclusion_emitted(self) -> bool:
        """Whether the report contains a scientific conclusion.

        Requires BOTH that no gate blocked interpretation and that the status is itself
        interpretable. Status alone is not implied by the gates: a run that crashed
        during execution is FAILED while its preflight gates all passed, and must not
        be reported as having concluded anything.
        """
        from .status import is_interpretable

        return (
            not self.gate_summary.get("blocks_conclusion", True)
            and is_interpretable(self.status)
        )


def run(
    spec: ExperimentSpec,
    execute: ExecuteFn,
    *,
    root: str = ".",
    registry: Registry | None = None,
    record_failures: bool = True,
    extra_context: Mapping[str, Any] | None = None,
) -> RunOutcome:
    """Execute one experiment through the full lifecycle.

    The function never raises on a *scientific* failure — an invalid or inconclusive
    experiment is a legitimate outcome and is returned. It does raise on *engineering*
    failures (a malformed specification, a gate that cannot be evaluated), because those
    mean the framework cannot certify anything.
    """
    registry = registry or Registry(root)
    failures = FailureRegistry(os.path.join(root, "experiments", "failures"))

    # ---------------------------------------------------------------- 1. validation
    known = [i for i in registry.ids() if i != spec.experiment_id]
    report = validate_spec(spec, root=root, known_experiment_ids=known,
                           allow_existing_output=True)
    report.raise_if_failed()

    # ---------------------------------------------------------------- 2. provenance
    prov = capture(spec, root=root)
    context: Dict[str, Any] = {
        "spec": spec,
        "root": root,
        "provenance": prov,
        **(extra_context or {}),
    }

    # ---------------------------------------------------------------- 3. preflight
    gate_results = run_phase(Phase.PREFLIGHT, spec.gates, context)
    pre = summarise(gate_results)
    if pre["overall"] in (Outcome.FAIL.value, Outcome.INVALID.value):
        # Rejected before any computation — the cheapest possible rejection.
        return _finish(
            spec, prov, Status.INVALID, gate_results, {}, root, registry, failures,
            record_failures, report.to_dict(), started=time.perf_counter(),
            execution=ExecutionResult(),
        )

    # ---------------------------------------------------------------- 4. execution
    started = time.perf_counter()
    status = Status.RUNNING
    try:
        execution = execute(context)
    except Exception as exc:  # noqa: BLE001 - recorded as a FAILED run, never hidden
        prov.finished_utc = __import__("aura.status", fromlist=["utc_now"]).utc_now()
        prov.runtime_seconds = time.perf_counter() - started
        prov.notes.append(f"execution raised {type(exc).__name__}: {exc}")
        return _finish(
            spec, prov, Status.FAILED, gate_results, {}, root, registry, failures,
            record_failures, report.to_dict(), started=started, execution=ExecutionResult(),
            failure_detail=f"execution raised {type(exc).__name__}: {exc}",
        )

    # ---------------------------------------------------------------- 5. later gates
    context.update(
        {
            "envelope_observations": execution.envelope_observations,
            "numerical": execution.numerical,
            "data": execution.data,
            "reproducibility": execution.reproducibility,
            "raw_data": execution.raw_data,
            "achieved": execution.achieved,
            "convergence": execution.convergence,
        }
    )
    for phase in (Phase.RUNTIME, Phase.POST, Phase.STATISTICAL):
        gate_results.extend(run_phase(phase, spec.gates, context))

    summary = summarise(gate_results)
    if summary["overall"] == Outcome.INVALID.value:
        status = Status.INVALID
    elif summary["overall"] == Outcome.FAIL.value:
        status = Status.FAILED
    elif summary["overall"] == Outcome.INCONCLUSIVE.value:
        status = Status.INCONCLUSIVE
    else:
        status = Status.COMPLETED

    return _finish(
        spec, prov, status, gate_results, execution.statistics, root, registry, failures,
        record_failures, report.to_dict(), started=started, execution=execution,
    )


def _finish(
    spec: ExperimentSpec,
    prov: Provenance,
    status: Status,
    gate_results: Sequence[Any],
    statistics: Mapping[str, Any],
    root: str,
    registry: Registry,
    failures: FailureRegistry,
    record_failures: bool,
    validation: Mapping[str, Any],
    *,
    started: float,
    execution: ExecutionResult,
    failure_detail: str | None = None,
) -> RunOutcome:
    """Package results, record status and failures. Always runs, on every path."""
    from .status import utc_now

    if prov.finished_utc is None:
        prov.finished_utc = utc_now()
        prov.runtime_seconds = round(time.perf_counter() - started, 6)

    summary = summarise(gate_results)
    package_dir = finalise(
        spec, prov, status, summary, statistics, root=root,
        execution=execution, validation=validation,
    )

    # Record a failure for any gate that rejected the run, so the rejection becomes a
    # permanent part of the research record without depending on anyone remembering.
    failure_id: Optional[str] = None
    if record_failures:
        rejecting = [r for r in gate_results if r.outcome in (Outcome.FAIL.value, Outcome.INVALID.value)]
        if rejecting:
            rec = failures.from_gate_failure(spec.experiment_id, rejecting[0])
            try:
                failures.record(rec)
                failure_id = rec.failure_id
            except Exception as exc:  # noqa: BLE001
                prov.notes.append(f"failure record could not be written: {exc}")
        elif failure_detail:
            prov.notes.append(failure_detail)

    # Advance the registry status when the experiment is registered.
    try:
        current = Status(registry.load(spec.experiment_id).status)
        if current is Status.PLANNED:
            registry.set_status(spec.experiment_id, Status.RUNNING, "execution started")
        registry.set_status(
            spec.experiment_id, status,
            f"gates returned {summary['overall']}"
            + (f"; recorded as {failure_id}" if failure_id else ""),
        )
    except Exception as exc:  # noqa: BLE001 - a demo may run unregistered
        prov.notes.append(f"registry status not updated: {exc}")

    return RunOutcome(
        experiment_id=spec.experiment_id,
        status=status,
        gate_summary=summary,
        provenance=prov,
        statistics=dict(statistics),
        package_dir=package_dir,
        failure_id=failure_id,
        validation=dict(validation),
    )


def finalise(
    spec: ExperimentSpec,
    prov: Provenance,
    status: Status,
    gate_summary: Mapping[str, Any],
    statistics: Mapping[str, Any],
    *,
    root: str = ".",
    execution: ExecutionResult | None = None,
    validation: Mapping[str, Any] | None = None,
) -> str:
    """Write the evidence package. Returns the package directory.

    Contents are deliberately few — one file per question a reader will actually ask::

        metadata.json     what ran, when, under what status
        provenance.json   the full result -> seed chain
        statistics.json   every measured quantity with its interval
        gates.json        every gate, its outcome and its evidence
        validation.json   the preflight specification check
        report.md         the human-readable research report
        handoff.md        the self-contained independent-review document
        checksums.txt     sha256 of every file above
    """
    execution = execution or ExecutionResult()
    out_dir = os.path.join(root, spec.output_dir or os.path.join("results", spec.experiment_id))
    os.makedirs(out_dir, exist_ok=True)

    def dump(name: str, payload: Any) -> str:
        path = os.path.join(out_dir, name)
        with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(payload, fh, indent=2, sort_keys=True, ensure_ascii=False)
            fh.write("\n")
        return path

    written: List[str] = []
    written.append(
        dump(
            "metadata.json",
            {
                "experiment_id": spec.experiment_id,
                "title": spec.title,
                "kind": spec.kind,
                "status": status.value,
                "framework_version": FRAMEWORK_VERSION,
                "spec_hash": spec.content_hash,
                "run_id": prov.run_id,
                "started_utc": prov.started_utc,
                "finished_utc": prov.finished_utc,
                "runtime_seconds": prov.runtime_seconds,
                # Same rule as RunOutcome.conclusion_emitted: gates AND status.
                "conclusion_emitted": (
                    not gate_summary.get("blocks_conclusion", True)
                    and __import__("aura.status", fromlist=["is_interpretable"]).is_interpretable(status)
                ),
                "gates_overall": gate_summary.get("overall"),
                "deviations": list(execution.deviations),
            },
        )
    )
    written.append(dump("provenance.json", prov.to_dict()))
    written.append(dump("statistics.json", dict(statistics)))
    written.append(dump("gates.json", dict(gate_summary)))
    written.append(dump("validation.json", dict(validation or {})))

    written.append(
        write_report(
            os.path.join(out_dir, "report.md"),
            generate_report(
                spec, provenance=prov, status=status, gate_summary=gate_summary,
                statistics=statistics, interpretations=execution.interpretations,
                deviations=execution.deviations, limitations=execution.limitations,
            ),
        )
    )
    written.append(
        write_handoff(
            os.path.join(out_dir, "handoff.md"),
            generate_handoff(
                spec, provenance=prov, status=status, gate_summary=gate_summary,
                statistics=statistics, interpretations=execution.interpretations,
                limitations=execution.limitations,
            ),
        )
    )

    checks = {
        os.path.relpath(p, out_dir).replace(os.sep, "/"): __import__(
            "aura.hashing", fromlist=["hash_file"]
        ).hash_file(p)
        for p in written
    }
    write_checksums(checks, os.path.join(out_dir, "checksums.txt"))
    return os.path.relpath(out_dir, root).replace(os.sep, "/")
