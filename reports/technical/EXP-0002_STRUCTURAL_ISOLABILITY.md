# EXP-0002 — Response-Based Fault Distinguishability Across Flight Conditions

**Experiment:** EXP-0002 (gate) · **Date:** 2026-09-08 · **Status:** COMPLETED
**Pre-registration:** [`experiments/EXP-0002/experiment_spec.md`](../../experiments/EXP-0002/experiment_spec.md)
**Results:** `results/validation/EXP-0002/exp0002_results.json` · **Dataset:** `DS-0001`
**Determination: PASS** (on valid conditions; see §22 for the qualifications, which matter)

> **Title note.** The file name retains "STRUCTURAL_ISOLABILITY" for continuity with the Phase 0
> plan. The experiment measures **response-based distinguishability**, which is a different
> quantity. See §6 and [`ADR-0008`](../../docs/decisions/ADR-0008-distinguishability-vs-structural-isolability.md).

---

## 1. Research question

> Do different faults produce distinguishable measured responses, and does the structure of that
> ambiguity change across flight conditions?

This is the ground-truth premise beneath hypothesis H2. If fault distinguishability does not depend
on operating condition, the evidential-ambiguity component $A$ has no condition-dependent reference
and the AURA design must change.

## 2. Experimental hypothesis

**EH-1.** The pairwise distinguishability matrix is neither diagonal nor dense, and its structure
varies across flight conditions.

Prior belief recorded before running: *uncertain, leaning against.* In a deterministic noise-free
simulation where every faulted channel is directly measured, most single sensor faults were expected
to separate, making a near-diagonal outcome a live possibility.

## 3. Experimental definition

| | |
|---|---|
| Independent variables | Flight condition (5 run, 4 valid); fault identity (18) |
| Primary dependent variable | Pairwise normalised RMS response distance $d_{ij}(c)$ (continuous) |
| Derived | Binary matrix at $\tau=1$; ambiguity degree; cross-condition rank correlation and verdict flips |
| Runs | 90 primary + 4 sensitivity sweeps + determinism replay |
| Controlled | Model, parameters, controller and gains (no scheduling), excitation, onset, magnitudes, integration, sampling, no noise, no wind |
| Randomness | **None.** No RNG anywhere in the pipeline |

## 4. Flight conditions

| ID | Alt (m) | $V_t$ (m/s) | $\rho$ | $\bar q$ (Pa) | trim $\alpha$ | trim $\delta_e$ | Validity |
|---|---|---|---|---|---|---|---|
| FC-1 | 1000 | 45 | 1.112 | 1125.5 | −0.88° | −2.01° | **VALID** |
| FC-2 | 1000 | 28 | 1.112 | 435.8 | 5.15° | −6.60° | **VALID** |
| FC-3 | 5000 | 35 | 0.736 | 450.9 | 4.83° | −6.35° | **VALID** |
| FC-4 | 5000 | 24 | 0.736 | 212.0 | 15.92° | −14.78° | **INVALID — FAIL-0001** |
| FC-5 | 5000 | 28 | 0.736 | 288.6 | 10.15° | −10.39° | **VALID** (replacement) |

FC-2/FC-3 are the designed **control pair**: nearly identical dynamic pressure (436 vs 451 Pa) at
different density and airspeed. Their agreement (§13) is what validates the metric.

Excitation, identical at every condition: pitch-attitude doublet, ±3°, on [4,7) and [7,10) s.

## 5. Fault definitions

18 modes: `F0` nominal; `F1` bias (10σ), `F2` scale (×1.10), `F3` drift (→10σ), `F4` stuck — each on
$\{q, a_z, V_t, \alpha\}$; `F6` elevator effectiveness loss (λ=0.70). Onset 2.0 s.

All four faulted channels are in the control loop, so every fault propagates into every measurement.

**F5 (increased noise) is excluded**: in a deterministic noise-free simulation its mean response is
identical to nominal *by construction*. Including it would have injected a guaranteed ambiguous pair
that is an artefact of the design, not a property of the aircraft.

## 6. Mathematical definition

$$d_{ij}(c) \;=\; \sqrt{\frac{1}{KN}\sum_{k=1}^{K}\sum_{n=1}^{N}\left(\frac{y_{i,k}(t_n)-y_{j,k}(t_n)}{\sigma_k}\right)^{2}}$$

