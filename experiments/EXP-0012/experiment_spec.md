# EXP-0012 — Experiment Specification

**Status:** PRE-REGISTERED. Written and committed **before** any EXP-0012 simulation was run.
**Type:** Adversarial. Tests whether the existing physics-based diagnostic framework becomes
*confidently wrong* when the true fault lies outside its hypothesis library.
**Date specified:** 2026-09-08

> §§1–11 are fixed here. The unseen-fault taxonomy, hypothesis space, metrics, thresholds,
> replication plan and decision gate may not be changed after results are seen.

---

## 1. Research question

> When an aircraft experiences a fault absent from the diagnostic hypothesis library, does a
> physics-based diagnostic system recognise that its hypotheses are inadequate, or does it
> confidently assign the observation to an incorrect known fault?

The phenomenon of interest: **increasing evidence should not produce increasing trust if the
hypothesis space is wrong.**

## 2. Two facts established analytically, before any simulation

### FACT 1 — The posterior is structurally incapable of expressing hypothesis-space mismatch

The classifier's confidence is
$P(j\mid y) = \exp(\mathrm{LL}_j)\big/\sum_k \exp(\mathrm{LL}_k)$.
Adding a constant $c$ to **every** $\mathrm{LL}_j$ — which is exactly what a uniform lack of fit
does — leaves the posterior **unchanged**. A softmax over $H_{\text{known}}$ therefore cannot say
"none of the above", **by construction, not by empirical accident.**

**Consequence: Outcome A (confidently wrong) is near-guaranteed for the posterior, and demonstrating
it would be close to trivial.** Reporting that alone would meet the letter of the research question
while evading §25's warning. The scientifically live question is therefore the second one:

> Does a **non-learning** statistic that *is* sensitive to absolute fit — the residual — already
> supply the missing "none of the above" signal?

### FACT 2 — The residual is a χ² goodness-of-fit statistic with a computable detection threshold

$R = \min_j \lVert y - w_j\rVert^2/\eta^2$. Under a correct hypothesis $R \sim \chi^2(KN)$; under
mismatch $R \sim \chi^2(KN) + \lVert\Delta_{\min}\rVert^2/\eta^2$. So mismatch is detectable at level
$\alpha$ iff

$$\frac{\lVert\Delta_{\min}\rVert}{\eta} \;>\; \sqrt{z_\alpha}\,(2KN)^{1/4}$$

| Window | $N$ | $KN$ | Detection threshold on $\lVert\Delta_{\min}\rVert/\eta$ ($\alpha=0.01$) |
|---|---|---|---|
| 0.25 s | 26 | 338 | 7.8 |
| 0.5 s | 51 | 663 | 9.2 |
| 2 s | 201 | 2613 | 13.0 |
| 5 s | 501 | 6513 | 16.3 |
| 18 s | 1801 | 23413 | **22.4** |

## 3. Pre-registered predictions

- **P1.** The posterior will be confidently wrong for every unseen fault (from FACT 1). Confidence
  will **not** decrease with observation length, because the posterior is invariant to uniform misfit.
- **P2.** The χ² residual test will detect mismatch whenever the nearest-known distance exceeds the
  threshold in §2 — about **22 deflection units at the full window**. EXP-0011 measured typical
  inter-class distances in the hundreds, so **most unseen faults should be caught by the residual.**
- **P3.** The dangerous case is an unseen fault that sits *on* a known manifold. **UF-001 (vane
  stiction) is predicted to be exactly a stuck-sensor fault while the signal is static**, so before
  the manoeuvre its nearest-known distance is **zero**: confidently wrong *and* undetectable by
  goodness-of-fit. After the manoeuvre it should separate.
- **P4.** UF-004 (static-port blockage) corrupts barometric altitude, and **no fault in the library
  acts on that channel at all**, so its residual should be large and it should be caught easily.
- **P5.** The winning hypothesis may **change** with observation window for UF-001 (stuck-like early,
  something else later) — a confidence reversal in the sense of §15.

**These predictions are recorded before the run and will not be refitted.**

## 4. Hypothesis space

$H_{\text{known}}$ = the 18 classes of EXP-0010/0011: `F0` nominal; `F1` bias, `F2` scale, `F3` drift,
`F4` stuck on each of $\{q, a_z, V_t, \alpha\}$; `F6` elevator effectiveness loss. Magnitude is
marginalised over the EXP-0011 grid (Case C prior, $[0.25,4]\times$ nominal).

