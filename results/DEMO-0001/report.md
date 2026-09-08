# DEMO-0001 — Monte Carlo recovery of a closed-form detection probability

**Status:** `COMPLETED` · **Kind:** infrastructure · **Gates:** `PASS` · **Run:** `98c047b361ef55d9` · **Generated:** 2026-09-08T15:07:47.850281+00:00

---

## Research question

Does the AURA Monte Carlo and statistics pipeline recover a known closed-form probability to its declared precision, and do its confidence intervals cover the true value?

## Hypothesis

A Monte Carlo estimate of detection probability produced by this framework agrees with the exact closed-form value Phi(d - z), to within the pre-declared statistical precision, with no refitting of any kind.

## Prediction

Pre-registered before execution:

> With deflection d = 2.0 and threshold z = Phi^-1(0.95) = 1.6449, the exact detection probability is Phi(0.3551) = 0.63875. The Monte Carlo estimate will lie within the declared half-width of 0.01 of that value, and the 95% confidence interval will contain it.

## Experimental design

| Role | Variable | Value |
|---|---|---|
| independent | `deflection` | 2.0 |
| dependent | `detection_probability` | measured |
| controlled | `estimator` | proportion |
| controlled | `noise_variance` | 1.0 |
| controlled | `threshold` | 1.6448536269514722 |

## Assumptions

The results below are conditional on every one of these.

- **`ASSUMPTION`** Trials are independent and identically distributed; the Monte Carlo interval is valid only under this assumption.
- **`ASSUMPTION`** The detector statistic is exactly Gaussian with unit variance, so the closed-form prediction Phi(d - z) is exact rather than approximate.
- **`ASSUMPTION`** The pseudo-random generator (numpy PCG64) is an adequate source of independent normal variates at this sample size.
- **`ASSUMPTION`** Detection is defined as the statistic strictly exceeding the threshold; ties have probability zero in continuous noise and are not handled specially.

## Configuration

| Item | Value |
|---|---|
| model | `threshold-detector` @ `1.0` |
| validity envelope `deflection` | [0.0, 6.0] |
| dataset (output) | `DS-DEMO-0001` @ `1.0` |
| config `specification` | `sha256:f5c680578b51c768…` |
| seed policy | base `20260908` over `['deflection', 'threshold', 'trial']` |

## Validation gates

| Gate | Phase | Outcome | Detail |
|---|---|---|---|
| `provenance_complete` | PREFLIGHT | ✅ **PASS** | provenance chain complete (WARNING: working tree dirty; commit alone does not reproduce this run) |
| `seed_policy_declared` | PREFLIGHT | ✅ **PASS** | seeds derived from base 20260908 over ['deflection', 'threshold', 'trial'] |
| `frozen_test_integrity` | PREFLIGHT | ✅ **PASS** | no frozen test declared for this experiment |
| `model_validity_envelope` | RUNTIME | ✅ **PASS** | all 1 envelope variable(s) within declared bounds |
| `numerical_validity` | RUNTIME | ✅ **PASS** | no non-finite values; timing self-consistent |
| `data_completeness` | POST | ✅ **PASS** | all 8851 trials recorded |
| `reproducibility` | POST | ✅ **PASS** | repeat execution was bit-identical |
| `raw_data_immutable` | POST | ✅ **PASS** | 0 raw artefact(s) unchanged |
| `statistical_precision` | STATISTICAL | ✅ **PASS** | achieved half-width 0.0099718 vs target 0.01 at 95% confidence (required N 8851, actual N 8851) |
| `convergence` | STATISTICAL | ✅ **PASS** | half-width changed 5.2% over the final checkpoint |

**Overall: `PASS`**

## Execution

| Item | Value |
|---|---|
| started (UTC) | 2026-09-08T15:07:47.401889+00:00 |
| finished (UTC) | 2026-09-08T15:07:47.850281+00:00 |
| runtime (s) | 0.283166 |
| code | `ce8a9a636898` **(dirty tree)** |
| framework | `0.8.0` |
| python | 3.13.15 on Windows/AMD64 |
| numpy | 2.5.2 |