$K=13$ channels, $N=1801$ post-onset samples at 100 Hz, $\sigma_k$ the **pre-declared** sensor noise
scale. Units: multiples of per-sample per-channel RMS sensor noise. Symmetric, $d_{ii}=0$,
trajectory-based, channel-aggregated by RMS.

Distinguishable iff $d_{ij} > \tau$.

**This is not structural isolability.** Structural isolability is computed from equation incidence
structure and is flight-condition-invariant by construction; the pre-declared gate would have failed
automatically for a definitional reason. Structural isolability remains a valid *outer bound*
(necessary, not sufficient).

## 7. Threshold justification

$\tau = 1.0$, declared a priori: if two fault responses differ by less than the RMS sensor noise per
sample per channel, a single-realisation observer has no consistent signal to separate them.

It is conservative in the direction that makes PASS *harder* on the "not diagonal" criterion, since
a matched filter over 1801 samples could separate well below 1σ.

**Integrity note worth stating plainly:** the pre-declared $\tau=1$ yields the **weakest**
cross-condition binary signal of any threshold tested — 1 verdict flip. At $\tau=3$ there are **38**.
Had the threshold been chosen after seeing results, $\tau=3$ would have been the flattering choice.
The pre-declared value is reported as primary and $\tau=3$ only as sensitivity.

## 8. Configuration

`experiments/EXP-0002/config/exp0002.yaml`, SHA-256 `b4bf7a875270…`. Python 3.13.15, NumPy 2.5.2,
Windows 11 x86-64. RK4 fixed step 0.002 s, zero-order-hold control, float64. Runtime 951 s for the
full experiment including all sweeps; 17.7 MiB of trajectories (git-ignored, regenerable).

## 9. Pilot verification

31 technical checks, all passed: trim convergence (residuals ≤ 5×10⁻¹⁵), physical plausibility of
trim, closed-loop stability, excitation adequacy, fault injection inert before onset and active
after, correct fault magnitudes, F6 not corrupting measurements directly, unit checks, metric
properties ($d_{ii}=0$, symmetry, non-negativity), and bitwise reproducibility.

**The pilot was defective and that defect caused FAIL-0001.** It verified closed-loop boundedness at
**FC-1 only**. Trim convergence was mistaken for flyability. Corrected: a validity gate now runs on
every condition inside the pipeline.

## 10. Full experiment

90 primary runs (5 conditions × 18 faults), all completed, none diverged numerically. Plus: step-size
sweep (3), threshold sweep (7), magnitude sweep (3), duration sweep (2), determinism replay.

## 11. Results — validity gate

| ID | max α | max \|Δθ\| | max \|ΔV\| | max \|Δh\| | Status |
|---|---|---|---|---|---|
| FC-1 | −0.04° | 2.86° | 0.86 m/s | 5.3 m | VALID |
| FC-2 | 6.40° | 2.87° | 0.79 m/s | 2.8 m | VALID |
| FC-3 | 6.13° | 2.76° | 0.78 m/s | 3.5 m | VALID |
| **FC-4** | **31.52°** | **32.47°** | **27.73 m/s** | **353.3 m** | **INVALID** |
| FC-5 | 11.65° | 2.78° | 0.71 m/s | 2.5 m | VALID |

Gate: no divergence, max α < 12°, |Δθ| < 10°, |ΔV| < 3 m/s, |Δh| < 50 m.

## 12. Isolability matrices

At $\tau = 1$, of 153 pairs:

| Condition | Distinguishable | Indistinguishable | $d$ range | Status |
|---|---|---|---|---|
| FC-1 | 142 (92.8%) | 11 | 0.066 – 8.22 | VALID |
| FC-2 | 143 (93.5%) | 10 | 0.129 – 8.23 | VALID |
| FC-3 | 143 (93.5%) | 10 | 0.132 – 8.23 | VALID |
| FC-5 | 143 (93.5%) | 10 | 0.118 – 8.21 | VALID |
| *FC-4* | *153 (100%)* | *0* | *2.05 – 69.8* | *INVALID* |

Full matrices: `results/validation/EXP-0002/binary_matrix_FC-*.txt` and `distance_matrix_FC-*.csv`.
Figures: `FIG-001`, `FIG-002`, `FIG-003`.

### The ambiguity group

The same five-member mutually-indistinguishable group appears at **every valid condition**:

$$\{\,\text{F0},\ \text{F2}\_q,\ \text{F2}\_\alpha,\ \text{F4}\_\alpha,\ \text{F4}\_{V_t}\,\}$$

