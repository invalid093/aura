"""Validity gates.

A gate is a named, automatic check that runs at a defined point in the experiment
lifecycle and returns an outcome. Gates are the framework's defining feature: they
convert "the researcher should remember to check X" into "the run cannot be reported as
valid unless X was checked".

Lifecycle::

    specification -> PREFLIGHT -> execution -> RUNTIME -> POST -> STATISTICAL -> package

Design rules
------------
* A gate that *cannot be evaluated* raises :class:`~aura.errors.GateError`. It must
  never return PASS. A false PASS is the one outcome that would make the whole
  framework untrustworthy, so the absence of evidence is never treated as evidence.
* Gate outcomes are data, not exceptions: a FAIL is a legitimate, recorded result.
* Gates are pure functions of a context dictionary, so they are testable in isolation
  and cannot reach into global state.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict, field
from enum import Enum
from typing import Any, Callable, Dict, List, Mapping, Sequence

from .errors import GateError
from .hashing import verify_checksums
from .status import utc_now


class Phase(str, Enum):
    """When a gate runs."""

    PREFLIGHT = "PREFLIGHT"
    RUNTIME = "RUNTIME"
    POST = "POST"
    STATISTICAL = "STATISTICAL"


class Outcome(str, Enum):
    """Result of a gate."""

    PASS = "PASS"
    FAIL = "FAIL"
    INVALID = "INVALID"
    INCONCLUSIVE = "INCONCLUSIVE"
    SUPERSEDED = "SUPERSEDED"

    @property
    def blocks_conclusion(self) -> bool:
        """Whether this outcome forbids emitting a scientific conclusion."""
        return self in (Outcome.FAIL, Outcome.INVALID)


@dataclass(frozen=True)
class GateResult:
    """The outcome of one gate evaluation."""

    name: str
    phase: str
    outcome: str
    detail: str
    evidence: Dict[str, Any] = field(default_factory=dict)
    checked_utc: str = field(default_factory=utc_now)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @property
    def passed(self) -> bool:
        return self.outcome == Outcome.PASS.value


#: A gate is ``(context) -> GateResult``.
GateFn = Callable[[Mapping[str, Any]], GateResult]

GATE_REGISTRY: Dict[str, "Gate"] = {}


@dataclass(frozen=True)
class Gate:
    """A registered gate."""

    name: str
    phase: Phase
    description: str
    fn: GateFn
    required_context: tuple[str, ...] = ()

    def run(self, context: Mapping[str, Any]) -> GateResult:
        """Evaluate the gate, raising :class:`GateError` if it cannot be evaluated."""
        missing = [k for k in self.required_context if k not in context]
        if missing:
            raise GateError(
                f"gate {self.name!r} cannot be evaluated: missing context {missing}. "
                "A gate that cannot run must never report PASS."
            )
        result = self.fn(context)
        if not isinstance(result, GateResult):  # pragma: no cover - programming error
            raise GateError(f"gate {self.name!r} returned {type(result).__name__}, not GateResult")
        return result


def register(name: str, phase: Phase, description: str, required_context: Sequence[str] = ()) -> Callable[[GateFn], GateFn]:
    """Decorator registering a gate under ``name``."""

    def deco(fn: GateFn) -> GateFn:
        if name in GATE_REGISTRY:
            raise GateError(f"gate {name!r} is already registered")
        GATE_REGISTRY[name] = Gate(name, phase, description, fn, tuple(required_context))
        return fn

    return deco


def _result(name: str, phase: Phase, outcome: Outcome, detail: str, **evidence: Any) -> GateResult:
    return GateResult(name, phase.value, outcome.value, detail, dict(evidence))


# ------------------------------------------------------------------ preflight gates
@register(
    "provenance_complete",
    Phase.PREFLIGHT,
    "Every link in the result->seed provenance chain is recorded.",
    required_context=("provenance",),
)
def _provenance_complete(ctx: Mapping[str, Any]) -> GateResult:
    prov = ctx["provenance"]
    missing = prov.missing_links()
    if missing:
        return _result(
            "provenance_complete", Phase.PREFLIGHT, Outcome.FAIL,
            f"provenance chain incomplete: {', '.join(missing)}",
            missing=missing,
        )
    if not prov.code_version_certifiable:
        # Cannot certify which code produced this run. Not a FAIL: the run may still be
        # legitimate, and blocking it would make the framework unusable outside a git
        # checkout. Not a PASS either -- the chain genuinely has a hole.
        return _result(
            "provenance_complete", Phase.PREFLIGHT, Outcome.INCONCLUSIVE,
            "no code version available (not a git working copy); the run cannot be "
            "traced to a specific commit",
            git_commit=None,
        )
    detail = "provenance chain complete"
    if prov.code.git_dirty:
        # Recorded, not fatal: a dirty tree cannot be reproduced from the commit alone,
        # but blocking it would make development impossible. The reader is told.
        return _result(
            "provenance_complete", Phase.PREFLIGHT, Outcome.PASS,
            detail + " (WARNING: working tree dirty; commit alone does not reproduce this run)",
            git_dirty=True,
        )
    return _result("provenance_complete", Phase.PREFLIGHT, Outcome.PASS, detail, git_dirty=False)


@register(
    "frozen_test_integrity",
    Phase.PREFLIGHT,
    "The declared frozen test set is byte-identical to its recorded checksums.",
    required_context=("spec", "root"),
)
def _frozen_test_integrity(ctx: Mapping[str, Any]) -> GateResult:
    spec, root = ctx["spec"], ctx["root"]
    ft = spec.frozen_test
    if not ft.enabled:
        # An explicit "not applicable" is a legitimate outcome, but it is recorded so
        # that a reader can see the question was asked.
        return _result(
            "frozen_test_integrity", Phase.PREFLIGHT, Outcome.PASS,
            "no frozen test declared for this experiment", applicable=False,
        )
    if not ft.checksum_file:
        raise GateError("frozen test enabled but no checksum_file recorded — cannot verify")
    import os

    path = os.path.join(root, ft.checksum_file)
    if not os.path.exists(path):
        raise GateError(f"frozen test checksum file missing: {ft.checksum_file}")
    problems = verify_checksums(path, root=root)
    if problems:
        return _result(
            "frozen_test_integrity", Phase.PREFLIGHT, Outcome.INVALID,
            f"frozen test set has been modified: {problems}", problems=problems,
        )
    return _result(
        "frozen_test_integrity", Phase.PREFLIGHT, Outcome.PASS,
        "frozen test set verified against recorded checksums", applicable=True,
    )


@register(
    "seed_policy_declared",
    Phase.PREFLIGHT,
    "Stochastic experiments derive seeds deterministically and use no global RNG.",
    required_context=("spec",),
)
def _seed_policy(ctx: Mapping[str, Any]) -> GateResult:
    r = ctx["spec"].randomisation
    if not r.enabled:
        return _result("seed_policy_declared", Phase.PREFLIGHT, Outcome.PASS,
                       "deterministic experiment; no seeds required", applicable=False)
    if r.base_seed is None or not r.label_fields:
        return _result("seed_policy_declared", Phase.PREFLIGHT, Outcome.FAIL,
                       "randomisation enabled without a complete seed policy")
    return _result("seed_policy_declared", Phase.PREFLIGHT, Outcome.PASS,
                   f"seeds derived from base {r.base_seed} over {r.label_fields}",
                   base_seed=r.base_seed, label_fields=list(r.label_fields))


# -------------------------------------------------------------------- runtime gates
@register(
    "model_validity_envelope",
    Phase.RUNTIME,
    "Every trial stayed inside the model's declared validity envelope.",
    required_context=("spec", "envelope_observations"),
)
def _model_validity(ctx: Mapping[str, Any]) -> GateResult:
    """The direct descendant of FAIL-0001.

    ``envelope_observations`` maps envelope key -> observed [min, max] across the run.
    Any excursion makes the run INVALID: its numbers describe a regime the model was
    never claimed to represent.
    """
    envelope = ctx["spec"].model.validity_envelope
    observed = ctx["envelope_observations"]
    if not envelope:
        raise GateError(
            "model_validity_envelope requested but the specification declares no envelope"
        )

    violations = []
    for key, (lo, hi) in envelope.items():
        if key not in observed:
            raise GateError(
                f"no observation recorded for envelope variable {key!r}; "
                "cannot certify the run stayed in envelope"
            )
        obs_lo, obs_hi = observed[key]
        if obs_lo < lo or obs_hi > hi:
            violations.append(
                {"variable": key, "allowed": [lo, hi], "observed": [obs_lo, obs_hi]}
            )
    if violations:
        return _result(
            "model_validity_envelope", Phase.RUNTIME, Outcome.INVALID,
            f"{len(violations)} envelope violation(s); results must not be interpreted",
            violations=violations,
        )
    return _result(
        "model_validity_envelope", Phase.RUNTIME, Outcome.PASS,
        f"all {len(envelope)} envelope variable(s) within declared bounds",
        observed=dict(observed),
    )


@register(
    "numerical_validity",
    Phase.RUNTIME,
    "No non-finite values were produced and integration settings are self-consistent.",
    required_context=("numerical",),
)
def _numerical_validity(ctx: Mapping[str, Any]) -> GateResult:
    """Includes the ``dt`` divisibility check that caught a real defect in EXP-0010.

    ``numerical`` may carry ``n_nonfinite``, ``dt`` and ``sample_dt``.
    """
    n = ctx["numerical"]
    problems: List[str] = []

    n_nonfinite = int(n.get("n_nonfinite", 0))
    if n_nonfinite:
        problems.append(f"{n_nonfinite} non-finite value(s) produced")

    dt, sample_dt = n.get("dt"), n.get("sample_dt")
    if dt is not None and sample_dt is not None:
        ratio = sample_dt / dt
        if abs(ratio - round(ratio)) > 1e-9:
            problems.append(
                f"integration step dt={dt} does not divide sample interval {sample_dt} "
                f"(ratio {ratio:.6f}); sampling would drift"
            )
    if problems:
        return _result("numerical_validity", Phase.RUNTIME, Outcome.INVALID,
                       "; ".join(problems), problems=problems)
    return _result("numerical_validity", Phase.RUNTIME, Outcome.PASS,
                   "no non-finite values; timing self-consistent", **{k: v for k, v in n.items()})


# ------------------------------------------------------------------------ post gates
@register(
    "data_completeness",
    Phase.POST,
    "Every planned trial produced a recorded outcome.",
    required_context=("data",),
)
def _data_completeness(ctx: Mapping[str, Any]) -> GateResult:
    """Catches the EXP-0002 defect where a label claimed 72 runs while 90 were checked."""
    d = ctx["data"]
    planned, actual = int(d["planned"]), int(d["actual"])
    failed = int(d.get("failed_trials", 0))
    if actual != planned:
        return _result(
            "data_completeness", Phase.POST, Outcome.INVALID,
            f"planned {planned} trials but recorded {actual}; the reported N is not the run N",
            planned=planned, actual=actual, failed_trials=failed,
        )
    if failed:
        return _result(
            "data_completeness", Phase.POST, Outcome.INCONCLUSIVE,
            f"{failed} of {planned} trials failed; the sample is not the intended one",
            planned=planned, actual=actual, failed_trials=failed,
        )
    return _result("data_completeness", Phase.POST, Outcome.PASS,
                   f"all {planned} trials recorded", planned=planned, actual=actual)


@register(
    "reproducibility",
    Phase.POST,
    "A repeat execution satisfied the declared reproducibility criterion.",
    required_context=("reproducibility",),
)
def _reproducibility(ctx: Mapping[str, Any]) -> GateResult:
    """``reproducibility`` carries ``mode`` (bitwise|tolerance), ``max_abs_diff``, ``tolerance``."""
    r = ctx["reproducibility"]
    if not r.get("checked", False):
        return _result("reproducibility", Phase.POST, Outcome.INCONCLUSIVE,
                       "no repeat execution was performed", checked=False)
    mode = r.get("mode", "bitwise")
    if mode == "bitwise":
        identical = bool(r["identical"])
        return _result(
            "reproducibility", Phase.POST,
            Outcome.PASS if identical else Outcome.FAIL,
            "repeat execution was bit-identical" if identical
            else "repeat execution differed; a deterministic experiment must be bit-identical",
            mode=mode, identical=identical,
        )
    diff, tol = float(r["max_abs_diff"]), float(r["tolerance"])
    ok = diff <= tol
    return _result(
        "reproducibility", Phase.POST, Outcome.PASS if ok else Outcome.FAIL,
        f"max |difference| {diff:.3e} vs declared tolerance {tol:.3e}",
        mode=mode, max_abs_diff=diff, tolerance=tol,
    )


@register(
    "raw_data_immutable",
    Phase.POST,
    "No pre-existing raw data file was modified by this run.",
    required_context=("raw_data",),
)
def _raw_data_immutable(ctx: Mapping[str, Any]) -> GateResult:
    r = ctx["raw_data"]
    modified = list(r.get("modified", []))
    if modified:
        return _result("raw_data_immutable", Phase.POST, Outcome.INVALID,
                       f"raw data was overwritten: {modified}", modified=modified)
    return _result("raw_data_immutable", Phase.POST, Outcome.PASS,
                   f"{int(r.get('checked', 0))} raw artefact(s) unchanged")


# ----------------------------------------------------------------- statistical gates
@register(
    "statistical_precision",
    Phase.STATISTICAL,
    "The experiment achieved its pre-declared precision target.",
    required_context=("spec", "achieved"),
)
def _statistical_precision(ctx: Mapping[str, Any]) -> GateResult:
    """Compares achieved half-width against the pre-registered target.

    A miss is ``INCONCLUSIVE``, not ``FAIL``: the experiment was validly run, it simply
    did not answer its question precisely enough. Conflating the two would let an
    under-powered run be reported as a negative result.
    """
    spec, achieved = ctx["spec"], ctx["achieved"]
    sp = spec.statistical_precision
    if sp is None:
        raise GateError(
            "statistical_precision gate declared but no precision target is specified"
        )
    hw = float(achieved["half_width"])
    required_n = achieved.get("required_n")
    actual_n = achieved.get("actual_n")
    ok = hw <= sp.half_width
    return _result(
        "statistical_precision", Phase.STATISTICAL,
        Outcome.PASS if ok else Outcome.INCONCLUSIVE,
        f"achieved half-width {hw:.5g} vs target {sp.half_width:.5g} "
        f"at {sp.confidence:.0%} confidence (required N {required_n}, actual N {actual_n})",
        target_half_width=sp.half_width, achieved_half_width=hw,
        confidence=sp.confidence, required_n=required_n, actual_n=actual_n,
        note="Precision only; says nothing about whether the modelled system is correct.",
    )


@register(
    "convergence",
    Phase.STATISTICAL,
    "The Monte Carlo estimate was still converging no faster than a declared bound.",
    required_context=("convergence",),
)
def _convergence(ctx: Mapping[str, Any]) -> GateResult:
    c = ctx["convergence"]
    trace = c.get("trace") or []
    if len(trace) < 2:
        raise GateError("convergence gate requires a trace with at least two checkpoints")
    last, prev = trace[-1], trace[-2]
    # If the half-width is still shrinking sharply at the final checkpoint, the run
    # stopped while the estimate was still moving.
    shrink = (prev["half_width"] - last["half_width"]) / max(prev["half_width"], 1e-300)
    limit = float(c.get("max_final_shrink", 0.25))
    if shrink > limit:
        return _result("convergence", Phase.STATISTICAL, Outcome.INCONCLUSIVE,
                       f"half-width still fell {shrink:.1%} over the final checkpoint "
                       f"(limit {limit:.0%}); the estimate had not settled",
                       final_shrink=shrink, limit=limit)
    return _result("convergence", Phase.STATISTICAL, Outcome.PASS,
                   f"half-width changed {shrink:.1%} over the final checkpoint",
                   final_shrink=shrink, limit=limit)


# ---------------------------------------------------------------------- orchestration
def run_phase(phase: Phase, gate_names: Sequence[str], context: Mapping[str, Any]) -> List[GateResult]:
    """Run every declared gate belonging to ``phase``.

    Unknown gate names raise rather than being skipped: silently ignoring a gate the
    specification asked for would produce an unearned PASS.
    """
    results: List[GateResult] = []
    for name in gate_names:
        gate = GATE_REGISTRY.get(name)
        if gate is None:
            raise GateError(f"unknown gate {name!r}; known: {sorted(GATE_REGISTRY)}")
        if gate.phase is not phase:
            continue
        results.append(gate.run(context))
    return results


def summarise(results: Sequence[GateResult]) -> Dict[str, Any]:
    """Aggregate gate results into an overall outcome.

    Precedence: INVALID > FAIL > INCONCLUSIVE > PASS. The worst outcome wins, and a
    single INVALID gate makes the whole run uninterpretable regardless of how many
    gates passed.
    """
    outcomes = [r.outcome for r in results]
    for worst in (Outcome.INVALID, Outcome.FAIL, Outcome.INCONCLUSIVE):
        if worst.value in outcomes:
            overall = worst
            break
    else:
        overall = Outcome.PASS
    return {
        "overall": overall.value,
        "blocks_conclusion": overall.blocks_conclusion,
        "counts": {o.value: outcomes.count(o.value) for o in Outcome if outcomes.count(o.value)},
        "results": [r.to_dict() for r in results],
    }
