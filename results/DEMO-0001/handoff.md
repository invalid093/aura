# HANDOFF — DEMO-0001: Monte Carlo recovery of a closed-form detection probability

**This document is self-contained.** It assumes no access to the repository and no memory of the session that produced it. It is written to be attacked.

**Status:** `COMPLETED` · **Gates:** `PASS` · **Run:** `98c047b361ef55d9` · **Code:** `ce8a9a636898` (dirty)

---

## Objective

Does the AURA Monte Carlo and statistics pipeline recover a known closed-form probability to its declared precision, and do its confidence intervals cover the true value?

## Hypothesis

A Monte Carlo estimate of detection probability produced by this framework agrees with the exact closed-form value Phi(d - z), to within the pre-declared statistical precision, with no refitting of any kind.

## Prediction (pre-registered)

> With deflection d = 2.0 and threshold z = Phi^-1(0.95) = 1.6449, the exact detection probability is Phi(0.3551) = 0.63875. The Monte Carlo estimate will lie within the declared half-width of 0.01 of that value, and the 95% confidence interval will contain it.

## Setup

- **Model:** `threshold-detector` version `1.0`
- **Declared validity envelope:**
  - `deflection` ∈ [0.0, 6.0]
- **Dataset (output):** `DS-DEMO-0001` @ `1.0`
- **Randomisation:** base seed `20260908`, per-cell seeds derived by SHA-256 over `['deflection', 'threshold', 'trial']`; no global RNG state is used.

## Assumptions

Every result below is conditional on these.

- **`ASSUMPTION`** Trials are independent and identically distributed; the Monte Carlo interval is valid only under this assumption.
- **`ASSUMPTION`** The detector statistic is exactly Gaussian with unit variance, so the closed-form prediction Phi(d - z) is exact rather than approximate.
- **`ASSUMPTION`** The pseudo-random generator (numpy PCG64) is an adequate source of independent normal variates at this sample size.
- **`ASSUMPTION`** Detection is defined as the statistic strictly exceeding the threshold; ties have probability zero in continuous noise and are not handled specially.

## Methods

| Role | Variable | Value |
|---|---|---|
| independent | `deflection` | 2.0 |
| dependent | `detection_probability` | measured |
| controlled | `estimator` | proportion |
| controlled | `noise_variance` | 1.0 |
| controlled | `threshold` | 1.6448536269514722 |

Metrics: `detection_probability`, `absolute_error_vs_closed_form`

## Data

- Specification hash: `sha256:00255c940ca336d12aa5620abac70ec0…`
- Configuration hashes: `specification`=`f5c680578b51…`
- Environment: python 3.13.15, numpy 2.5.2, Windows/AMD64

## Results

- **`CALCULATION`** `absolute_error_vs_closed_form` = `{'value': 0.0054609606659722365, 'closed_form': 0.6387600313123353, 'monte_carlo': 0.6442209919783075, 'interval_covers_closed_form': True}`
- **`CALCULATION`** `detection_probability` = 0.644221 [0.634187, 0.65413] (95%, wilson-score, n=8851); trials completed 8851/8851, failed 0

## Validation gates

| Gate | Phase | Outcome |
|---|---|---|
| `provenance_complete` | PREFLIGHT | **PASS** — provenance chain complete (WARNING: working tree dirty; commit alone does not reproduce this run) |
| `seed_policy_declared` | PREFLIGHT | **PASS** — seeds derived from base 20260908 over ['deflection', 'threshold', 'trial'] |
| `frozen_test_integrity` | PREFLIGHT | **PASS** — no frozen test declared for this experiment |
| `model_validity_envelope` | RUNTIME | **PASS** — all 1 envelope variable(s) within declared bounds |
| `numerical_validity` | RUNTIME | **PASS** — no non-finite values; timing self-consistent |
| `data_completeness` | POST | **PASS** — all 8851 trials recorded |
| `reproducibility` | POST | **PASS** — repeat execution was bit-identical |
| `raw_data_immutable` | POST | **PASS** — 0 raw artefact(s) unchanged |
| `statistical_precision` | STATISTICAL | **PASS** — achieved half-width 0.0099718 vs target 0.01 at 95% confidence (required N 8851, actual N 8851) |
| `convergence` | STATISTICAL | **PASS** — half-width changed 5.2% over the final checkpoint |

**Overall: `PASS`**

## Failures

None recorded for this run.

## Corrections

None recorded.

## Evidence classification

**Measured by the system:**

- `CALCULATION` — `absolute_error_vs_closed_form`
- `CALCULATION` — `detection_probability`

**Inferred by the researcher:**

- **`INTERPRETATION`** The Monte Carlo estimate agreeing with the closed form to within the declared precision, with the interval covering the exact value, is consistent with the seeding, aggregation and interval machinery being correct. It is a check of the framework, not evidence about any physical system.
- **`LIMITATION`** One deflection value at one threshold. Agreement here does not establish that the estimators are correct across their whole domain.
- **`ASSUMPTION`** Bit-identical repeat execution is asserted for this deterministic-seed configuration on this platform; cross-platform bitwise identity of floating-point sampling is not claimed.

## Limitations

- **`LIMITATION`** A demonstration of infrastructure. It supports no aerospace claim.
- **`LIMITATION`** Reproducibility was verified within a single process on one platform.
- **`LIMITATION`** Working tree was dirty; the recorded commit alone does not reproduce this run.

## Claims that are NOT supported

- Any claim outside the declared validity envelope.
- Any claim of operational, real-aircraft, or safety-critical applicability.
- Any causal claim; the design measures association under fixed conditions.

## Conclusion

`COMPLETED`. The run was valid and met its declared precision. What that implies for the hypothesis is a researcher judgement, recorded above under *inferred*, and is not generated by the framework.

## Questions for independent review

**What should another researcher try to prove wrong?**

- Is the declared validity envelope actually the right one, or does it merely bound what this configuration happens to produce?
- Is the pre-registered prediction falsifiable as written, or could any outcome be read as consistent with it?
- Does the precision target address the question being asked, or only the one that is cheap to measure?
- Are the assumptions listed above complete — what is being assumed silently?
- Would the same specification, run by someone else from the recorded configuration, produce these numbers?