Composition per condition: **4 pairs versus nominal** (detection ambiguity — the fault is nearly
undetectable) and **6–7 fault-versus-fault pairs** (isolation ambiguity).

**Physical mechanism.** A multiplicative (scale-factor) fault is unobservable when the true signal is
near zero: at FC-1 trim α = −0.88° = −0.0154 rad, so a 10% scale error perturbs α by 0.0015 rad =
0.18σ. Likewise a *stuck* fault is nearly inert on a channel that is already near-constant — α in
trim, and $V_t$ because the autothrottle regulates it. These are textbook observability facts, not
numerical artefacts.

### The condition-dependent pair

`F1_Vt` (bias) versus `F2_Vt` (scale) is indistinguishable **only at FC-1** and is the single binary
verdict flip at $\tau=1$.

## 13. Quantitative summaries

### Cross-condition structure (valid conditions only)

| Pair | Spearman ρ | Binary flips | \|Δα\| | $\bar q$ ratio |
|---|---|---|---|---|
| FC-2 \| FC-3 *(control pair)* | **0.9843** | 0 | 0.33° | 1.03 |
| FC-2 \| FC-5 | 0.9293 | 0 | 4.99° | 1.51 |
| FC-3 \| FC-5 | 0.9224 | 0 | 5.32° | 1.56 |
| FC-1 \| FC-3 | 0.8563 | 1 | 5.71° | 2.50 |
| FC-1 \| FC-2 | 0.8511 | 1 | 6.04° | 2.58 |
| FC-1 \| FC-5 *(extreme pair)* | **0.6577** | 1 | 11.03° | 3.90 |

**The rank correlation is perfectly monotone in operating-point separation — 6 of 6 pairs in order
(Spearman between ρ and |Δα| = −1.000).** The control pair, designed to have nearly identical
dynamic pressure, returns ρ = 0.984 and zero flips; the most separated pair returns ρ = 0.658.

This is the central quantitative result, and it is **threshold-free**.

### Analytic prediction, made independently of the simulation

On a regulated channel with near-constant true value $V_0$, a bias fault ($y = V_0 + b$) and a scale
fault ($y = kV_0$) are identical when $b = (k-1)V_0$, i.e. at

$$V^{*} = \frac{b}{k-1} = \frac{10\sigma_V}{0.10} = \frac{5.0}{0.10} = 50\ \text{m/s}$$

| $V_0$ | Condition | Measured $d$ | Analytic | Verdict at τ=1 |
|---|---|---|---|---|
| 28.0 | FC-2 | 1.719 | 1.220 | distinguishable |
| 28.0 | FC-5 | 1.490 | 1.220 | distinguishable |
| 35.0 | FC-3 | 1.262 | 0.832 | distinguishable |
| 45.0 | FC-1 | 0.568 | 0.277 | **AMBIGUOUS** |

**Pearson correlation between measured and analytically predicted distance: r = 0.979** across four
conditions. The closed form predicts the ordering and trend; it under-predicts magnitude because it
accounts only for the direct $V_t$-channel difference and not for closed-loop propagation into other
channels.

## 14. Sensitivity analysis

| Sweep | Result | Verdict |
|---|---|---|
| **S-A step size** (0.005 / 0.002 / 0.001 s) | Identical pair counts at all conditions; ρ vs base ≥ 0.9992 | **Not solver-dependent** |
| **S-B threshold** (0.1→100) | Valid-condition flips: 1, 3, 1, **38**, 0, 0, 0. Structure exists for τ ∈ [0.1, 3]; at τ ≥ 10 all valid conditions collapse to zero distinguishable pairs | Conclusion survives; **but only over τ ≲ 8, the observed distance range** |
| **S-C magnitude** (×0.5 / ×1 / ×2) | Counts 117–126 / 142–143 / 143–147; min ρ between conditions 0.797 / 0.658 / 0.736; flips 20 / 1 / 4 | **Not an artefact of one magnitude** — condition-dependence persists at every magnitude |
| **S-D duration** (10 / 20 s) | Identical counts and flips | **Not driven by run length** |
| **S-E determinism** | All 90 runs bitwise identical on replay | **Reproducible** |
| Noise sensitivity | **Not run** — no noise is simulated (§6). Stated, not skipped | — |

## 15. FACTS

