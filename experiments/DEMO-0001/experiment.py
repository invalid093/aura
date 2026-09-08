"""DEMO-0001 — Monte Carlo recovery of a closed-form detection probability.

A framework demonstration, not aerospace research. It exercises the complete lifecycle:
pre-registration, deterministic seeding, Monte Carlo, validity gates, statistical
sufficiency, provenance, report and handoff.

The experiment is designed so that the *truth is known*: the detection probability has
an exact closed form, so this run tests the framework's statistics rather than a
scientific proposition.
"""

from __future__ import annotations

from typing import Any, Mapping

import numpy as np

from aura.evidence import EvidenceClass, Statement
from aura.montecarlo import plan_sample_size, run as mc_run
from aura.runner import ExecutionResult
from models.detector import detection_probability, trial


def execute(context: Mapping[str, Any]) -> ExecutionResult:
    """Run the demonstration and return everything the gates need to judge it."""
    spec = context["spec"]
    deflection = float(spec.variables.independent["deflection"])
    threshold = float(spec.variables.controlled["threshold"])
    sp = spec.statistical_precision

    # ---- sample size is DERIVED from the declared precision, never typed by hand ----
    n = plan_sample_size(
        estimator=sp.metric,
        half_width=sp.half_width,
        confidence=sp.confidence,
        planning_value=sp.planning_value,
    )

    labels = {"deflection": deflection, "threshold": threshold}
    result = mc_run(
        trial,
        n=n,
        base_seed=spec.randomisation.base_seed,
        labels=labels,
        label_fields=spec.randomisation.label_fields,
        estimator=sp.metric,
        confidence=sp.confidence,
    )

    # ---- comparison against the closed form, computed independently of the run ------
    exact = detection_probability(deflection, threshold)
    estimate = result.interval.point
    abs_error = abs(estimate - exact)
    covered = result.interval.low <= exact <= result.interval.high

    # ---- reproducibility: repeat the campaign and require bit-identical samples -----
    repeat = mc_run(
        trial, n=n, base_seed=spec.randomisation.base_seed, labels=labels,
        label_fields=spec.randomisation.label_fields,
        estimator=sp.metric, confidence=sp.confidence,
    )
    identical = bool(np.array_equal(result.samples, repeat.samples))

    statistics = {
        "detection_probability": result.to_dict(),
        "absolute_error_vs_closed_form": {
            "value": abs_error,
            "closed_form": exact,
            "monte_carlo": estimate,
            "interval_covers_closed_form": covered,
        },
    }

    return ExecutionResult(
        statistics=statistics,
        # The envelope variable is the model input under test; the gate compares this
        # against the envelope declared in the specification.
        envelope_observations={"deflection": [deflection, deflection]},
        numerical={"n_nonfinite": 0, "estimator": sp.metric},
        data={"planned": n, "actual": result.n_completed, "failed_trials": result.n_failed},
        reproducibility={"checked": True, "mode": "bitwise", "identical": identical},
        raw_data={"checked": 0, "modified": []},
        achieved={
            "half_width": result.interval.half_width,
            "required_n": n,
            "actual_n": result.n_completed,
        },
        convergence={"trace": result.convergence, "max_final_shrink": 0.25},
        interpretations=[
            Statement(
                EvidenceClass.INTERPRETATION,
                "The Monte Carlo estimate agreeing with the closed form to within the "
                "declared precision, with the interval covering the exact value, is "
                "consistent with the seeding, aggregation and interval machinery being "
                "correct. It is a check of the framework, not evidence about any "
                "physical system.",
            ),
            Statement(
                EvidenceClass.LIMITATION,
                "One deflection value at one threshold. Agreement here does not "
                "establish that the estimators are correct across their whole domain.",
            ),
            Statement(
                EvidenceClass.ASSUMPTION,
                "Bit-identical repeat execution is asserted for this deterministic-seed "
                "configuration on this platform; cross-platform bitwise identity of "
                "floating-point sampling is not claimed.",
            ),
        ],
        limitations=[
            "A demonstration of infrastructure. It supports no aerospace claim.",
            "Reproducibility was verified within a single process on one platform.",
        ],
    )
