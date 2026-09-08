# EXP-0011 — Experiment Specification

**Status:** PRE-REGISTERED. Written and committed **before** any EXP-0011 simulation was run.
**Type:** Extension of EXP-0010. Relaxes its largest assumption.
**Date specified:** 2026-09-08

> §§1–10 are fixed here. Magnitude ranges, knowledge conditions, metrics, thresholds and replication
> counts may not be changed after results are seen.

---

## 1. Question

> **How does fault-isolation performance change when the diagnostic system does not know the
> magnitude of the fault?**

EXP-0010 found essentially perfect isolation at reference sensor noise — but its classifier knew
both the fault templates *and* the fault magnitude. Fault magnitude is treated here as an **unknown
nuisance parameter**, which is a different kind of uncertainty from measurement noise and must not
be conflated with it.

## 2. A closed-form prediction, derived before simulating

On a channel the autothrottle regulates, with magnitude free:

- F1 (bias): $y = V(t) + b$
- F2 (scale): $y = \kappa V(t)$
- difference: $b - (\kappa-1)V(t)$; minimising over $b$ gives $b^\* = (\kappa-1)\overline{V}$
- **residual: $-(\kappa-1)\,(V(t)-\overline{V})$, RMS $= (\kappa-1)\,\mathrm{std}(V)$**

**The two classes separate only by the *fluctuation* of airspeed, not by its mean.** Computed from
the stored nominal trajectories, before running EXP-0011:

| Condition | mean $V$ | std $V$ | per-sample $d$, magnitude **known** | per-sample $d$, magnitude **free** | reduction |
|---|---|---|---|---|---|
| FC-1 | 45.07 | 0.4147 | 0.987 | 0.083 | **11.9×** |
| FC-2 | 28.04 | 0.3778 | 4.392 | 0.076 | **58.1×** |
| FC-3 | 35.05 | 0.3809 | 2.990 | 0.076 | **39.2×** |
| FC-5 | 28.03 | 0.3465 | 4.394 | 0.069 | **63.4×** |

Over the full 18 s window this predicts $d'_{\min} = 2.9$–$3.5$, i.e.
$P(\text{correct discrimination}) = 0.93$–$0.96$ — **not** the ≈1.0 that EXP-0010 reported with
magnitude known.

**And in any window that precedes the excitation doublet (onset 2 s, doublet 4–10 s),
$\mathrm{std}(V) = 0$ exactly in the nominal trajectory, so the predicted separation is zero and
$P = 0.5$ — pure chance.**

**Pre-registered predictions, to be tested and not refitted:**

- **P1.** Unknown magnitude reduces F1_Vt/F2_Vt separation by 12–63× depending on condition.
- **P2.** Over the full window the pair remains separable but no longer near-perfectly:
  $P \approx 0.93$–0.96.
- **P3.** In pre-manoeuvre windows (≤ 2 s) the pair is **indistinguishable regardless of sensor
  quality**; the ambiguity is resolved by *excitation*, not by time or better sensors.
- **P4.** The same mechanism should collapse *any* pair of fault classes whose effect on a
  near-constant channel is an additive constant — so F1 (bias) and F4 (stuck) should also collapse
  on regulated channels.

Measured $d'_{\min}$ will exceed these predictions, because they account only for the direct channel
and ignore closed-loop propagation into the other twelve. The predictions are therefore **lower
bounds**, and the test is whether they rank and scale correctly.

## 3. Hypotheses

- **EH-1.** Allowing magnitude to vary creates cross-class response overlap that does not exist at
  fixed magnitude.
- **EH-2.** There exist fault-class pairs whose overlap **persists** as the observation window grows.
- **EH-3.** Unknown magnitude is a larger source of diagnostic uncertainty than reference sensor noise.

None is assumed true. EH-2 in particular distinguishes *fundamental ambiguity* from *temporary
information insufficiency*, which are different research problems.

## 4. Fault-magnitude model