- Trim converged at all five conditions to residuals ≤ 5×10⁻¹⁵.
- FC-4's nominal run reaches α = 31.52°, |Δθ| = 32.47°, |ΔV| = 27.73 m/s, |Δh| = 353.3 m.
- At τ=1, valid conditions show 142–143 of 153 pairs distinguishable.
- The group {F0, F2_q, F2_α, F4_α, F4_Vt} is mutually indistinguishable at all four valid conditions.
- `F1_Vt`/`F2_Vt` is indistinguishable at FC-1 only.
- All 90 runs are bitwise reproducible.

## 16. CALCULATIONS

- Cross-condition Spearman ρ ranges 0.658–0.984; monotone in |Δα| (rank correlation −1.000).
- $V^{*} = b/(k-1) = 50$ m/s; measured-vs-analytic Pearson r = 0.979.
- 13-channel metric dilutes active-channel distance by $\sqrt{7/13} = 0.734$ (7 channels ever differ
  under longitudinal excitation), i.e. active-channel distances are 1.363× larger. **Uniform across
  all pairs**, so rankings and all cross-condition conclusions are unaffected; only the absolute
  comparison against τ shifts.
- Runtime 951 s; storage 17.7 MiB for 90 runs (compressed).

## 17. OBSERVATIONS

- Ambiguity is dominated by faults that are *weak by construction*: scale errors on near-zero
  signals and stuck faults on near-constant signals.
- Ambiguity is roughly 40% detection-type (versus nominal) and 60% isolation-type (fault versus fault).
- The amount of ambiguity is nearly constant across valid conditions (10–11 pairs); what changes is
  its **composition and ordering**.
- FC-1 and FC-5 have the *same* pair count at τ=3 (87 each) but ρ = 0.658 — same quantity of
  ambiguity, different structure.
- FC-4's apparent "perfect diagnosability" is an artefact of divergence amplification.

## 18. INTERPRETATIONS

*(Our reading; contestable.)*

- Response-based fault distinguishability in this model **does** depend on operating condition, but
  the dependence is **modest at the pre-declared threshold** — one verdict flip in 153 pairs. The
  substantive evidence is the continuous rank structure, not the binary matrix.
- The monotone relationship between ρ and operating-point separation, together with the control
  pair returning 0.98, indicates a real physical effect rather than numerical noise.
- The bias/scale crossover shows condition-dependent ambiguity can be **analytically predictable**.
  For AURA this matters more than the magnitude of the effect: it means the ambiguity component has
  a reference that can be *derived*, not only measured.
- The stable five-member ambiguity group supports a **set-valued diagnostic output**: a system forced
  to name one fault would be guessing among five hypotheses that the data cannot separate.

## 19. HYPOTHESES (suggested, not established)

- Ambiguity structure may depend more strongly on **excitation** than on flight condition. All
  conditions here share one doublet; a different manoeuvre could reorder the matrix more than a
  change of airspeed does. Testable and currently untested.
- With measurement noise, the ambiguity group will **grow**, because faults now separated by
  1 < d < 3 would become unreliable to distinguish from single realisations.
- The near-stall region may show genuinely different structure — FC-4 was intended to probe it and
  could not. A controllable high-α condition would need a controller that can hold trim there.

## 20. LIMITATIONS

1. **Deterministic and noise-free.** Distinguishability is evaluated *before* measurement uncertainty.
   These are upper bounds on what any estimator could achieve.
2. **One self-implemented aircraft (TV-D10).** GFW-1's parameters were chosen by the same person who
   ran the experiment. Reproduction on an independently sourced model is required before this result
   becomes load-bearing.
3. **One excitation.** See §19.
4. **Single magnitude per mechanism** in the primary result (swept in S-C, but the reported matrix is
   one magnitude).
5. **13-channel dilution** (§16) — uniform, but it shifts absolute distances relative to τ.
6. **Correlated channels not decorrelated.** Whitening would need a data-derived covariance, making
   the metric influenceable by results. Consequence: correlated channels contribute partially
   redundant evidence, inflating $d$ somewhat.
7. **The high-α regime is not covered.** FC-5 reaches 11.65°; the intended 15.9° condition was invalid.
8. **No structural isolability computed**, so the outer bound is unverified.

## 21. FAILURES

**FAIL-0001 — `EXPERIMENTAL_INVALIDITY`.** FC-4 departs controlled flight; its matrix is invalid and
excluded. Full record: [`experiments/failures/FAIL-0001.md`](../../experiments/failures/FAIL-0001.md).