**Every unseen fault satisfies $UF_i \notin H_{\text{known}}$. No "unknown" class is added to the
primary experiment** (§7 of the brief). A rejection rule is evaluated only as a clearly labelled
post-hoc analysis.

The classifier receives **only** the noisy measurement vector. Not the true identity, not the
magnitude, not an OOD flag, and no feature encoding novelty.

## 5. Unseen-fault taxonomy

Each has a physical interpretation, a mathematical definition, and a stated reason for being outside
the library. **Magnitudes are chosen to place each fault at a target position on a difficulty axis,
not to manufacture a result** — and the actual position is measured, not assumed.

### Category A — new mechanism on an existing channel

**UF-001 — Angle-of-attack vane stiction (predicted NEAR)**
*Physical:* a vane bearing with static friction; the reading only updates once the true angle has
moved more than δ from the last reported value.
*Model:* $y[k] = y[k-1]$ if $|y_{\text{true}}[k]-y[k-1]| < \delta$, else
$y_{\text{true}}[k] - \delta\,\mathrm{sgn}(\cdot)$.
*Not in library:* `F4` is a *total* freeze; this is a partial, signal-dependent freeze.
*Expected signature:* identical to `F4_alpha` while α is static; a staircase during the manoeuvre.

**UF-002 — Rate-gyro saturation (predicted MODERATE)**
*Physical:* the gyro's measurement range is exceeded and the output clips.
*Model:* $y = \mathrm{clip}(y_{\text{true}}, -L, +L)$.
*Not in library:* `F2` is a linear scale error; this is a nonlinearity active only at high rate.
*Expected signature:* invisible until $|q|>L$; then flat-topped, resembling an attenuating scale error.

**UF-003 — Pitot line partial blockage, pneumatic lag (predicted NEAR)**
*Physical:* a restricted pitot line increases the pneumatic time constant — a documented air-data
failure mode.
*Model:* $\dot y = (y_{\text{true}} - y)/\tau$.
*Not in library:* no dynamic/filtering fault is represented.
*Expected signature:* zero error in steady state, error only during transients.

### Category B — cross-channel coupled fault

**UF-004 — Static-port blockage (predicted DISTANT)**
*Physical:* a blocked static port biases the static-pressure reference, which corrupts **barometric
altitude and airspeed simultaneously** through one physical cause.
*Model:* a single static-pressure error $\delta p$ gives $\Delta h = \delta p/(\rho g)$ and
$\Delta V \approx \delta p/(\rho V)$.
*Not in library:* every library fault is single-channel, and **no library fault acts on altitude at
all**.
*Expected signature:* an altitude error no hypothesis can explain → large residual.

### Category C — model-structure mismatch (plant faults)

**UF-005 — Pitch static-stability loss (predicted NEAR)**
*Physical:* partial horizontal-stabiliser damage or an aft centre-of-gravity shift reduces static
pitch stiffness.
*Model:* $C_{m\alpha} \rightarrow (1-\lambda)\,C_{m\alpha}$ from onset.
*Not in library:* `F6` changes *control* effectiveness; this changes *stability*. Both are plant
faults with pitch-axis signatures, so this is deliberately the hardest plant case.
*Expected signature:* altered closed-loop pitch dynamics, plausibly resembling `F6`.

**UF-006 — Airframe icing drag rise (predicted MODERATE)**
*Physical:* ice accretion increases parasite drag.
*Model:* $C_{D0} \rightarrow (1+\kappa)\,C_{D0}$ from onset.
*Not in library:* no aerodynamic-degradation hypothesis exists.
*Expected signature:* airspeed loss opposed by the autothrottle; a throttle and speed signature.

## 6. Design

| | |
|---|---|
| Unseen faults | 6, each at 3 magnitudes (small / nominal / large) |
| Flight conditions | FC-1, FC-2, FC-3, FC-5. **FC-4 not resurrected** (FAIL-0001) |
| Windows | 0.25, 0.5, 1, 2, 5, 10, 18 s — the EXP-0010/0011 axis, unchanged |
| Noise | η = 1 primary; 0.1 and 10 for the noise attack |
| New simulations | 6 × 3 × 4 = **72** |
| Replications | Determined by a pilot (§9), not assumed |