| Property | Value |
|---|---|
| Nominal magnitudes | As EXP-0002/0010: bias 10σ, scale ×1.10, drift → 10σ, stuck (no magnitude parameter of its own), elevator effectiveness λ = 0.70 |
| Grid | $m/m_{\text{nom}} \in \{0.25, 0.354, 0.5, 0.707, 1, 1.414, 2, 2.828, 4\}$ — 9 levels, $\sqrt2$-spaced |
| Range label | **Experimental range.** Physical bounds for these fault mechanisms are not available, so the range is *not* claimed to be physically calibrated. It is centred on the EXP-0002 nominal and spans a factor of 16 |
| Sign | Positive only. Negative magnitudes are excluded, and this is a **limitation** — a negative bias could intersect a different class |
| Zero | Excluded. At $m \to 0$ every fault converges to nominal and all classes collapse trivially; that is an artefact of the limit, not a diagnostic fact |
| Time variation | Magnitude is constant within a run (drift's time profile is part of its class definition, not its magnitude) |
| Onset | Fixed at 2.0 s, as in EXP-0002/0010 |
| Class-specific ranges | The same relative grid for every class, so no class is given an advantage |

**Detectability floor (pre-declared).** A (class, magnitude) template is *detectable* if
$d'(F(m), F_0) \geq 4.65$ at reference noise over the full window — the deflection giving 99%
detection for the optimal test. **Manifold-overlap results are reported only over detectable
templates**, so that "two faults look alike" cannot be an artefact of both being too small to see.

## 5. Diagnostic knowledge conditions

| Case | The classifier knows | Prior over magnitude |
|---|---|---|
| **A** | The exact magnitude | Point mass at the truth — reproduces EXP-0010 |
| **B** | $m \in [0.5, 2]\,m_{\text{nom}}$ | Uniform over the 5 grid points in that range |
| **C** | $m \in [0.25, 4]\,m_{\text{nom}}$ | Uniform over all 9 grid points |

The true magnitude is drawn uniformly from the grid in every case. Only Case A is told it.

This separates *uncertainty caused by sensors* from *uncertainty caused by not knowing the fault*.

## 6. Guard against an artificially easy classifier

The classifier receives **only** the noisy measurement vector and the declared prior. It does not
receive the true magnitude (except in Case A, which exists precisely as the EXP-0010 control), the
true class, the simulation identifier, or any quantity derived from ground truth. Priors over class
are uniform and stated.

## 7. Diagnostic objective

**Primary: fault-*class* isolation with magnitude marginalised out.** The classifier computes
$p(y \mid \text{class}) = \sum_m p(y \mid \text{class}, m)\,p(m)$ and selects the most likely class.

Magnitude estimation is **secondary** and may not substitute for class isolation.

## 8. Metrics

**Primary — $P_{\text{class}}$:** probability of correct fault-class identification (18 classes),
marginalised over unknown magnitude, by Monte Carlo.

**Secondary 1 — manifold overlap.** For each class pair,
$$D^{\min}_{AB}(c,W) \;=\; \min_{m_A, m_B \in \mathcal{M}_{\text{det}}}\; d'\!\left(y(A,m_A),\, y(B,m_B)\right)$$
the *worst-case-magnitude* (adversarial) separation, with corresponding
$P_{\text{disc}}^{\text{worst}} = \Phi(D^{\min}/2\eta)$.

**Pre-declared overlap bands** (on $P_{\text{disc}}^{\text{worst}}$ at reference noise, full window):

| Band | Range |
|---|---|
| Clearly separated | ≥ 0.99 |
| Partially overlapping | 0.75 – 0.99 |
| Strongly overlapping | 0.55 – 0.75 |
| **Structurally intersecting** | < 0.55 (near chance) |

**Secondary 2 — magnitude estimation error**, reported for completeness.

## 9. Probabilistic interpretation — stated explicitly

Every probability reported is **conditional on**: the GFW-1 model, the fault taxonomy, the declared
magnitude grid and prior, uniform class priors, the Gaussian white noise model, the stated σ, the
observation window, and exact knowledge of the template families. It is a property of *this
inference problem*, not a real-world confidence. It is **not** "the aircraft is 80% sure".

$P_{\text{class}}$ remains an **upper bound** on any real diagnoser (TV-M5): the template families
are still assumed exactly known, only the magnitude within them is not.

## 10. Design

| | |
|---|---|
| Flight conditions | FC-1, FC-2, FC-3, FC-5. **FC-4 is not resurrected** (FAIL-0001) |
| Classes | 18 (F0 + 4 mechanisms × 4 channels + F6) |
| Magnitudes | 9 per class (F0 has none) → 154 templates per condition |
| Windows | 0.25, 0.5, 1, 2, 5, 10, 18 s after onset — spanning pre-manoeuvre and post-manoeuvre |
| Noise | η ∈ {0.1, 1, 10}: low / reference / elevated, giving the §14 comparison |
| Replications | 20 000 per cell |
| New simulations | 4 × 17 × 8 = **544** (the $m=1$ grid is reused from DS-0001) |

**Efficiency.** As in EXP-0010 the Monte Carlo reduces exactly: with $y = w_i + z$, the score of
template $j$ is $\lVert w_j\rVert^2 - 2(M_{ij} + t_j)$ where $t = z\!\cdot\!w \sim N(0, M)$ and $M$ is
the raw Gram matrix — **independent of the true template $i$**. One sample of $t$ therefore serves
all 154 true templates in a cell.

## 11. Validity attacks (required)

| ID | Attack | Purpose |
|---|---|---|
| W-A | Magnitude-grid resolution: √2 grid vs 2× subgrid | Is the overlap an artefact of discretisation? |
| W-B | Magnitude range: [0.5,2] vs [0.25,4] (Cases B vs C) | Does overlap exist only because the range is broad? |
| W-C | Observation window (built into the design) | Does more data resolve it, or is it persistent? |
| W-D | Noise level η ∈ {0.1, 1, 10} | Does the overlap survive — and does it survive *low* noise, which is the sharper test? |
| W-E | Linearity of response in magnitude | Justifies (or refutes) interpolating between grid points |
| W-F | Alternative separation metric (per-channel max vs RMS) | Is the overlap metric-specific? |
| W-G | Detectability floor on/off | Is the overlap an artefact of undetectably small faults? |

## 12. Decision gate

Classify the evidence as Outcome A (known magnitude was the main hidden assumption), B (magnitude
uncertainty is manageable / transient), C (fundamental cross-class ambiguity exists), D (model
assumptions dominate), E (mixed) — or several. Heterogeneous evidence is not to be forced into one
category.

## 13. Prohibited in this experiment

No neural networks, no learning, no trained classifiers, no hyperparameter optimisation, no
uncertainty estimator, no decision manager. No claim of improved safety, real-aircraft validity, or
real-world confidence. FC-4 is not resurrected. EXP-0002 and EXP-0010 are not rewritten to make the
narrative cleaner.
