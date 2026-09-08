"""Experiment comparison.

Purpose: **prevent the accidental comparison of scientifically incompatible
experiments.** Two runs that differ in model version, controlled variables, dataset or
assumptions are not comparable, however similar their metric names look.

This is a direct response to a real defect in the research record: in EXP-0011 one
experimental case could select a hypothesis that another case could not, so the central
comparison was between two differently-shaped admissible sets. Nothing in the tooling
noticed. Now something does.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, Sequence

from .spec import ExperimentSpec

#: Differences in these fields make two experiments incomparable rather than merely
#: different — a metric computed under a different model or on different data is a
#: different quantity, not a comparable measurement of the same one.
BLOCKING_FIELDS = ("model.identifier", "model.version", "datasets", "variables.controlled")


@dataclass
class Difference:
    """One field that differs between two specifications."""

    field_name: str
    left: Any
    right: Any
    blocking: bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            "field": self.field_name,
            "left": self.left,
            "right": self.right,
            "blocking": self.blocking,
        }


@dataclass
class Comparison:
    """Result of comparing two experiments."""

    left_id: str
    right_id: str
    differences: List[Difference] = field(default_factory=list)
    shared_metrics: List[str] = field(default_factory=list)
    metric_values: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    @property
    def blocking(self) -> List[Difference]:
        return [d for d in self.differences if d.blocking]

    @property
    def comparable(self) -> bool:
        """False if any blocking difference exists — the metrics are not commensurable."""
        return not self.blocking

    def to_dict(self) -> Dict[str, Any]:
        return {
            "left": self.left_id,
            "right": self.right_id,
            "comparable": self.comparable,
            "blocking_differences": [d.to_dict() for d in self.blocking],
            "other_differences": [d.to_dict() for d in self.differences if not d.blocking],
            "shared_metrics": self.shared_metrics,
            "metric_values": self.metric_values,
        }

    def render(self) -> str:
        """Markdown summary, leading with comparability."""
        lines = [f"# Comparison — {self.left_id} vs {self.right_id}\n"]
        if self.comparable:
            lines.append(
                "**COMPARABLE.** No blocking difference found. The experiments share a model "
                "version, datasets and controlled variables.\n"
            )
        else:
            lines.append(
                "## ⚠ NOT COMPARABLE\n\n"
                "These experiments differ in ways that make their metrics different quantities. "
                "Comparing the numbers below would be an error.\n"
            )
            lines.append("| Field | " + self.left_id + " | " + self.right_id + " |")
            lines.append("|---|---|---|")
            for d in self.blocking:
                lines.append(f"| `{d.field_name}` | `{d.left}` | `{d.right}` |")
            lines.append("")

        other = [d for d in self.differences if not d.blocking]
        if other:
            lines.append("### Non-blocking differences\n")
            lines.append("| Field | " + self.left_id + " | " + self.right_id + " |")
            lines.append("|---|---|---|")
            for d in other:
                lines.append(f"| `{d.field_name}` | `{d.left}` | `{d.right}` |")
            lines.append("")

        if self.shared_metrics:
            lines.append("### Shared metrics\n")
            lines.append("| Metric | " + self.left_id + " | " + self.right_id + " |")
            lines.append("|---|---|---|")
            for m in self.shared_metrics:
                v = self.metric_values.get(m, {})
                lines.append(f"| `{m}` | {v.get('left', 'n/a')} | {v.get('right', 'n/a')} |")
            lines.append("")
            if not self.comparable:
                lines.append(
                    "**These values are shown for completeness only.** The experiments are not "
                    "comparable, so any difference between them is uninterpretable.\n"
                )
        else:
            lines.append("No metric is defined in both experiments.\n")
        return "\n".join(lines)


def _flatten(spec: ExperimentSpec) -> Dict[str, Any]:
    """Comparable view of a specification."""
    return {
        "kind": spec.kind,
        "model.identifier": spec.model.identifier,
        "model.version": spec.model.version,
        "model.validity_envelope": spec.model.validity_envelope,
        "datasets": sorted(f"{d.identifier}@{d.version}:{d.role}" for d in spec.datasets),
        "variables.independent": spec.variables.independent,
        "variables.dependent": sorted(spec.variables.dependent),
        "variables.controlled": spec.variables.controlled,
        "metrics": sorted(spec.metrics),
        "assumptions": sorted(spec.assumptions),
        "gates": sorted(spec.gates),
        "randomisation.base_seed": spec.randomisation.base_seed,
        "statistical_precision": (
            None if spec.statistical_precision is None
            else {
                "metric": spec.statistical_precision.metric,
                "confidence": spec.statistical_precision.confidence,
                "half_width": spec.statistical_precision.half_width,
            }
        ),
    }


def compare(
    left: ExperimentSpec,
    right: ExperimentSpec,
    *,
    left_stats: Mapping[str, Any] | None = None,
    right_stats: Mapping[str, Any] | None = None,
) -> Comparison:
    """Compare two experiment specifications and, optionally, their statistics."""
    lf, rf = _flatten(left), _flatten(right)
    differences: List[Difference] = []
    for key in sorted(set(lf) | set(rf)):
        lv, rv = lf.get(key), rf.get(key)
        if lv != rv:
            differences.append(Difference(key, lv, rv, blocking=key in BLOCKING_FIELDS))

    shared = sorted(set(left.metrics) & set(right.metrics))
    values: Dict[str, Dict[str, Any]] = {}
    for m in shared:
        entry: Dict[str, Any] = {}
        for side, stats in (("left", left_stats), ("right", right_stats)):
            payload = (stats or {}).get(m)
            if isinstance(payload, Mapping) and "interval" in payload:
                iv = payload["interval"]
                entry[side] = f"{iv['point']:.6g} [{iv['low']:.6g}, {iv['high']:.6g}]"
            elif payload is not None:
                entry[side] = str(payload)
        if entry:
            values[m] = entry

    return Comparison(left.experiment_id, right.experiment_id, differences, shared, values)
