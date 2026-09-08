"""Preflight validation of an experiment specification.

Runs **before any computation**. An invalid specification must never reach a simulator:
the cheapest possible moment to catch a missing hypothesis or an output collision is
before a single trajectory is integrated.

Validation returns *all* problems rather than raising on the first, because fixing a
specification one error per run is how researchers stop reading error messages.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict, List, Sequence

from .errors import SpecificationError
from .spec import ID_PATTERN, KINDS, ExperimentSpec
from .status import Status

#: Severity levels. ERROR blocks execution; WARNING is recorded and proceeds.
ERROR = "ERROR"
WARNING = "WARNING"


@dataclass(frozen=True)
class Problem:
    """One validation finding."""

    severity: str
    field: str
    message: str

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"[{self.severity}] {self.field}: {self.message}"


@dataclass(frozen=True)
class ValidationReport:
    """Outcome of preflight validation."""

    experiment_id: str
    problems: List[Problem]

    @property
    def errors(self) -> List[Problem]:
        return [p for p in self.problems if p.severity == ERROR]

    @property
    def warnings(self) -> List[Problem]:
        return [p for p in self.problems if p.severity == WARNING]

    @property
    def ok(self) -> bool:
        """True when execution may proceed (warnings do not block)."""
        return not self.errors

    def to_dict(self) -> Dict[str, Any]:
        return {
            "experiment_id": self.experiment_id,
            "ok": self.ok,
            "errors": [str(p) for p in self.errors],
            "warnings": [str(p) for p in self.warnings],
        }

    def raise_if_failed(self) -> None:
        """Raise :class:`SpecificationError` listing every error."""
        if self.ok:
            return
        joined = "; ".join(str(p) for p in self.errors)
        raise SpecificationError(f"specification rejected ({len(self.errors)} error(s)): {joined}")


def validate_spec(
    spec: ExperimentSpec,
    *,
    root: str = ".",
    known_experiment_ids: Sequence[str] = (),
    allow_existing_output: bool = False,
) -> ValidationReport:
    """Validate ``spec``; see :mod:`aura.validation` for the checklist rationale.

    Parameters
    ----------
    known_experiment_ids:
        Ids already present in the registry. Used to detect an id collision, which
        would silently overwrite a previous experiment's record.
    allow_existing_output:
        Set true only for a deliberate re-run into an existing directory. The default
        refuses, because overwriting a finalised evidence package destroys provenance.
    """
    p: List[Problem] = []

    def err(f: str, m: str) -> None:
        p.append(Problem(ERROR, f, m))

    def warn(f: str, m: str) -> None:
        p.append(Problem(WARNING, f, m))

    # -- identity ------------------------------------------------------------------
    if not ID_PATTERN.match(spec.experiment_id):
        err("experiment_id", f"{spec.experiment_id!r} does not match EXP-#### or DEMO-####")
    if spec.experiment_id in known_experiment_ids:
        err("experiment_id", f"{spec.experiment_id} already exists in the registry")

    if spec.kind not in KINDS:
        err("kind", f"{spec.kind!r} is not one of {sorted(KINDS)}")

    try:
        Status(spec.status)
    except ValueError:
        err("status", f"{spec.status!r} is not a valid Status")

    # -- scientific content --------------------------------------------------------
    # These four exist because a specification without them cannot be falsified, and an
    # unfalsifiable experiment is the failure mode the whole framework targets.
    for name, value in (
        ("research_question", spec.research_question),
        ("hypothesis", spec.hypothesis),
        ("prediction", spec.prediction),
    ):
        if len(value.strip()) < 15:
            err(name, "must be a substantive statement, not a placeholder")

    if not spec.metrics:
        err("metrics", "at least one metric must be defined")
    if len(set(spec.metrics)) != len(spec.metrics):
        err("metrics", "duplicate metric names")

    if not spec.variables.dependent:
        err("variables.dependent", "at least one dependent variable must be named")
    if not spec.variables.independent:
        warn("variables.independent", "no independent variable — is this a fixed-point run?")
    if not spec.variables.controlled:
        warn(
            "variables.controlled",
            "nothing declared controlled; an undeclared control is untraceable later",
        )

    if not spec.assumptions:
        err("assumptions", "assumptions must be documented (may not be an empty list)")

    # -- model and envelope --------------------------------------------------------
    if not spec.model.identifier:
        err("model.identifier", "model identifier is required")
    if not spec.model.version:
        err("model.version", "model version is required")
    if not spec.model.validity_envelope:
        # Not an error: an infrastructure experiment may have no physical envelope.
        (err if spec.kind in ("exploratory", "confirmatory") else warn)(
            "model.validity_envelope",
            "no validity envelope declared; results cannot be checked against one "
            "(this is the defect behind FAIL-0001)",
        )
    else:
        for key, bounds in spec.model.validity_envelope.items():
            if not (isinstance(bounds, (list, tuple)) and len(bounds) == 2):
                err(f"model.validity_envelope.{key}", "must be a two-element [min, max]")
            elif bounds[0] > bounds[1]:
                err(f"model.validity_envelope.{key}", f"min > max ({bounds[0]} > {bounds[1]})")

    # -- datasets ------------------------------------------------------------------
    if not spec.datasets:
        warn("datasets", "no dataset declared; the experiment is self-contained")
    seen: set[str] = set()
    for d in spec.datasets:
        if not d.identifier:
            err("datasets", "dataset identifier is required")
        if d.identifier in seen:
            err("datasets", f"duplicate dataset identifier {d.identifier}")
        seen.add(d.identifier)
        if d.role not in ("input", "output"):
            err("datasets", f"role must be input or output, got {d.role!r}")
        if not d.version:
            err("datasets", f"{d.identifier} has no version")

    # -- randomisation -------------------------------------------------------------
    r = spec.randomisation
    if r.enabled:
        if r.base_seed is None:
            err("randomisation.base_seed", "required when randomisation is enabled")
        elif not isinstance(r.base_seed, int) or isinstance(r.base_seed, bool):
            err("randomisation.base_seed", "must be an integer")
        if not r.label_fields:
            err(
                "randomisation.label_fields",
                "required when randomisation is enabled; seeds must be derivable per cell",
            )
        if r.repetitions is not None and r.repetitions < 1:
            err("randomisation.repetitions", "must be >= 1")
    else:
        if r.repetitions:
            warn("randomisation", "repetitions declared but randomisation is disabled")

    # -- statistical precision -----------------------------------------------------
    sp = spec.statistical_precision
    if sp:
        if sp.metric not in ("proportion", "mean"):
            err("statistical_precision.metric", "must be 'proportion' or 'mean'")
        if not 0.0 < sp.confidence < 1.0:
            err("statistical_precision.confidence", "must lie strictly in (0, 1)")
        if sp.half_width <= 0:
            err("statistical_precision.half_width", "must be positive")
        if sp.metric == "proportion" and sp.planning_value is not None:
            if not 0.0 <= float(sp.planning_value) <= 1.0:
                err("statistical_precision.planning_value", "proportion planning value must be in [0,1]")
        if sp.metric == "mean" and sp.planning_value is not None:
            if float(sp.planning_value) <= 0:
                err("statistical_precision.planning_value", "sigma planning value must be positive")
        if not r.enabled:
            err(
                "statistical_precision",
                "a precision target requires randomisation to be enabled",
            )
    elif r.enabled:
        warn(
            "statistical_precision",
            "stochastic experiment without a precision target; N is then an unjustified choice",
        )

    # -- frozen test ---------------------------------------------------------------
    ft = spec.frozen_test
    if spec.kind == "confirmatory" and not ft.enabled:
        err("frozen_test.enabled", "confirmatory experiments must declare a frozen test")
    if ft.enabled:
        if not ft.path:
            err("frozen_test.path", "required when a frozen test is declared")
        elif not os.path.exists(os.path.join(root, ft.path)):
            err("frozen_test.path", f"declared frozen test path does not exist: {ft.path}")
        if not ft.checksum_file:
            err(
                "frozen_test.checksum_file",
                "required: integrity cannot be asserted without a recorded checksum",
            )

    # -- gates ---------------------------------------------------------------------
    if not spec.gates:
        err("gates", "at least one validity gate must be declared")
    else:
        from .gates import GATE_REGISTRY  # local import avoids a cycle

        for g in spec.gates:
            if g not in GATE_REGISTRY:
                err("gates", f"unknown gate {g!r}; known: {sorted(GATE_REGISTRY)}")
        if len(set(spec.gates)) != len(spec.gates):
            err("gates", "duplicate gate names")

    # -- outputs -------------------------------------------------------------------
    if not spec.output_dir:
        err("output_dir", "an output location is required")
    else:
        if os.path.isabs(spec.output_dir) or ":" in spec.output_dir:
            err("output_dir", "must be a repository-relative path (no machine-specific paths)")
        if ".." in spec.output_dir.split("/"):
            err("output_dir", "must not escape the repository root")
        target = os.path.join(root, spec.output_dir)
        if os.path.exists(target) and os.listdir(target) and not allow_existing_output:
            err(
                "output_dir",
                f"{spec.output_dir} already exists and is non-empty; "
                "refusing to overwrite a previous experiment record",
            )
    return ValidationReport(spec.experiment_id, p)