Its significance is larger than a lost data point. FC-4 returned the *most favourable-looking*
numbers in the entire experiment — perfect diagonality and ρ = 0.37–0.46 against other conditions,
which would have read as dramatic condition-dependence. **The validity attack turned the headline
result into a discarded artefact**, and with FC-4 removed the evidence is materially weaker.

Two minor defects, both fixed and recorded: the sensitivity step 0.004 s does not divide the 100 Hz
sample interval (corrected to 0.005 s during pilot verification); and the determinism summary line
printed a hard-coded "72 runs" while the check covered all 90 (label only — the check itself was
always complete).

## 22. Pass / fail determination

Against the criteria fixed in the pre-registration, evaluated on **valid conditions only**:

| # | Criterion | Result | Verdict |
|---|---|---|---|
| 1 | Not fully diagonal at every condition | 10–11 ambiguous pairs at each of FC-1/2/3/5 | **PASS** |
| 2 | Not fully dense at every condition | 142–143 of 153 distinguishable | **PASS** |
| 3 | Ambiguity physically motivated | Five-member group with a textbook observability mechanism; bias/scale pair predicted in closed form (r = 0.979) | **PASS** |
| 4 | Structure differs across conditions | ≥1 verdict flip: **yes** (1 pair). Rank correlation materially below 1: **yes** (0.658 minimum, monotone in operating-point separation) | **PASS** |

# EXP-0002: PASS

### Qualifications that a reader should weigh against that verdict

- **The margin on criterion 4 is thin at the pre-declared threshold.** One flip in 153 pairs (0.65%).
  The verdict rests mainly on the continuous rank correlation, which is the stronger and
  threshold-free evidence — but it is a weaker claim than "the matrix restructures".
- **FC-4's exclusion removed what looked like the strongest evidence.** Reporting PASS on the
  remainder is only defensible because the FC-4 result was an artefact, and a reviewer should check
  that judgement independently by re-running the validity scan.
- **Criterion 1 was ambiguously worded** ("not fully diagonal at every condition") and conflicts with
  the corresponding FAIL clause ("fully diagonal at all conditions"). With FC-4 excluded the question
  is moot — all valid conditions have ambiguity, so both readings agree. **Had FC-4 been valid, the
  determination would have depended on which reading was used, and that would have been a defect in
  the pre-registration.** Recorded so it is fixed in future specifications.

## 23. Implications for AURA

**The premise survives, with its scope narrowed.**

1. **H2's ground truth exists but is thinner than assumed.** Ambiguity is real, stable and physically
   explicable, but at realistic thresholds its condition-dependence is a *reordering of magnitudes*
   rather than a wholesale change of which faults are confusable. AURA should not claim the ambiguity
   set changes dramatically with flight condition — on this evidence it does not.
2. **Set-valued output is justified.** A five-member group survives at every condition. A diagnoser
   forced to output one class would be guessing among five hypotheses the data cannot separate.
3. **The ambiguity reference can be *derived*, not just measured.** The bias/scale crossover is a
   closed-form prediction confirmed at r = 0.979. This is stronger than the original plan, which
   relied on a structural matrix that could not have been condition-dependent at all.
4. **The dominant ambiguity mechanism is fault weakness, not fault similarity.** Most ambiguous pairs
   involve faults that barely perturb the aircraft. That points AURA's decision layer toward
   *detectability-aware* abstention as much as isolation-aware abstention.
5. **A-FLT-03 is not yet supported.** The Phase 0 assumption named F2 on `q` and F6 (elevator
   effectiveness) as the flight-condition-dependent ambiguity pair. **They are distinguishable at
   every valid condition**; the pair that actually behaves this way is `F1_Vt`/`F2_Vt`. The
   assumption was wrong in its specifics while right in its general claim.

## 24. Recommended next experiment

**EXP-0010 — the same matrix with measurement noise, over repeated realisations.**

Rationale: the single largest limitation is that this experiment is noise-free, and the most
consequential open question for AURA is how much of the 142/153 "distinguishable" survives when a
diagnoser sees one noisy realisation rather than an exact trajectory. Hypothesis H3 (shift/fault
confounding) cannot be tested without it either.

Deliberately **not** recommended next: any learning component, any uncertainty estimator, any
decision layer. EXP-0002 establishes that the substrate exists; it does not establish that a learned
uncertainty estimate is needed to exploit it, and a simpler baseline may suffice.

Second priority: reproduce the headline cross-condition result on an **independently sourced**
aircraft model, to retire TV-D10.