## Results

### `absolute_error_vs_closed_form`

- **`CALCULATION`** value: `{'value': 0.0054609606659722365, 'closed_form': 0.6387600313123353, 'monte_carlo': 0.6442209919783075, 'interval_covers_closed_form': True}`

### `detection_probability`

- **`CALCULATION`** estimate: 0.644221 [0.634187, 0.65413] (95% wilson-score, n=8851, half-width 0.009972)
- trials: requested 8851, completed 8851, failed 0

## Statistical uncertainty

Pre-declared target: **proportion**, half-width ≤ 0.01 at 95% confidence.

`detection_probability` convergence — half-width 0.03139 at n=885 → 0.009972 at n=8851.

**`LIMITATION`** These intervals describe sampling precision under the stated assumptions only. They do not establish that the modelled system is the right one, and a satisfied precision target is not a validated result.

## Failures

None recorded for this run.

## Deviations from preregistration

None recorded. Specification hash `00255c940ca336d1…` matches the pre-registered content.

## Evidence classification

AURA separates what the system measured from what a researcher inferred. The two are never rendered in the same section.

### What the system measured

- **`CALCULATION`** `absolute_error_vs_closed_form` = {'value': 0.0054609606659722365, 'closed_form': 0.6387600313123353, 'monte_carlo': 0.6442209919783075, 'interval_covers_closed_form': True}
- **`CALCULATION`** `detection_probability` = 0.644221 [0.634187, 0.65413] (95% wilson-score, n=8851, half-width 0.009972)

### What the researcher inferred

- **`INTERPRETATION`** The Monte Carlo estimate agreeing with the closed form to within the declared precision, with the interval covering the exact value, is consistent with the seeding, aggregation and interval machinery being correct. It is a check of the framework, not evidence about any physical system.
- **`LIMITATION`** One deflection value at one threshold. Agreement here does not establish that the estimators are correct across their whole domain.
- **`ASSUMPTION`** Bit-identical repeat execution is asserted for this deterministic-seed configuration on this platform; cross-platform bitwise identity of floating-point sampling is not claimed.

**Editorial problems detected:**
- statement set contains no measured evidence (FACT/CALCULATION/OBSERVATION) — this is commentary, not a result

## What the evidence supports

Under the assumptions listed above, and at the stated precision:

- **`CALCULATION`** `detection_probability` was measured as 0.644221 [0.634187, 0.65413] (95% wilson-score, n=8851, half-width 0.009972)

**`LIMITATION`** These are measurements, not conclusions. Whether they support the hypothesis is an interpretation, and appears only where a researcher has supplied one.

## What the evidence does not support

- Any claim beyond the declared validity envelope of the model.
- Any claim about a system, condition or fault not present in this configuration.
- Any causal claim: this experiment measures association under a fixed design.

## Limitations

- **`LIMITATION`** A demonstration of infrastructure. It supports no aerospace claim.
- **`LIMITATION`** Reproducibility was verified within a single process on one platform.
- **`LIMITATION`** The working tree was dirty at execution time, so the recorded commit alone does not reproduce this run.

## Reproducibility information

To reproduce this run:

```bash
python -m aura run DEMO-0001
```

Provenance chain for any reported metric:

1. result: <metric>
2. experiment: DEMO-0001 (run 98c047b361ef55d9)
3. specification: experiments/DEMO-0001/spec.yaml sha256=00255c940ca336d1
4. configuration[specification]: sha256=f5c680578b51c768
5. dataset: DS-DEMO-0001 @ 1.0
6. model: threshold-detector @ 1.0
7. code: ce8a9a6368984318ef382555c92cefe45b5dfd2b (dirty) framework=0.8.0
8. seed: base=20260908 labels=['deflection', 'threshold', 'trial']

## Final decision

**`COMPLETED`** — the run was valid and achieved its declared precision. What it implies for the hypothesis is a researcher judgement and is not generated automatically; see *What the researcher inferred*.

