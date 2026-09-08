"""DEMO-0002 — a deliberately invalid run.

This experiment is *designed to be rejected*. It runs the same threshold-detector model
as DEMO-0001 at a deflection of 9.0, which lies outside the model's declared validity
envelope of [0.0, 6.0].

The execution code below is deliberately **not** defensive: it does not check the
envelope, and it reports its observations honestly. That is the point. The researcher's
code does not have to remember; the framework enforces the envelope at the runtime gate,
marks the run ``INVALID``, writes a failure record, and refuses to emit a scientific
conclusion — even though the numbers produced look excellent.

This is the demonstration counterpart of FAIL-0001 in the historical research record,
where the flight condition that had departed controlled flight was the one producing the
most favourable-looking distinguishability matrix in the study.
"""

from __future__ import annotations

from typing import Any, Mapping

from aura.evidence import EvidenceClass, Statement
from aura.montecarlo import plan_sample_size, run as mc_run
from aura.runner import ExecutionResult
from models.detector import detection_probability, trial


def execute(context: Mapping[str, Any]) -> ExecutionResult:
    """Run at an out-of-envelope operating point and report observations truthfully."""
    spec = context["spec"]
    deflection = float(spec.variables.independent["deflection"])
    threshold = float(spec.variables.controlled["threshold"])
    sp = spec.statistical_precision

    n = plan_sample_size(
        estimator=sp.metric,
        half_width=sp.half_width,
        confidence=sp.confidence,
        planning_value=sp.planning_value,
    )

    labels = {"deflection": deflection, "threshold": threshold}
    result = mc_run(
        trial, n=n, base_seed=spec.randomisation.base_seed, labels=labels,
        label_fields=spec.randomisation.label_fields,
        estimator=sp.metric, confidence=sp.confidence,
    )

    return ExecutionResult(
        statistics={
            "detection_probability": result.to_dict(),
            "closed_form_reference": {
                "value": detection_probability(deflection, threshold),
                "note": "Computed for completeness. Outside the declared envelope this "
                        "comparison is not informative: both numbers saturate at 1.",
            },
        },
        # Reported honestly. The gate — not this function — decides what it means.
        envelope_observations={"deflection": [deflection, deflection]},
        numerical={"n_nonfinite": 0, "estimator": sp.metric},
        data={"planned": n, "actual": result.n_completed, "failed_trials": result.n_failed},
        achieved={
            "half_width": result.interval.half_width,
            "required_n": n,
            "actual_n": result.n_completed,
        },
        convergence={"trace": result.convergence, "max_final_shrink": 0.25},
        interpretations=[
            Statement(
                EvidenceClass.INTERPRETATION,
                "If AURA is working, this run is marked INVALID and no conclusion is "
                "drawn from it — despite an estimate that looks essentially perfect. "
                "An apparently excellent result from outside the validity envelope is "
                "the most dangerous kind, because nothing about the number itself "
                "signals the problem.",
            ),
        ],
        limitations=[
            "The operating point is outside the model's declared validity envelope, so "
            "no number produced by this run describes anything the model represents.",
        ],
    )
