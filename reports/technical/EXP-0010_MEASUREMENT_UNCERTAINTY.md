# EXP-0010 — Measurement Uncertainty and Practical Diagnosability

**Experiment:** EXP-0010 · **Date:** 2026-09-08 · **Status:** COMPLETED
**Pre-registration:** [`experiments/EXP-0010/experiment_spec.md`](../../experiments/EXP-0010/experiment_spec.md)
**Results:** `results/validation/EXP-0010/exp0010_results.json` · **Source data:** `DS-0001` (reused, no re-simulation)
**Extends, does not replace:** [EXP-0002](EXP-0002_STRUCTURAL_ISOLABILITY.md)

> **Headline.** At the reference sensor specification, EXP-0002's five-member ambiguity group
> **dissolves completely** — isolation is perfect. But isolation is not *fast*: it takes about 5
> seconds of observation. **The binding constraint on fault isolation in this system is time, not
> noise.** That was not one of the five outcomes the decision gate anticipated.

---

## 1. Research question

> When realistic measurement uncertainty is introduced, which fault hypotheses remain practically
> distinguishable, which become statistically ambiguous, and does the boundary depend meaningfully
> on flight condition?

Sub-questions: **RQ-A** noise degradation · **RQ-B** ambiguity threshold · **RQ-C** condition dependence.

## 2. Hypotheses

Pre-registered, with no assumption that any answer is yes:

- **EH-A.** Measurement uncertainty reduces distinguishability monotonically.
- **EH-B.** There exists an uncertainty level at which previously distinguishable hypotheses become
  practically indistinguishable.
- **EH-C.** That level depends on flight condition.

## 3. Relationship to EXP-0002 — and a correction to how EXP-0002 must be read

EXP-0002 measured $d_{ij}$, an RMS difference **per channel per sample**. For two known signals in
white Gaussian noise, the Bayes-optimal binary test depends on the *unnormalised* deflection, and the
two are related exactly:

$$d'_{ij} = d_{ij}\sqrt{KN} = d_{ij}\times 153.0 \qquad (K=13,\ N=1801)$$

