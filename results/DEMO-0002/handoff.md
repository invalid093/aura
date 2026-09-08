# HANDOFF — DEMO-0002: Deliberately invalid run - operating point outside the model validity envelope

**This document is self-contained.** It assumes no access to the repository and no memory of the session that produced it. It is written to be attacked.

**Status:** `INVALID` · **Gates:** `INVALID` · **Run:** `020a13c34997fcfb` · **Code:** `ce8a9a636898` (dirty)

---

## ⚠ This experiment produced no scientific conclusion

The run ended `INVALID` with overall gate outcome `INVALID`. The numbers below describe what the run did. They are **not** evidence about the research question, and a reviewer should treat any interpretation of them as unsupported.

## Objective

Does AURA automatically reject an experiment whose operating point lies outside the declared validity envelope of its model, even when the resulting numbers look good?

## Hypothesis

At a deflection of 9.0 the detection probability is estimable by Monte Carlo to the same declared precision as at any other operating point.

## Prediction (pre-registered)

> The estimate will approach 1.0 and appear excellent. That apparent quality is exactly the hazard: the run is outside the envelope in which the model means anything, so AURA must reject it despite the attractive numbers.

## Setup

- **Model:** `threshold-detector` version `1.0`
- **Declared validity envelope:**
  - `deflection` ∈ [0.0, 6.0]
- **Dataset (output):** `DS-DEMO-0002` @ `1.0`
- **Randomisation:** base seed `20260908`, per-cell seeds derived by SHA-256 over `['deflection', 'threshold', 'trial']`; no global RNG state is used.

## Assumptions

Every result below is conditional on these.

- **`ASSUMPTION`** Trials are independent and identically distributed.
- **`ASSUMPTION`** The detector statistic is exactly Gaussian with unit variance.
- **`ASSUMPTION`** DELIBERATE DEFECT: this specification asserts that a deflection of 9.0 is a legitimate operating point for the threshold-detector model. It is not. The model's declared validity envelope is [0.0, 6.0], and this experiment exists to demonstrate that AURA rejects the run automatically rather than relying on a reviewer to notice.

## Methods

| Role | Variable | Value |
|---|---|---|
| independent | `deflection` | 9.0 |
| dependent | `detection_probability` | measured |
| controlled | `estimator` | proportion |
| controlled | `noise_variance` | 1.0 |
| controlled | `threshold` | 1.6448536269514722 |

Metrics: `detection_probability`

## Data

- Specification hash: `sha256:5f13ae592837b44b54d9875e43c7b19e…`
- Configuration hashes: `specification`=`006770c695a4…`
- Environment: python 3.13.15, numpy 2.5.2, Windows/AMD64

## Results

- **`CALCULATION`** `closed_form_reference` = `{'value': 0.9999999999999046, 'note': 'Computed for completeness. Outside the declared envelope this comparison is not informative: both numbers saturate at 1.'}`
- **`CALCULATION`** `detection_probability` = 1 [0.9996, 1] (95%, wilson-score, n=9604); trials completed 9604/9604, failed 0

## Validation gates

| Gate | Phase | Outcome |
|---|---|---|
| `provenance_complete` | PREFLIGHT | **PASS** — provenance chain complete (WARNING: working tree dirty; commit alone does not reproduce this run) |
| `seed_policy_declared` | PREFLIGHT | **PASS** — seeds derived from base 20260908 over ['deflection', 'threshold', 'trial'] |
| `model_validity_envelope` | RUNTIME | **INVALID** — 1 envelope violation(s); results must not be interpreted |
| `numerical_validity` | RUNTIME | **PASS** — no non-finite values; timing self-consistent |
| `data_completeness` | POST | **PASS** — all 9604 trials recorded |
| `statistical_precision` | STATISTICAL | **PASS** — achieved half-width 0.00019991 vs target 0.01 at 95% confidence (required N 9604, actual N 9604) |
| `convergence` | STATISTICAL | **PASS** — half-width changed 10.0% over the final checkpoint |

**Overall: `INVALID`**

## Failures

None recorded for this run.

## Corrections

None recorded.

## Evidence classification

**Measured by the system:**

- `CALCULATION` — `closed_form_reference`
- `CALCULATION` — `detection_probability`

**Inferred by the researcher:**

- **`INTERPRETATION`** If AURA is working, this run is marked INVALID and no conclusion is drawn from it — despite an estimate that looks essentially perfect. An apparently excellent result from outside the validity envelope is the most dangerous kind, because nothing about the number itself signals the problem.

## Limitations

- **`LIMITATION`** The operating point is outside the model's declared validity envelope, so no number produced by this run describes anything the model represents.
- **`LIMITATION`** Working tree was dirty; the recorded commit alone does not reproduce this run.

## Claims that are NOT supported

- Any claim outside the declared validity envelope.
- Any claim of operational, real-aircraft, or safety-critical applicability.
- Any causal claim; the design measures association under fixed conditions.
- **Any claim at all about the research question**: the gates rejected this run.

## Conclusion

`INVALID`. No conclusion is drawn. The framework rejected the run and the correct next action is to address the recorded gate failure.

## Questions for independent review

**What should another researcher try to prove wrong?**

- Is the declared validity envelope actually the right one, or does it merely bound what this configuration happens to produce?
- Is the pre-registered prediction falsifiable as written, or could any outcome be read as consistent with it?
- Does the precision target address the question being asked, or only the one that is cheap to measure?
- Are the assumptions listed above complete — what is being assumed silently?
- Would the same specification, run by someone else from the recorded configuration, produce these numbers?
