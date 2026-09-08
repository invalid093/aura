"""Reusable Monte Carlo engine.

Extracted from EXP-0012, where the trial loop, seed derivation and aggregation were
embedded in the experiment script and therefore untestable and unreusable. Here they
are a component with an explicit contract.

Guarantees
----------
* **Deterministic** — trial *i* always receives the same seed, derived from the base
  seed and the trial's labels, independently of execution order or worker count.
* **Failures are data** — a trial that raises is recorded as a failed trial, not
  silently dropped. Dropping failures biases the estimate towards whatever succeeds.
* **Estimators are pluggable** — the engine aggregates whatever estimator the
  experiment declares rather than hard-coding the mean.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field, asdict
from typing import Any, Callable, Dict, List, Mapping, Optional, Sequence

import numpy as np

from .errors import StatisticalError
from .seeds import derive_seed
from .statistics import (
    Interval,
    convergence_trace,
    mean_ci,
    proportion_ci,
    quantile_ci,
    required_n_mean,
    required_n_proportion,
)

#: A trial takes (rng, labels) and returns a float outcome (or 0/1 for a proportion).
TrialFn = Callable[[np.random.Generator, Mapping[str, Any]], float]


@dataclass
class TrialFailure:
    """One trial that raised."""

    index: int
    seed: int
    labels: Dict[str, Any]
    error: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class MonteCarloResult:
    """Outcome of a Monte Carlo campaign."""

    n_requested: int
    n_completed: int
    failures: List[TrialFailure] = field(default_factory=list)
    samples: np.ndarray = field(default_factory=lambda: np.empty(0))
    estimator: str = "mean"
    interval: Optional[Interval] = None
    convergence: List[Dict[str, float]] = field(default_factory=list)
    required_n: Optional[int] = None
    runtime_seconds: float = 0.0
    base_seed: Optional[int] = None
    label_fields: List[str] = field(default_factory=list)

    @property
    def n_failed(self) -> int:
        return len(self.failures)

    def to_dict(self, *, include_samples: bool = False) -> Dict[str, Any]:
        """Serialise for the evidence package.

        Raw samples are excluded by default: for large campaigns they are REGENERABLE
        from the recorded seeds, so storing them is a retention decision rather than a
        provenance requirement (see :mod:`aura.retention`).
        """
        d: Dict[str, Any] = {
            "estimator": self.estimator,
            "n_requested": self.n_requested,
            "n_completed": self.n_completed,
            "n_failed": self.n_failed,
            "required_n": self.required_n,
            "runtime_seconds": round(self.runtime_seconds, 6),
            "base_seed": self.base_seed,
            "label_fields": list(self.label_fields),
            "failures": [f.to_dict() for f in self.failures[:50]],
            "convergence": self.convergence,
        }
        if self.interval is not None:
            d["interval"] = self.interval.to_dict()
        if include_samples:
            d["samples"] = self.samples.tolist()
        return d


def _aggregate(
    samples: np.ndarray, estimator: str, confidence: float, quantile: float | None
) -> Interval:
    """Apply the declared estimator."""
    if estimator == "proportion":
        uniq = np.unique(samples)
        if not np.all(np.isin(uniq, (0.0, 1.0))):
            raise StatisticalError(
                "estimator 'proportion' requires every trial outcome to be 0 or 1; "
                f"saw values {uniq[:5].tolist()}"
            )
        return proportion_ci(int(samples.sum()), samples.size, confidence)
    if estimator == "mean":
        return mean_ci(samples, confidence)
    if estimator == "quantile":
        if quantile is None:
            raise StatisticalError("estimator 'quantile' requires a quantile value")
        return quantile_ci(samples, quantile, confidence)
    if estimator == "variance":
        # Reported as a point value with a mean-based interval on the squared
        # deviations: adequate for reporting, and the method string says what it is.
        centred = (samples - samples.mean()) ** 2
        iv = mean_ci(centred, confidence)
        return Interval(
            point=float(samples.var(ddof=1)),
            low=max(0.0, iv.low), high=iv.high,
            confidence=confidence, method="variance-via-squared-deviations", n=samples.size,
        )
    raise StatisticalError(
        f"unknown estimator {estimator!r}; known: proportion, mean, quantile, variance"
    )


def run(
    trial: TrialFn,
    *,
    n: int,
    base_seed: int,
    labels: Mapping[str, Any] | None = None,
    label_fields: Sequence[str] | None = None,
    estimator: str = "mean",
    confidence: float = 0.95,
    quantile: float | None = None,
    checkpoints: int = 10,
    max_failures: int | None = None,
) -> MonteCarloResult:
    """Run ``n`` independent trials and aggregate them.

    Parameters
    ----------
    trial:
        Called as ``trial(rng, labels)``. Must not use global RNG state.
    labels:
        Cell labels shared by every trial (e.g. flight condition). The trial index is
        appended automatically so each trial gets its own stream.
    max_failures:
        Abort once this many trials have raised. ``None`` runs to completion and
        reports the failures — preferable when failures are themselves informative.

    Raises
    ------
    StatisticalError
        If every trial failed. An estimate from zero samples is not a weak result, it
        is not a result, and returning one would be a false PASS.
    """
    if n < 1:
        raise StatisticalError("n must be >= 1")
    labels = dict(labels or {})
    started = time.perf_counter()

    values: List[float] = []
    failures: List[TrialFailure] = []

    for i in range(n):
        cell_labels = dict(labels)
        cell_labels["trial"] = i
        seed = derive_seed(base_seed, *[cell_labels[k] for k in sorted(cell_labels)])
        rng = np.random.default_rng(seed)
        try:
            out = float(trial(rng, cell_labels))
            if not np.isfinite(out):
                raise ValueError(f"trial returned non-finite value {out!r}")
            values.append(out)
        except Exception as exc:  # noqa: BLE001 - recorded, never swallowed
            failures.append(TrialFailure(i, seed, cell_labels, f"{type(exc).__name__}: {exc}"))
            if max_failures is not None and len(failures) >= max_failures:
                break

    runtime = time.perf_counter() - started
    samples = np.asarray(values, dtype=float)

    if samples.size == 0:
        raise StatisticalError(
            f"all {len(failures)} trial(s) failed; no estimate can be formed. "
            f"First error: {failures[0].error if failures else 'unknown'}"
        )

    interval = _aggregate(samples, estimator, confidence, quantile)
    trace = convergence_trace(
        samples, confidence, checkpoints,
        kind="proportion" if estimator == "proportion" else "mean",
    )

    return MonteCarloResult(
        n_requested=n,
        n_completed=int(samples.size),
        failures=failures,
        samples=samples,
        estimator=estimator,
        interval=interval,
        convergence=trace,
        runtime_seconds=runtime,
        base_seed=base_seed,
        label_fields=list(label_fields or sorted(labels)),
    )


def plan_sample_size(
    estimator: str,
    half_width: float,
    confidence: float = 0.95,
    planning_value: float | None = None,
) -> int:
    """Required N for a declared precision target.

    ``planning_value`` is the planning proportion for ``proportion`` and the planning
    standard deviation for ``mean``. For ``proportion`` a missing planning value uses
    the conservative worst case p = 0.5.
    """
    if estimator == "proportion":
        return required_n_proportion(half_width, confidence, planning_value)
    if estimator == "mean":
        if planning_value is None:
            raise StatisticalError(
                "planning sigma is required to size a mean experiment; run a pilot first"
            )
        return required_n_mean(half_width, float(planning_value), confidence)
    raise StatisticalError(f"cannot plan sample size for estimator {estimator!r}")
