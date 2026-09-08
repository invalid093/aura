# DEMO-0002 — Deliberately invalid run - operating point outside the model validity envelope

**Status:** `INVALID` · **Kind:** infrastructure · **Gates:** `INVALID` · **Run:** `020a13c34997fcfb` · **Generated:** 2026-09-08T15:07:48.624855+00:00

> ### No scientific conclusion is emitted for this experiment.
> The run finished with status `INVALID` and overall gate outcome `INVALID`. Its numbers are recorded below as evidence of *what the run did*, not as evidence about the research question. Interpreting them would mean drawing a conclusion from a run the framework rejected.

---

## Research question

Does AURA automatically reject an experiment whose operating point lies outside the declared validity envelope of its model, even when the resulting numbers look good?

## Hypothesis

At a deflection of 9.0 the detection probability is estimable by Monte Carlo to the same declared precision as at any other operating point.

## Prediction

Pre-registered before execution:

> The estimate will approach 1.0 and appear excellent. That apparent quality is exactly the hazard: the run is outside the envelope in which the model means anything, so AURA must reject it despite the attractive numbers.

## Experimental design

| Role | Variable | Value |
|---|---|---|
| independent | `deflection` | 9.0 |
| dependent | `detection_probability` | measured |
| controlled | `estimator` | proportion |
| controlled | `noise_variance` | 1.0 |
| controlled | `threshold` | 1.6448536269514722 |

## Assumptions

The results below are conditional on every one of these.

- **`ASSUMPTION`** Trials are independent and identically distributed.
- **`ASSUMPTION`** The detector statistic is exactly Gaussian with unit variance.
- **`ASSUMPTION`** DELIBERATE DEFECT: this specification asserts that a deflection of 9.0 is a legitimate operating point for the threshold-detector model. It is not. The model's declared validity envelope is [0.0, 6.0], and this experiment exists to demonstrate that AURA rejects the run automatically rather than relying on a reviewer to notice.

## Configuration

| Item | Value |
|---|---|
| model | `threshold-detector` @ `1.0` |
| validity envelope `deflection` | [0.0, 6.0] |
| dataset (output) | `DS-DEMO-0002` @ `1.0` |
| config `specification` | `sha256:006770c695a41bd7…` |
| seed policy | base `20260908` over `['deflection', 'threshold', 'trial']` |

## Validation gates

| Gate | Phase | Outcome | Detail |
|---|---|---|---|
| `provenance_complete` | PREFLIGHT | ✅ **PASS** | provenance chain complete (WARNING: working tree dirty; commit alone does not reproduce this run) |
| `seed_policy_declared` | PREFLIGHT | ✅ **PASS** | seeds derived from base 20260908 over ['deflection', 'threshold', 'trial'] |
| `model_validity_envelope` | RUNTIME | ❌ **INVALID** | 1 envelope violation(s); results must not be interpreted |
| `numerical_validity` | RUNTIME | ✅ **PASS** | no non-finite values; timing self-consistent |
| `data_completeness` | POST | ✅ **PASS** | all 9604 trials recorded |
| `statistical_precision` | STATISTICAL | ✅ **PASS** | achieved half-width 0.00019991 vs target 0.01 at 95% confidence (required N 9604, actual N 9604) |
| `convergence` | STATISTICAL | ✅ **PASS** | half-width changed 10.0% over the final checkpoint |

**Overall: `INVALID`**

## Execution

| Item | Value |
|---|---|
| started (UTC) | 2026-09-08T15:07:48.296749+00:00 |
| finished (UTC) | 2026-09-08T15:07:48.624855+00:00 |
| runtime (s) | 0.183748 |
| code | `ce8a9a636898` **(dirty tree)** |
| framework | `0.8.0` |
| python | 3.13.15 on Windows/AMD64 |
| numpy | 2.5.2 |

## Results

### `closed_form_reference`

- **`CALCULATION`** value: `{'value': 0.9999999999999046, 'note': 'Computed for completeness. Outside the declared envelope this comparison is not informative: both numbers saturate at 1.'}`

### `detection_probability`

- **`CALCULATION`** estimate: 1 [0.9996, 1] (95% wilson-score, n=9604, half-width 0.0001999)
- trials: requested 9604, completed 9604, failed 0

## Statistical uncertainty

Pre-declared target: **proportion**, half-width ≤ 0.01 at 95% confidence.

`detection_probability` convergence — half-width 0.001993 at n=960 → 0.0001999 at n=9604.

**`LIMITATION`** These intervals describe sampling precision under the stated assumptions only. They do not establish that the modelled system is the right one, and a satisfied precision target is not a validated result.

## Failures

None recorded for this run.

## Deviations from preregistration

None recorded. Specification hash `5f13ae592837b44b…` matches the pre-registered content.

## Evidence classification

AURA separates what the system measured from what a researcher inferred. The two are never rendered in the same section.

### What the system measured

- **`CALCULATION`** `closed_form_reference` = {'value': 0.9999999999999046, 'note': 'Computed for completeness. Outside the declared envelope this comparison is not informative: both numbers saturate at 1.'}
- **`CALCULATION`** `detection_probability` = 1 [0.9996, 1] (95% wilson-score, n=9604, half-width 0.0001999)

### What the researcher inferred

- **`INTERPRETATION`** If AURA is working, this run is marked INVALID and no conclusion is drawn from it — despite an estimate that looks essentially perfect. An apparently excellent result from outside the validity envelope is the most dangerous kind, because nothing about the number itself signals the problem.

**Editorial problems detected:**
- statement set contains no measured evidence (FACT/CALCULATION/OBSERVATION) — this is commentary, not a result

## What the evidence supports

**Nothing.** The gates rejected this run, so it supports no claim about the research question. This section is deliberately empty rather than omitted, so that its emptiness is visible.

## What the evidence does not support

- Any claim beyond the declared validity envelope of the model.
- Any claim about a system, condition or fault not present in this configuration.
- Any causal claim: this experiment measures association under a fixed design.

## Limitations

- **`LIMITATION`** The operating point is outside the model's declared validity envelope, so no number produced by this run describes anything the model represents.
- **`LIMITATION`** The working tree was dirty at execution time, so the recorded commit alone does not reproduce this run.

## Reproducibility information

To reproduce this run:

```bash
python -m aura run DEMO-0002
```

Provenance chain for any reported metric:

1. result: <metric>
2. experiment: DEMO-0002 (run 020a13c34997fcfb)
3. specification: experiments/DEMO-0002/spec.yaml sha256=5f13ae592837b44b
4. configuration[specification]: sha256=006770c695a41bd7
5. dataset: DS-DEMO-0002 @ 1.0
6. model: threshold-detector @ 1.0
7. code: ce8a9a6368984318ef382555c92cefe45b5dfd2b (dirty) framework=0.8.0
8. seed: base=20260908 labels=['deflection', 'threshold', 'trial']

## Final decision

**`INVALID` — no scientific conclusion.** Overall gate outcome `INVALID`. The correct next action is to address the gate failure recorded above, not to reinterpret these numbers.

