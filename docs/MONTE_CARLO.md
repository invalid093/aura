# AURA — Monte Carlo and statistical sufficiency

**Question this document answers:** *how do I run stochastic trials, how many do I need,
and what do the intervals actually mean?*

---

## Why this is a component

In EXP-0012 the trial loop, seed derivation and aggregation lived inside the experiment
script. They were therefore untestable, unreusable, and could not be checked against a
known answer. `aura.montecarlo` extracts them with an explicit contract.

## Minimal use

```python
from aura.montecarlo import plan_sample_size, run

n = plan_sample_size("proportion", half_width=0.01, confidence=0.95, planning_value=0.64)

def trial(rng, labels):
    return 1.0 if rng.normal(labels["deflection"], 1.0) > labels["threshold"] else 0.0

result = run(trial, n=n, base_seed=20260908,
             labels={"deflection": 2.0, "threshold": 1.6449},
             estimator="proportion", confidence=0.95)

print(result.interval.point, result.interval.half_width)
```

The trial signature is `trial(rng, labels) -> float`. It must take **all** randomness from
`rng`; reading global RNG state breaks reproducibility silently.

## Sample size is derived, not typed

> AURA should not merely run N trials because the researcher typed N.

Declare the precision you need:

```yaml
statistical_precision:
  metric: proportion
  confidence: 0.95
  half_width: 0.01
  planning_value: 0.64      # optional; omit for the conservative worst case
```

The framework computes required N, measures achieved precision, and reports both:

```
statistical_precision (STATISTICAL): achieved half-width 0.0099718 vs target 0.01
at 95% confidence (required N 8851, actual N 8851)
```

| Estimator | Required N | Notes |
|---|---|---|
| `proportion` | `z²p(1−p)/h²` | `planning_value` omitted ⇒ worst case p = 0.5 (9,604 for h = 0.01) |
| `mean` | `(zσ/h)²` | σ **must** come from a pilot or theory; there is no honest default |

Supplying a planning value gives a smaller N but makes it conditional on that pilot. Which
was used is recorded.

### What this does *not* establish

> **A satisfied precision target is not a validated result.**

It addresses sampling precision under the stated assumptions — i.i.d. trials, a correctly
implemented model — and nothing else. The gate's own evidence carries this caveat, and so
does every generated report. Precision is about how tightly you measured, never about
whether you measured the right thing.

## Guarantees

**Deterministic.** Trial *i* always receives the same seed, derived from the base seed and
its labels, independently of execution order or worker count.

**Failures are data.** A trial that raises becomes a `TrialFailure` recording its index,
seed, labels and error — never a silent drop, which would bias the estimate toward
whatever succeeds. `data_completeness` turns any failures into an `INCONCLUSIVE` gate
outcome. If *every* trial fails, `run` raises: zero samples is not a weak estimate, it is
not an estimate.

**Non-finite outcomes are failures.** A trial returning `inf` or `NaN` is recorded as
failed rather than aggregated.

**Estimators are declared, not chosen after the fact.** The estimator comes from the
specification.

## Estimators and intervals

| Estimator | Interval | Why this one |
|---|---|---|
| `proportion` | **Wilson score** | Wald has badly wrong coverage near p = 0 or 1 and can produce bounds outside [0,1]. AURA's own record reported proportions of 0.058 and 1.000 — exactly where Wald misleads |
| `mean` | Normal approximation, sd with Bessel's correction | Method string records the choice; for n < 30 the interval is optimistic and `convergence_trace` shows whether n is adequate |
| `quantile` | Distribution-free, from binomial order statistics | No distributional assumption |
| `variance` | Point variance with an interval on squared deviations | Reported honestly as `variance-via-squared-deviations` |

`proportion` **refuses** non-binary outcomes rather than silently treating 0.5 as a
success.

## Convergence

`convergence_trace` reports the interval half-width at increasing sample counts. The
`convergence` gate returns `INCONCLUSIVE` if the half-width was still shrinking by more
than 25% over the final checkpoint — evidence the run stopped while the estimate was still
moving. The full trace is published in `statistics.json` so the reader can judge rather
than trust.

## Special functions, without scipy

| Function | Method | Accuracy |
|---|---|---|
| `normal_cdf` | `0.5·erfc(−x/√2)` | machine precision |
| `normal_quantile` | Acklam rational approximation + one Halley refinement | ~1e-15 absolute; verified against published values at p = 0.975, 0.995 |
| `chi2_quantile` | Wilson–Hilferty | better than ~0.5% for dof ≥ 10 — and **raises** for dof < 10 rather than returning a silently inaccurate critical value |

That last refusal matters: a wrong critical value would produce false PASS results, which
is the failure mode a gate framework must not have.

## Validating the engine

`DEMO-0001` exists to check this machinery against a known answer. The detection
probability of a threshold detector is exactly Φ(d − z), so the Monte Carlo estimate can be
compared with truth rather than with another simulation:

| Quantity | Value |
|---|---|
| Closed form Φ(2.0 − 1.6449) | 0.638760 |
| Monte Carlo (n = 8,851) | 0.644221 |
| Absolute error | 0.005461 |
| Declared half-width target | 0.010000 |
| 95% CI | [0.63419, 0.65413] — **contains the exact value** |

The prediction was registered in the specification before the run and is not refitted.

Throughput on the development machine: ~73,000 trials/s for a trivial trial function; the
dominant cost in a real experiment is the model evaluation, not the engine.