**Case A (control):** known faults through the identical pipeline, to verify that any OOD failure is
not general classifier failure.
**Case B:** unseen fault, classifier restricted to $H_{\text{known}}$.
**Case C:** nearest-known comparison — continuous manifold distance from each unseen fault to the
whole library, extending the EXP-0011 method.

## 7. Metrics

**Confidence — defined precisely.** $P(j\mid y)$ is a **posterior over $H_{\text{known}}$ under a
uniform class prior and the stated noise model**. It is a genuine probability *conditional on the
hypothesis space containing the truth* — which is exactly the condition this experiment violates.
It is **not** a probability that the diagnosis is correct, and is never described as one.

**Primary metric — false confidence:**
$$FC(t) = P\big(\text{posterior confidence} \ge \tau \;\wedge\; \text{no correct hypothesis exists}\big)$$
with **τ = 0.95**, reused from EXP-0010/0011's practical-ambiguity threshold rather than chosen here.

**Secondary:** median and maximum winning confidence; confidence growth with window; runner-up
margin; nearest-known continuous manifold distance; **normalised residual $R/KN$ and its χ² p-value**;
winning-hypothesis identity and whether it changes with window.

## 8. The three failure modes, kept separate (§11 of the brief)

At every window each case is classified as exactly one of:

| Label | Criterion |
|---|---|
| **Not yet detectable** | The unseen fault's distance from `F0` is below the detection threshold |
| **Ambiguous among known** | Detectable, but the top-two posterior margin is small |
| **Confidently assigned to a wrong known hypothesis** | Confidence ≥ τ, and the residual does **not** reject |
| **Poorly explained by all known hypotheses** | The χ² residual test rejects at α = 0.01 |

The last two are the scientifically decisive pair: the first is the dangerous failure, the second is
the framework catching itself without any ML.

## 9. Statistical plan

A pilot measures score and confidence variance and the effect size, and the replication count is
chosen from it — **not assumed** (§18 of the brief). Exact Monte Carlo reduction as in EXP-0011,
extended to carry the residual: decomposing $z = Ua + z_\perp$ on an orthonormal basis of the
template span gives $\lVert z\rVert^2 = \lVert a\rVert^2 + \lVert z_\perp\rVert^2$ with
$\lVert z_\perp\rVert^2 \sim \chi^2(KN-r)$ independent, so both the projections and the residual are
sampled exactly.

## 10. Validity attacks

| ID | Attack | Purpose |
|---|---|---|
| W-A | Nearest-known: UF-001 pre-manoeuvre, predicted to sit *on* the `F4_alpha` manifold | Does the main result survive the hardest case? |
| W-B | Easy-OOD: UF-004, predicted far from everything | Are obvious OOD cases already rejected by the existing score? |
| W-C | Window: restrict to pre-manoeuvre windows | Is apparent OOD confidence merely non-detection? |
| W-D | Model/noise: η ∈ {0.1, 1, 10} and unseen-fault magnitude ×{0.5, 1, 2} | Does the effect survive modest uncertainty? |
| W-E | Known-fault control | Are known faults still diagnosed correctly by the same pipeline? |
| W-F | Envelope validity | Reject trajectories exceeding the EXP-0011 rule (divergence or α > 25°). **Do not repeat the FAIL-0001 mistake.** |

## 11. Decision gate

| Gate | Criterion |
|---|---|
| **A — strong support** | At least one physically meaningful unseen fault produces high confidence in a wrong known fault, with sufficient observable evidence, surviving the attacks |
| **B — moderate** | Misclassified but confidence low or unstable |
| **C — weak** | Additional observation reliably exposes the mismatch; the problem is transient |
| **D — negative** | The framework already indicates poor fit for unseen faults. **Do not invent an ML problem** — investigate why the physics-based representation is robust |

**Gate D is a live and expected possibility** given FACT 2, and would be a legitimate result.
Both A and D may hold simultaneously for different faults; heterogeneous evidence will not be forced
into one category.

## 12. Prohibited

No neural networks, random forests, SVMs, learned embeddings, autoencoders, learned OOD detectors,
Bayesian neural networks, deep ensembles, conformal prediction, learned uncertainty estimators,
reinforcement learning or learned policies. No abstention mechanism in the primary experiment. No
claim of improved safety or real-aircraft validity. FC-4 is not resurrected. Prior experiments are
not rewritten.
