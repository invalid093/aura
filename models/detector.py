"""A minimal threshold detector — the model used by AURA's framework demonstrations.

Deliberately trivial and scientifically transparent. Its purpose is to exercise the
research-engineering machinery (pre-registration, seeds, Monte Carlo, gates, provenance,
reporting), **not** to produce aerospace research. It was chosen because it has an exact
closed-form answer, so the framework's statistics can be checked against truth rather
than against another simulation.

Model
-----
A signal of deflection ``d`` is present in unit-variance Gaussian noise. The detector
forms a single sufficient statistic and declares a detection when it exceeds a threshold
``z``::

    t ~ N(d, 1)          under signal-present
    detect  <=>  t > z

so the exact detection probability is

.. math::

    P_D = \\Phi(d - z)

and the exact false-alarm probability with no signal is :math:`P_{FA} = \\Phi(-z)`.

Validity envelope
-----------------
The model is declared valid for ``0 <= d <= 6``. Beyond that the detection probability
is numerically indistinguishable from 1 in double precision, so a Monte Carlo estimate
carries no information and the closed-form comparison becomes vacuous. This bound is
what DEMO-0002 deliberately violates.
"""

from __future__ import annotations

import numpy as np

from aura.statistics import normal_cdf, normal_quantile

#: Declared validity envelope of the model. Mirrored in the experiment specifications;
#: the runtime gate checks observations against the spec, not against this constant.
VALID_DEFLECTION = (0.0, 6.0)


def threshold_for_false_alarm(alpha: float) -> float:
    """Detection threshold giving false-alarm probability ``alpha``."""
    if not 0.0 < alpha < 1.0:
        raise ValueError(f"alpha must lie in (0, 1), got {alpha}")
    return normal_quantile(1.0 - alpha)


def detection_probability(deflection: float, threshold: float) -> float:
    """Exact detection probability :math:`\\Phi(d - z)`.

    This is the closed-form prediction the demonstration tests its Monte Carlo estimate
    against. It is computed from ``erfc`` and carries no approximation error.
    """
    return normal_cdf(float(deflection) - float(threshold))


def trial(rng: np.random.Generator, labels: dict) -> float:
    """One Monte Carlo trial: returns 1.0 for a detection, 0.0 otherwise.

    Takes its randomness solely from ``rng``, which the Monte Carlo engine seeds
    deterministically. It reads no global state, so the trial is reproducible in
    isolation from its seed alone.
    """
    d = float(labels["deflection"])
    z = float(labels["threshold"])
    statistic = rng.normal(loc=d, scale=1.0)
    return 1.0 if statistic > z else 0.0
