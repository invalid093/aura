"""Statistical estimators, intervals and sufficiency calculations.

Dependency-free by design: ``scipy`` is not required, so the framework runs anywhere
numpy does. The two special functions needed are built from ``math.erf``/``math.erfc``
(exact to machine precision in CPython) plus a refined rational approximation for the
normal quantile.

Scope discipline
----------------
Every function here answers a *precision* question under stated assumptions. None of
them establishes correctness. :func:`required_n_proportion` tells you how many trials
give a half-width of 0.01 **if** trials are independent and identically distributed;
it says nothing about whether the simulated system is the right one. The framework
repeats this caveat in generated reports rather than letting a satisfied precision
target read as a validated result.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, asdict
from typing import Any, Dict, Literal, Sequence

import numpy as np

from .errors import StatisticalError

__all__ = [
    "Interval",
    "normal_cdf",
    "normal_quantile",
    "chi2_quantile",
    "proportion_ci",
    "mean_ci",
    "quantile_ci",
    "required_n_proportion",
    "required_n_mean",
    "achieved_half_width",
    "convergence_trace",
]


# --------------------------------------------------------------------------- intervals
@dataclass(frozen=True)
class Interval:
    """A point estimate with a confidence interval.

    ``method`` names the estimator so that a reader can reproduce the number, and
    ``confidence`` is the nominal coverage — nominal, because coverage of any of these
    intervals is approximate at small n.
    """

    point: float
    low: float
    high: float
    confidence: float
    method: str
    n: int

    @property
    def half_width(self) -> float:
        """Half the interval width — the quantity precision targets are stated in."""
        return 0.5 * (self.high - self.low)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["half_width"] = self.half_width
        return d


# ------------------------------------------------------------------- special functions
def normal_cdf(x: float) -> float:
    """Standard normal CDF, via ``erfc`` (machine precision, no approximation error)."""
    return 0.5 * math.erfc(-float(x) / math.sqrt(2.0))


# Acklam's rational approximation coefficients; refined below with a Halley step.
_A = (-3.969683028665376e01, 2.209460984245205e02, -2.759285104469687e02,
      1.383577518672690e02, -3.066479806614716e01, 2.506628277459239e00)
_B = (-5.447609879822406e01, 1.615858368580409e02, -1.556989798598866e02,
      6.680131188771972e01, -1.328068155288572e01)
_C = (-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e00,
      -2.549732539343734e00, 4.374664141464968e00, 2.938163982698783e00)
_D = (7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e00,
      3.754408661907416e00)
_P_LOW = 0.02425


def normal_quantile(p: float) -> float:
    """Inverse standard normal CDF (probit).

    Accurate to ~1e-15 absolute: Acklam's approximation followed by one Halley
    refinement against :func:`normal_cdf`.

    >>> round(normal_quantile(0.975), 10)
    1.959963985
    """
    p = float(p)
    if not 0.0 < p < 1.0:
        raise StatisticalError(f"normal_quantile requires 0 < p < 1, got {p}")

    if p < _P_LOW:
        q = math.sqrt(-2.0 * math.log(p))
        x = (((((_C[0] * q + _C[1]) * q + _C[2]) * q + _C[3]) * q + _C[4]) * q + _C[5]) / \
            ((((_D[0] * q + _D[1]) * q + _D[2]) * q + _D[3]) * q + 1.0)
    elif p <= 1.0 - _P_LOW:
        q = p - 0.5
        r = q * q
        x = (((((_A[0] * r + _A[1]) * r + _A[2]) * r + _A[3]) * r + _A[4]) * r + _A[5]) * q / \
            (((((_B[0] * r + _B[1]) * r + _B[2]) * r + _B[3]) * r + _B[4]) * r + 1.0)
    else:
        q = math.sqrt(-2.0 * math.log(1.0 - p))
        x = -(((((_C[0] * q + _C[1]) * q + _C[2]) * q + _C[3]) * q + _C[4]) * q + _C[5]) / \
            ((((_D[0] * q + _D[1]) * q + _D[2]) * q + _D[3]) * q + 1.0)

    # Halley refinement: removes the ~1e-9 approximation error of the rational form.
    e = normal_cdf(x) - p
    u = e * math.sqrt(2.0 * math.pi) * math.exp(x * x / 2.0)
    return x - u / (1.0 + x * u / 2.0)


def chi2_quantile(p: float, dof: int) -> float:
    """Chi-square quantile via the Wilson–Hilferty transform.

    Accurate to better than ~0.5% for ``dof >= 10``, which is the regime AURA's
    goodness-of-fit gates operate in. Deliberately *not* offered for small ``dof``:
    the approximation degrades and a silently wrong critical value would produce false
    PASS results, which is the one failure mode a gate framework must not have.
    """
    if dof < 10:
        raise StatisticalError(
            f"chi2_quantile uses Wilson-Hilferty and is not accurate for dof < 10 (got {dof}); "
            "use an exact routine or increase the degrees of freedom"
        )
    z = normal_quantile(p)
    t = 2.0 / (9.0 * dof)
    return dof * (1.0 - t + z * math.sqrt(t)) ** 3


# ---------------------------------------------------------------------- point + interval
def proportion_ci(successes: int, n: int, confidence: float = 0.95) -> Interval:
    """Wilson score interval for a binomial proportion.

    Wilson rather than Wald: the Wald interval has badly wrong coverage near p = 0 or 1
    and can produce bounds outside [0, 1]. AURA's own EXP-0012 reported proportions near
    0.058 and EXP-0010 reported 1.000 — exactly the regime where Wald misleads.
    """
    if n <= 0:
        raise StatisticalError("proportion_ci requires n > 0")
    if not 0 <= successes <= n:
        raise StatisticalError(f"successes ({successes}) must lie in [0, n={n}]")

    z = normal_quantile(0.5 + confidence / 2.0)
    p_hat = successes / n
    denom = 1.0 + z * z / n
    centre = (p_hat + z * z / (2 * n)) / denom
    half = (z / denom) * math.sqrt(p_hat * (1 - p_hat) / n + z * z / (4 * n * n))
    return Interval(
        point=p_hat,
        low=max(0.0, centre - half),
        high=min(1.0, centre + half),
        confidence=confidence,
        method="wilson-score",
        n=n,
    )


def mean_ci(samples: Sequence[float] | np.ndarray, confidence: float = 0.95) -> Interval:
    """Normal-approximation confidence interval for a mean.

    Uses the sample standard deviation with Bessel's correction. For ``n < 30`` the
    normal quantile understates the interval; the method string records the choice so a
    reader can judge it, and :func:`convergence_trace` will show whether n is adequate.
    """
    a = np.asarray(samples, dtype=float).ravel()
    n = a.size
    if n < 2:
        raise StatisticalError("mean_ci requires at least 2 samples")
    if not np.all(np.isfinite(a)):
        raise StatisticalError("mean_ci received non-finite samples")

    z = normal_quantile(0.5 + confidence / 2.0)
    mean = float(a.mean())
    se = float(a.std(ddof=1)) / math.sqrt(n)
    return Interval(mean, mean - z * se, mean + z * se, confidence, "normal-approx", n)


def quantile_ci(
    samples: Sequence[float] | np.ndarray, q: float, confidence: float = 0.95
) -> Interval:
    """Distribution-free CI for a quantile, from binomial order statistics.

    Makes no distributional assumption: the rank bounds come from the binomial
    distribution of how many samples fall below the true quantile.
    """
    a = np.sort(np.asarray(samples, dtype=float).ravel())
    n = a.size
    if n < 2:
        raise StatisticalError("quantile_ci requires at least 2 samples")
    if not 0.0 < q < 1.0:
        raise StatisticalError(f"quantile_ci requires 0 < q < 1, got {q}")

    z = normal_quantile(0.5 + confidence / 2.0)
    spread = z * math.sqrt(n * q * (1 - q))
    lo = max(0, int(math.floor(n * q - spread)))
    hi = min(n - 1, int(math.ceil(n * q + spread)))
    point = float(np.quantile(a, q))
    return Interval(point, float(a[lo]), float(a[hi]), confidence, "order-statistic", n)


# ------------------------------------------------------------------------- sufficiency
def required_n_proportion(
    half_width: float,
    confidence: float = 0.95,
    p_planning: float | None = None,
) -> int:
    """Trials needed for a proportion CI of at most ``half_width``.

    Parameters
    ----------
    p_planning:
        Planning value for the proportion. ``None`` uses the conservative worst case
        p = 0.5, which is the honest default before any data exists. Supplying a
        planning value from a pilot gives a smaller N but makes the answer conditional
        on that pilot — the framework records which was used.

    Returns the normal-approximation sample size; the achieved half-width is always
    measured afterwards from the realised Wilson interval rather than assumed.
    """
    if half_width <= 0:
        raise StatisticalError("half_width must be positive")
    p = 0.5 if p_planning is None else float(p_planning)
    if not 0.0 <= p <= 1.0:
        raise StatisticalError(f"p_planning must lie in [0, 1], got {p}")
    z = normal_quantile(0.5 + confidence / 2.0)
    return int(math.ceil(z * z * p * (1 - p) / (half_width * half_width)))


def required_n_mean(half_width: float, sigma: float, confidence: float = 0.95) -> int:
    """Trials needed for a mean CI of at most ``half_width``, given a planning ``sigma``.

    ``sigma`` must come from a pilot or from theory; if it is wrong the achieved
    precision will differ, which is why the framework reports achieved precision
    separately from required N.
    """
    if half_width <= 0:
        raise StatisticalError("half_width must be positive")
    if sigma <= 0:
        raise StatisticalError("sigma must be positive")
    z = normal_quantile(0.5 + confidence / 2.0)
    return int(math.ceil((z * sigma / half_width) ** 2))


def achieved_half_width(interval: Interval) -> float:
    """Convenience accessor used by the statistical validity gate."""
    return interval.half_width


def convergence_trace(
    samples: Sequence[float] | np.ndarray,
    confidence: float = 0.95,
    checkpoints: int = 10,
    kind: Literal["mean", "proportion"] = "mean",
) -> list[dict[str, float]]:
    """Half-width of the running estimate at increasing sample counts.

    A shrinking trace that flattens near the target is evidence the estimator has
    converged; a trace still falling steeply at the final n indicates the run stopped
    early. Reported in the evidence package so the reader can judge this rather than
    taking the final number on trust.
    """
    a = np.asarray(samples, dtype=float).ravel()
    n = a.size
    if n < 2:
        raise StatisticalError("convergence_trace requires at least 2 samples")
    if checkpoints < 1:
        raise StatisticalError("checkpoints must be >= 1")

    marks = sorted({max(2, int(round(n * (i + 1) / checkpoints))) for i in range(checkpoints)})
    trace: list[dict[str, float]] = []
    for m in marks:
        window = a[:m]
        if kind == "proportion":
            iv = proportion_ci(int(window.sum()), m, confidence)
        else:
            iv = mean_ci(window, confidence)
        trace.append({"n": m, "point": iv.point, "half_width": iv.half_width})
    return trace