| EXP-0002 $d_{ij}$ | $d'$ | Optimal $P_e$ at reference noise |
|---|---|---|
| 0.066 (most ambiguous pair) | 10.1 | 2.2 × 10⁻⁷ |
| 1.0 (EXP-0002's threshold τ) | 153 | < 10⁻¹⁶ |

**EXP-0002's τ = 1 was conservative by a factor of ≈ 153.** Its "indistinguishable" pairs are
indistinguishable *per sample*, not to an observer that integrates the window. EXP-0002 declared the
threshold conservative in advance; EXP-0010 quantifies by how much.

**What survives from EXP-0002 is more important than what does not.** Its *ordering* — which pairs
are closest — largely carries over to the statistical setting, though not exactly; §13 tests this
rather than assuming it. Only the binary labels were clearly too pessimistic.

## 4. Experimental design

| | |
|---|---|
| Axes | 4 valid flight conditions × 10 uncertainty levels × 9 observation windows × 18 fault hypotheses |
| Replications | 20 000 per cell → 130 M classification trials |
| New simulation | **None.** DS-0001 reused |
| Runtime | 355 s total, including all validity attacks |
| FC-4 | Not used. Remains invalid (FAIL-0001) |

**Efficiency.** Because the classifier is a quadratic form in Gaussian noise, the Monte Carlo reduces
*exactly* to 18 dimensions rather than 13 × N: with $v_j = w_j - w_i$, correct isolation requires
$z\!\cdot\!v_j < \lVert v_j\rVert^2/2$ for all $j\neq i$, and $u_j = z\!\cdot\!v_j$ is Gaussian with
covariance obtainable from one 18×18 Gram matrix per (condition, window). Verified against direct
full-dimensional simulation (§18, V-C). Cost reduction ≈ 60–70× per trial.

## 5. Noise model

Additive, zero-mean, Gaussian, white, independent across channels and time; per-channel σ from the
EXP-0002 sensor specification; uniform multiplier η; 100 Hz; fixed seed 20261008 with per-cell seeds
derived deterministically.

**σ provenance: synthetic, representative of MEMS-grade instruments. Not from any datasheet and not
a claim about any real sensor.**

Deliberately separated: measurement noise (this model) · sensor bias (fault F1) · sensor drift
(fault F3) · fault magnitude (fixed; swept in V-D) · model uncertainty (**not modelled**; η is used
as its proxy).

### Table 2 — Uncertainty levels

| η | Label |
|---|---|
| 1 | Reference specification — realistic instrument grade |
| 2–5 | Degraded/lower-grade sensors — plausible |
| 10–1000 | **Experimental stress levels.** Not sensor claims. Read as a *total effective uncertainty* multiplier, since model mismatch, turbulence and template error all reduce the deflection identically |

## 6. Fault model

Unchanged from EXP-0002: 18 modes — F0 nominal; bias/scale/drift/stuck on $\{q, a_z, V_t, \alpha\}$;
F6 elevator effectiveness loss. Magnitudes fixed at the EXP-0002 values, swept ×0.5 and ×2 in V-D.

## 7. Flight conditions

### Table 1

| ID | Alt | $V_t$ | $\bar q$ | trim α |
|---|---|---|---|---|
| FC-1 | 1000 m | 45 m/s | 1126 Pa | −0.88° |
| FC-2 | 1000 m | 28 m/s | 436 Pa | 5.15° |
| FC-3 | 5000 m | 35 m/s | 451 Pa | 4.83° |
| FC-5 | 5000 m | 28 m/s | 289 Pa | 10.15° |

## 8. Statistical methodology & 9. Primary metric

**Primary: $P_{\text{iso}}$** — probability of correct 18-way isolation under the Bayes-optimal
classifier with **known templates** and known noise, equal priors.

**This is an upper bound on any real diagnoser** and is reported as such everywhere. No real system
knows the fault templates exactly.

**Secondary:** closed-form pairwise $P_{\text{disc}} = \Phi(d'/2\eta)$; detection $P_{\text{det}}$
and false alarm $P_{\text{FA}}$, kept strictly separate from isolation.

**Practical ambiguity** is read at $P_{\text{disc}} < 0.95$ — a reading aid on a continuous surface,
not a claim that a sharp threshold exists.

## 10. Monte Carlo methodology

N = 20 000 per cell, justified in advance: binomial SE at the worst case $P=0.5$ is 0.0035, giving a
95% CI half-width of ±0.007. Realised CIs on headline numbers: ±0.003 to ±0.006. Verified stable
across five seeds (range 0.0011).

---

## 11. Results

### Table 4 — Main result: $P_{\text{iso}}$ at the full 18 s window

| η | FC-1 | FC-2 | FC-3 | FC-5 |
|---|---|---|---|---|
| **1** (reference) | **1.000** | **1.000** | **1.000** | **1.000** |
| 2 | 0.999 | 1.000 | 1.000 | 1.000 |
| 5 | 0.982 | 0.997 | 0.997 | 0.996 |
| 10 | 0.952 | 0.980 | 0.981 | 0.979 |
| 20 | 0.898 | 0.930 | 0.934 | 0.947 |
| 50 | 0.803 | 0.837 | 0.839 | 0.854 |
| 100 | 0.653 | 0.686 | 0.695 | 0.696 |
| 200 | 0.431 | 0.419 | 0.433 | 0.429 |
| 1000 | 0.118 | 0.109 | 0.112 | 0.110 |

**At the reference specification, isolation is perfect and there are zero practically ambiguous
pairs at every condition.**

### Time to isolation (FC-1)

| Window | η=1 | η=10 | η=50 | η=200 |
|---|---|---|---|---|
| 0.05 s | 0.452 | 0.302 | 0.108 | 0.067 |
| 0.5 s | 0.559 | 0.417 | 0.218 | 0.091 |
| 2 s | 0.701 | 0.503 | 0.331 | 0.132 |
| 5 s | 0.997 | 0.859 | 0.540 | 0.229 |
| 18 s | 1.000 | 0.952 | 0.803 | 0.431 |

**Even with perfect sensors, $P_{\text{iso}} = 0.45$ at 0.05 s and does not reach 0.95 until ≈ 5 s.**

### Detection versus isolation

At η = 1: $P_{\text{det}} = 1.000$, $P_{\text{FA}} = 0.000$. At η = 50: $P_{\text{det}} = 0.98$ but
$P_{\text{iso}} = 0.80$ — **and $P_{\text{FA}} = 0.89$**. Under elevated uncertainty the maximum-
likelihood rule with equal priors declares *some* fault in 89% of nominal cases while still
"detecting" faults 98% of the time. High detection performance conceals unusable isolation and an
unusable false-alarm rate. The two must not be conflated.

## 12. Comparison with EXP-0002

| | EXP-0002 | EXP-0010 |
|---|---|---|
| Most ambiguous pair | $d=0.066$, labelled indistinguishable | $P_{\text{disc}} > 1-10^{-7}$ at η=1 |
| Ambiguous pairs at reference noise | 10–11 of 153 | **0 of 153** |
| Ambiguity ordering | F0/F2_α closest, then F0/F2_q, F2_q/F2_α, F0/F4_α | **Identical ordering** |

EXP-0002's structure is confirmed; its binary labels are superseded.

## 13. The five-member ambiguity group under noise

EXP-0002 identified {F0, F2_q, F2_α, F4_α, F4_Vt} with **no noise model at all**. Ranking the 18
faults by per-fault $P_{\text{iso}}$ at FC-1:

| η | Five hardest faults, in order |
|---|---|
| 10 | **F0 (0.62), F2_α (0.64), F2_q (0.89), F4_α (0.98), F4_Vt (1.00)** |
| 50 | **F0 (0.11), F2_α (0.24), F2_q (0.40), F4_α (0.53), F4_Vt (0.65)** |

**The five hardest faults are exactly the five-member group, at both stress levels** (FIG-005). Of
the first 3 pairs to become practically ambiguous (η=10), 3 of 3 lie inside the group; at η=50, 10 of
11 do.

**Answering the brief's five options directly:** noise (2) *expands* the group beyond five members
only at η ≥ 100; below that it (1) leaves the group essentially unchanged while converting it from a
binary label into (5) a probabilistic, graded ambiguity. It does not contract it or reorder it.

### Is this circular? A direct test, because the concern is legitimate

$P_{	ext{iso}}$ is a monotone function of the same distances EXP-0002 measured, so "the group with
the smallest distances degrades first" risks being an arithmetic identity rather than a finding. This
was tested rather than argued.

Ranking the 18 faults by per-fault $P_{	ext{iso}}$ and, separately, by nearest-neighbour
deterministic distance $\min_j d_{ij}$ (full results:
`results/validation/EXP-0010/circularity_test.json`):

| η | Spearman(rank by $P_{	ext{iso}}$, rank by $\min_j d_{ij}$) | Faults whose rank differs | Largest rank shift |
|---|---|---|---|
| 10 | 0.767 | 9 of 18 | **10 positions** (F6) |
| 50 | 0.981 | 9 of 18 | 2 positions |
| 200 | 0.942 | 8 of 18 | 5 positions |

And the *number* of close neighbours carries information beyond the nearest one:
corr($P_{	ext{iso}}$, $\min_j d_{ij}$) = +0.636, corr($P_{	ext{iso}}$, #neighbours with $d<3$) =
−0.470, while the two predictors are themselves correlated only at −0.775.

**Honest verdict: substantially implied, not identical.** The claim must be stated more weakly than
it first appeared. What is genuinely non-trivial is that the mapping from pairwise deterministic
distance to *many-hypothesis* statistical performance **stays monotone** — which was not guaranteed,
since a fault with several moderately close neighbours can be harder to isolate than one with a
single very close neighbour, and F6 shifts by ten rank positions for exactly that reason.

**Revised claim.** Deterministic distinguishability analysis is a *useful screening tool* — it
identifies roughly the right hard set at a fraction of the cost — but it is not a substitute for the
statistical analysis, and it does not predict the uncertainty level at which the group emerges
(η ≈ 10), which was not derivable from EXP-0002.

## 14. Analytical prediction test

EXP-0002 predicted in closed form that a bias fault and a scale fault on a regulated channel coincide
at $V^{*} = b/(k-1) = 50$ m/s. **The prediction was not refitted.**

| Condition | $V_0$ | η₉₅ predicted | η₉₅ measured | ratio |
|---|---|---|---|---|
| FC-1 | 45 m/s | 12.9 | 26.4 | 2.05 |
| FC-3 | 35 m/s | 38.7 | 58.7 | 1.52 |
| FC-2 | 28 m/s | 56.8 | 79.9 | 1.41 |
| FC-5 | 28 m/s | 56.8 | 69.3 | 1.22 |

**Pearson r = 0.979.** The closed form, which uses only the $V_t$ channel, correctly ranks the
conditions and predicts the scale to within a factor of 1.2–2.1; it is *conservative* because the
other twelve channels also carry information.

**Answer to the brief's question:** yes — the analytical model correctly predicts *where* practical
discrimination becomes difficult, though it under-states *how much* uncertainty is tolerable.

## 15. Flight-condition analysis

### η at which $P_{\text{iso}}$ falls to 0.95

| Window | FC-1 | FC-2 | FC-3 | FC-5 | spread |
|---|---|---|---|---|---|
| 5 s | 3.9 | 6.0 | 6.0 | 6.2 | 1.59× |
| 10 s | 9.0 | 13.0 | 13.1 | 14.3 | 1.60× |
| 18 s | 10.2 | 15.1 | 15.7 | 18.7 | **1.83×** |

**Ordering FC-1 < FC-2 ≈ FC-3 < FC-5 at every window** — and preserved at every fault magnitude
(§17). FC-1 (highest dynamic pressure, lowest trim α) is consistently the *worst* condition for
isolation, FC-5 (lowest $\bar q$, highest α) the best.

But at $P_{\text{iso}} = 0.50$ the limits are 161, 162, 167, 166 — a spread of **1.04×**.

**Condition dependence is real, modest (≤1.8×), robust — and confined to the high-reliability
regime.** Where isolation collapses entirely, flight condition does not matter. The answer to RQ-C is
therefore *yes, but only where it matters for reliability, and by less than a factor of two*.

## 16. Time-to-isolation analysis

At η = 1, the window at which $P_{\text{iso}}$ first reaches 0.95 is **5 s at every condition**. At
η = 10 it is 18 s for FC-1 and 10 s for the others. At η ≥ 20 it is never reached within 18 s.

At the reference specification, the entire range of $P_{\text{iso}}$ across all ten uncertainty
levels at the full window is 0.118–1.000, while across windows at η=1 it is 0.452–1.000. **In the
realistic uncertainty range (η ≤ 5), the window is the only variable that matters** — η changes
$P_{\text{iso}}$ by less than 0.02, while window changes it by 0.55.

Isolation here is **delayed, then persistent**: poor for the first ~1 s, rising sharply between 2 s
and 5 s as the excitation doublet (4–10 s) is observed, and complete thereafter. Isolation depends on
*observing the manoeuvre*, not merely on elapsed time — the 2→5 s jump coincides with the doublet.

## 17. Sensitivity analysis

### Table 5

| ID | Attack | Result | Verdict |
|---|---|---|---|
| V-A | Alternative seed base | max \|Δ$P_{\text{iso}}$\| = 0.0007 across all conditions | **Not seed-dependent** |
| V-B | Student-t(ν=4), matched variance | Indistinguishable from Gaussian (Δ ≤ 0.01) | **Robust to heavy tails** |
| V-B | AR(1), ρ = 0.5 | **21% mean relative loss** in $P_{\text{iso}}$ | **Materially worse — see below** |
| V-C | Gram reduction vs direct full-dimensional simulation | Agreement within MC error at every cell | **Efficient method is exact** |
| V-D | Fault magnitude ×0.5 / ×2 | η₉₅ = 5.4/10.0/10.0/12.4 and 15.0/22.0/23.1/23.6; **condition ordering preserved at every magnitude** | **Not a magnitude artefact** |
| V-E | Observation window | Built into the primary design (§16) | Longer observation *does* dissolve ambiguity |
| V-F | Recomputed $d_{ij}$ vs EXP-0002 | max abs difference 5.0 × 10⁻¹⁰ | **Same data, consistent pipeline** |

### The temporally-correlated-noise result, explained rather than just reported

AR(1) noise with ρ = 0.5 reduces the effective number of independent samples by
$(1+\rho)/(1-\rho) = 3$, so the deflection should fall by $\sqrt{3} = 1.732$ — i.e. AR(1) at η should
behave like white noise at $1.732\,\eta$. Testing that prediction against all twelve measured cells:

**mean |observed − predicted| = 0.0048, Pearson r = 0.9993.**

The white-noise assumption is therefore optimistic by a *predictable* factor, not an unknown one.
This is a limitation with a correction, which is more useful than a limitation without one.

## 18. Validity attacks — what could still be wrong

- **The classifier knows the templates exactly.** This is the largest unaddressed optimism, and it
  is structural, not incidental. Template error acts exactly like elevated η, so **the realistic
  operating regime may be η ≥ 10 rather than η = 1.** Untested.
- **Fault magnitude is known.** If magnitude were free, F1 and F2 on the same channel would overlap
  by construction (that is what $V^*$ means). Hypothesis classes would then genuinely intersect.
  Untested and probably the dominant real source of ambiguity.
- **TV-D10** — one self-implemented aircraft with experimenter-chosen parameters.
- One excitation profile; §16 shows isolation depends on observing it.
- Equal priors; real fault priors are far from uniform.

## 19. Findings

### Observed
1. At the reference sensor specification, $P_{\text{iso}} = 1.000$ and there are **zero** practically
   ambiguous pairs at all four valid conditions.
2. $P_{\text{iso}}$ reaches 0.95 only after ≈ 5 s of observation, even with perfect sensors.
3. The five faults hardest to isolate are exactly EXP-0002's five-member group at both stress levels —
   though the rank correlation between statistical difficulty and deterministic nearest-neighbour
   distance is 0.77–0.98, not 1.0, so this is substantially (not entirely) implied by the metric.
4. η₉₅ varies by up to 1.83× across conditions with a fixed ordering; η₅₀ varies by 1.04×.
5. The closed-form bias/scale prediction ranks conditions correctly under noise (r = 0.979).
6. AR(1) noise costs 21% of $P_{\text{iso}}$, quantitatively explained by $\sqrt{3}$ (r = 0.9993).
7. Under elevated uncertainty, detection stays high (0.98) while the false-alarm rate becomes
   unusable (0.89).

### Inferred
- Ambiguity in this system at realistic noise is **temporal**, not statistical.
- Deterministic distinguishability analysis is a useful *screening* tool — it identifies roughly the
  right hard set cheaply — but it does not predict the uncertainty level at which ambiguity emerges,
  and its ranking is not identical to the statistical one.
- The argmax rule is a poor decision rule under uncertainty, independently of how uncertainty is
  represented.

### Speculative
- If template error is included, the effective regime may sit at η ≥ 10, where ambiguity is real and
  condition-dependent. This would restore the original motivation — but it is a hypothesis.
- Unknown fault magnitude may dominate every effect measured here.

## 20. Limitations

1. Known templates → every probability is an **upper bound**.
2. Known fault magnitude → composite-hypothesis ambiguity not measured.
3. Model uncertainty not modelled; η used as a proxy.
4. White noise is the primary model; correlated noise costs a further 21%.
5. One self-implemented aircraft (TV-D10, HIGH, unmitigated).
6. One excitation, one sensor suite, equal priors.
7. Nothing here concerns real sensors, real aircraft, safer autonomy, improved reliability, or
   operational applicability. **No such claim is made.**

## 21. Threats to validity

Carried forward: TV-N1 (novelty unverified), TV-D1 (simulation bias), TV-D9/TV-D10 (single,
self-implemented airframe). **New:** the known-template and known-magnitude assumptions, which
together make $P_{\text{iso}}$ an upper bound of unknown tightness. Recorded as **TV-M5**.

## 22. Decision gate

| Outcome | Verdict |
|---|---|
| **A — noise primarily scales separation** | **SUPPORTED, dominant.** The ambiguity ordering is preserved exactly; noise reduces margins without restructuring the problem until η ≥ 100 |
| **B — noise creates new ambiguity at realistic levels** | **NOT SUPPORTED.** At η ≤ 5, $P_{\text{iso}} \geq 0.982$ and zero pairs are ambiguous. New ambiguity requires stress levels |
| **C — noise interacts strongly with flight condition** | **PARTIALLY SUPPORTED.** Real, robust, ordered — but ≤1.83×, and only in the high-reliability regime. "Strongly" would overstate it |
| **D — dominated by modelling assumptions** | **PARTIALLY.** The white-noise assumption is optimistic by a predictable factor; the known-template assumption is unquantified. Conclusions are not *dominated*, but they are bounded |
| **E — mixed across fault classes** | **SUPPORTED.** Five faults degrade early; thirteen remain isolable to η ≈ 100 |

### A finding outside the pre-declared categories

**The binding constraint on isolation is the observation window, not the uncertainty level.** None of
A–E anticipated this. At realistic noise the entire isolation problem is *temporal*: the aircraft
cannot know which fault it has for several seconds, regardless of sensor quality.

## 23. Implications for AURA

**This result weakens the original motivation in one respect and relocates it in another. Both should
be stated plainly.**

1. **The case for uncertainty-aware *isolation* at realistic sensor noise is weak in this
   configuration.** With good sensors, known templates and enough time, there is nothing to be
   uncertain about — $P_{\text{iso}} = 1.000$. AURA cannot justify itself on sensor noise alone.
2. **The case relocates to the transient.** For roughly the first 5 seconds after onset the aircraft
   genuinely cannot isolate the fault, and this is *irreducible* — not a sensor limitation. An
   autonomous system must act during that window. **"What do I do before isolation is possible?" is
   a better-grounded research question than "which fault is it?"**, and it is measured, not assumed.
3. **The argmax rule fails badly under uncertainty** ($P_{\text{FA}} = 0.89$ at η = 50). That is a
   concrete argument for a decision layer that does not simply take the most likely hypothesis —
   though it argues for *decision rules*, not specifically for AURA's two-component representation.
4. **Deterministic analysis is useful for screening, with a caveat now measured.** It identifies
   approximately the right hard set cheaply (rank correlation 0.77–0.98), but the correspondence is
   not exact and it cannot predict the uncertainty level at which ambiguity appears. It guides
   expensive statistical work; it does not replace it.
5. **A-UNC-03's reference stands.** Response-based distinguishability does predict practical
   diagnosability — the mapping is monotone and the ordering is preserved.

**What AURA may not now claim:** that measurement noise creates diagnostic ambiguity at realistic
sensor quality. On this evidence, it does not.

## 24. Recommended next experiment

**EXP-0011 — isolation with *unknown fault magnitude* (composite hypotheses).**

Rationale: it is the largest untested assumption and the most likely dominant source of real
ambiguity. When magnitude is free, F1 and F2 on the same channel intersect exactly at $V^*$ — the
closed form already proves the classes overlap. This converts a point-hypothesis test into a
composite one and can only *increase* ambiguity. It reuses the same machinery and requires no new
simulation beyond a magnitude grid.

**Second priority: EXP-0012 — the transient window.** Characterise what is knowable in the first
5 seconds, since §16 shows that is where the real problem lives.

**Explicitly not recommended next:** any learning component, uncertainty estimator or decision layer.
EXP-0010 has just shown that the motivating ambiguity is absent at realistic noise with known
templates. Building the architecture now would be building it on the weakest version of its own case.
