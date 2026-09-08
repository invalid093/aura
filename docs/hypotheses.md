# AURA — Hypotheses and Falsification Criteria

**Status:** PRE-REGISTERED (Phase 0). Not yet tested.
**Date:** 2026-09-08
**Binding rule:** These hypotheses, their thresholds, and their falsification criteria are fixed
*before* any confirmatory experiment is run. Changing them after seeing test-set results is
prohibited (`CLAUDE.md`). Changes require an ADR and invalidate any confirmatory result that
depended on the old version.

Notation: $A$ = evidential ambiguity, $N$ = competence loss (novelty), both defined in
`docs/research_question.md`.

---

## H1 — Decision quality (primary)

**Statement.** Under combined flight-regime and fault distribution shift, a decision policy over
the two-component representation $(A, N)$ achieves **lower expected decision cost at matched
autonomy coverage** than the best single-scalar confidence gate.

**Primary metric.** Expected decision cost $\mathbb{E}[C]$ under the cost model in
`reports/phase0/EXPERIMENTAL_DESIGN_PRELIMINARY.md` §6, evaluated on the frozen test set,
at coverage matched to within ±1 percentage point.

**Supported if.** $\mathbb{E}[C]_{\text{AURA}} < \mathbb{E}[C]_{\text{best baseline}}$ with a 95%
bias-corrected bootstrap CI on the paired difference excluding zero, over ≥1000 bootstrap
resamples at the *scenario* level (not the sample level — see TV-L2).

**FALSIFIED if** either:
- (a) the 95% CI on the paired cost difference contains zero, **or**
- (b) act/abstain/escalate decisions agree with the best scalar baseline at >95% at matched
  coverage — i.e. the LIT-0012 equivalence result reproduces.

**Prior belief.** Genuinely uncertain. LIT-0012 is direct evidence *against* H1. The stated reason
AURA might differ ($A$ and $N$ read structurally different evidence) is an argument, not a result.
**A negative outcome here is a publishable finding and is not a project failure.**

---

## H2 — Identifiability of the decomposition

**Statement.** $A$ and $N$ are empirically separable rather than two monotone functions of one
latent scalar.

**Metrics.**
1. Spearman $\rho(A, N)$ across the test set.
2. $\rho(A, \text{structural ambiguity})$ vs $\rho(N, \text{structural ambiguity})$, where
   structural ambiguity is the size of the true ambiguity group from the isolability matrix at the
   scenario's flight condition.
3. $\rho(N, \text{true shift magnitude})$ vs $\rho(A, \text{true shift magnitude})$.

**Supported if.** $|\rho(A,N)| < 0.6$ **and** $A$ tracks structural ambiguity strictly better than
$N$ does **and** $N$ tracks shift magnitude strictly better than $A$ does (each with
non-overlapping 95% bootstrap CIs).

**FALSIFIED if** $|\rho(A,N)| \ge 0.6$, or if neither component shows a preferential association
with its intended ground truth.

**Why this matters.** If H2 is falsified, H1 cannot be interpreted even if it is supported — any
cost improvement would then be attributable to having two thresholds instead of one, not to the
decomposition. **H2 is therefore a gate on H1's interpretation, and must be evaluated first.**

---

## H3 — Shift/fault confounding (the LIT-0004 limitation, quantified)

**Statement.** As regime-shift magnitude increases, novelty-gated diagnosis increasingly suppresses
genuine fault detections; there exists a shift magnitude beyond which novelty gating is net-harmful.

**Metric.** Missed-detection rate as a function of shift magnitude $s$, at fixed false-alarm rate,
under a novelty gate; compared against the same detector with the gate disabled.

**Supported if.** $\text{MDR}_{\text{gated}}(s) - \text{MDR}_{\text{ungated}}(s)$ increases
monotonically in $s$ over the tested range (Spearman $\rho > 0.7$, $p < 0.05$), and there exists
$s^*$ within the tested range at which the gated policy's expected cost exceeds the ungated
policy's.

**FALSIFIED if** the difference is flat or non-monotonic in $s$, or no crossover $s^*$ exists
within the tested range.

**Note.** H3 is the hypothesis most likely to yield a clean, useful result regardless of H1, because
it measures a quantity nobody has measured and the mechanism is well-motivated. It is also
**independent of AURA's own method** — it is a property of novelty gating in general.

---

## H4 — Calibration of the classical baseline

**Statement.** The fault posterior produced by a classical multiple-model / Kalman-filter-bank
diagnoser is **overconfident** in-distribution and degrades faster under regime shift than an
ensemble-based learned diagnoser.

**Metric.** Negative log-likelihood and Brier score of the fault posterior (primary, proper scoring
rules); ECE reported as secondary only (LIT-0010, LIT-0011).

**Supported if.** MMAE posterior NLL exceeds ensemble NLL at all shift levels, with the gap
widening monotonically in shift magnitude.

**FALSIFIED if** the MMAE posterior is competitive or better under shift.

**Note.** H4 falsified would be a *more* interesting result than H4 supported: it would say the
classical model-based method the field has largely moved past is in fact the better-calibrated
option under shift, which would directly challenge the value of the learned components.

---

## H5 — Ambiguity-set coverage

**Statement.** When AURA abstains from a point diagnosis and returns a fault set, that set contains
the true fault at least as often as the nominal coverage level, and is smaller than a conformal
prediction set at matched coverage in the in-distribution case.

**FALSIFIED if** empirical coverage falls below nominal under shift by more than the exchangeability
violation would predict, or if set sizes are not smaller than the conformal baseline.

**Note.** Conformal methods lose their guarantee under distribution shift (exchangeability
violation, LIT-0016). Documenting *by how much* is itself useful.

---

## Summary table

| ID | Claim | Primary metric | Falsified if | Prior belief |
|----|-------|----------------|--------------|--------------|
| H1 | Two-component beats scalar on decisions | Expected decision cost at matched coverage | CI contains zero, or >95% decision agreement | Uncertain; evidence against |
| H2 | $A$ and $N$ are separable | $\rho(A,N)$; association with ground truth | $\|\rho\| \ge 0.6$ | Moderately confident yes |
| H3 | Novelty gating suppresses real faults under shift | MDR gap vs shift magnitude | Flat/non-monotonic, no crossover | Confident yes |
| H4 | MMAE posterior is overconfident and degrades fast | NLL / Brier under shift | MMAE competitive under shift | Moderately confident yes |
| H5 | Ambiguity sets have valid coverage | Set coverage and size | Under-coverage beyond prediction | Uncertain |

---

## What would cause AURA to be abandoned

Recorded now, before results exist, so the criterion cannot be softened later:

1. **H2 falsified AND H3 falsified.** If the decomposition is not identifiable *and* the confounding
   effect does not exist, the central premise is wrong. Report the negative result; stop.
2. **A systematic literature search closes G4 and G6** (`research/gaps/GAP_MATRIX.md`). Re-scope.
3. **The pilot shows the diagnosis task is trivially easy or impossible** at the chosen sensor
   suite — e.g. >99% or <20% isolation accuracy in-distribution. Then the experiment cannot
   discriminate between methods and the setup must be redesigned, not the hypothesis.
4. **Structural isolability turns out to be flight-condition-independent** for the chosen model and
   fault set. Then there is no mode-dependent ground truth, and H2's ground truth disappears.
   *This is a real risk and must be checked in EXP-0002, before any learning code is written.*
