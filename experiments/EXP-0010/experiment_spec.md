# EXP-0010 — Experiment Specification

**Status:** PRE-REGISTERED. Written and committed **before** any result was computed.
**Type:** Extension of EXP-0002 (not a replacement)
**Date specified:** 2026-09-08
**Answers:** RQ-0010-A (noise degradation), RQ-0010-B (ambiguity threshold), RQ-0010-C (condition dependence)

> §§1–9 are fixed here. Metrics, thresholds, noise model, levels and replication count may not be
> changed after results are seen.

---

## 1. Question

> When realistic measurement uncertainty is introduced, which fault hypotheses remain practically
> distinguishable, which become statistically ambiguous, and does the boundary depend meaningfully
> on flight condition?

## 2. A design constraint derived *before* running

EXP-0002 measured $d_{ij}$ = RMS difference per channel per sample, in sensor-σ units. For two
**known** signals in white Gaussian noise the Bayes-optimal binary test has error probability
$P_e = \Phi(-d'/2)$, where $d'$ is the *unnormalised* deflection. These are related exactly:

$$d'_{ij} \;=\; d_{ij}\sqrt{KN}, \qquad \sqrt{KN}=\sqrt{13\times 1801}=153.0$$

Consequences, computed before the experiment:

| EXP-0002 $d_{ij}$ | Deflection $d'$ | Optimal $P_e$ at reference noise |
|---|---|---|
| 0.066 (most ambiguous pair) | 10.1 | 2.2 × 10⁻⁷ |
| 1.0 (EXP-0002 threshold τ) | 153 | < 10⁻¹⁶ |
| 3.38 (median pair) | 517 | < 10⁻¹⁶ |

**At the reference sensor specification, with known templates and the full 18 s window, every
EXP-0002 pair is separable with negligible error.** A study that sweeps noise alone, at the
reference level, would measure nothing.

**This is also a correction to how EXP-0002 should be read.** Its τ = 1 threshold was declared as
deliberately conservative; EXP-0010 quantifies *how* conservative — by a factor of √(KN) ≈ 153.
EXP-0002's "ambiguous pairs" are ambiguous **per-sample**, not ambiguous to an observer that
integrates the whole window. This does not invalidate EXP-0002 — the ambiguity *ordering* and the
condition-dependence stand — but the binary labels must be read as a conservative per-sample view.

The experiment therefore sweeps **two** axes: effective noise level **and observation window**.

## 3. Practical diagnosability — the definition used here

| Term | Meaning |
|---|---|
| **Deterministic distinguishability** (EXP-0002) | The noise-free responses differ: $d_{ij} > 0$ |
| **Practical distinguishability** (EXP-0010) | An optimal observer, given the noise level and observation window, separates the two hypotheses with high probability |

A pair is **not** called indistinguishable because noisy trajectories overlap in one realisation, and
**not** called distinguishable because noise-free trajectories differ by an arbitrarily small amount.
The measure is a probability over the noise distribution.

## 4. Noise model (pre-declared)

| Property | Value |
|---|---|
| Form | Additive, zero-mean |
| Distribution | Gaussian (primary); Student-t(ν=4) and AR(1) coloured tested in validity attack |
| Spectrum | White (primary) |
| Independence | Independent across channels and across time |
| Per-channel σ | The EXP-0002 sensor specification (rates 0.5 °/s, accels 0.05 m/s², $V_t$ 0.5 m/s, α/β 0.5°, h 1.0 m, attitude 0.2°) |
| Provenance | **Synthetic and representative of MEMS-grade instruments. Not taken from any specific datasheet, and not a claim about any real sensor.** |
| Sampling | 100 Hz, synchronous |
| Scaling | Multiplier η applied uniformly to all σ |
| Seeds | Fixed base seed 20261008; per-cell seed derived deterministically from (condition, window, η, true fault) |

**Deliberately separated, not conflated:**

| Quantity | Where it lives in AURA |
|---|---|
| Measurement noise | This model (η × σ) |
| Sensor bias | Fault mechanism **F1** |
| Sensor drift | Fault mechanism **F3** |
| Fault magnitude | Fixed at the EXP-0002 values; swept in the validity attack |
| Model uncertainty | **Not modelled.** See §11 |

## 5. Normalisation

All channels are normalised by their own σ before any comparison, so the metric is dimensionless and
no channel's raw magnitude dominates. This is the same normalisation as EXP-0002 — chosen for
continuity, not because it produces cleaner results.

## 6. Noise levels (pre-declared, with honest labelling)

η ∈ {1, 2, 5, 10, 20, 50, 100, 200, 500, 1000}.

- **η = 1** — the reference specification. *Realistic instrument-grade.*
- **η = 2–5** — degraded or lower-grade sensors. *Plausible.*
- **η ≥ 10** — **explicitly labelled experimental stress levels.** These are **not** a claim that any
  aircraft sensor is 10–1000× worse than spec.

Their scientific justification is different and is stated in advance: what governs discrimination is
the **deflection** $d'$, and *any* source of effective uncertainty reduces it identically — model
mismatch, turbulence, unmodelled dynamics, and template error all act like elevated noise. η is
therefore read as a **total effective uncertainty multiplier**, of which sensor noise is one
component. This is the honest reading, and the report will use it.

## 7. Observation windows

$T_{\text{obs}}$ ∈ {0.05, 0.1, 0.25, 0.5, 1, 2, 5, 10, 18} s after fault onset (5 to 1801 samples).

Included because §16 requires a time-to-isolation perspective and because §2 shows window length is
as important as noise level.

## 8. Statistical separation measures

### Primary — probability of correct isolation, $P_{\text{iso}}$

The Bayes-optimal 18-way classifier with **known templates** and known noise: choose
$\hat j = \arg\min_j \lVert (y - y_j)/(\eta\sigma) \rVert^2$. $P_{\text{iso}}$ is the probability it
returns the true fault, estimated by Monte Carlo, averaged over the 18 hypotheses with equal priors.

This is the isolation question directly (§10), and it is an **upper bound on any real diagnoser**,
because no real system knows the templates exactly. Reported as an upper bound throughout.

### Secondary 1 — pairwise probability of correct discrimination, $P_{\text{disc}}$

Closed form for the optimal binary test: $P_{\text{disc}}(i,j) = \Phi\!\left(d'_{ij}/2\eta\right)$.
Exact, no Monte Carlo, and directly comparable with EXP-0002.

### Secondary 2 — detection

$P_{\text{det}}$: probability the classifier does not return F0 when a fault is present.
$P_{\text{FA}}$: probability it does not return F0 when none is. Reported to keep detection and
isolation separate (§10) — detection performance may **not** substitute for isolation.

### Practical-ambiguity reading aid

A pair is called **practically ambiguous** when $P_{\text{disc}} < 0.95$. This is a reading aid on a
continuous quantity, not a claim that the world has a sharp threshold (§14). Every result is
reported as a continuous surface; the 0.95 contour is drawn on figures only to orient the reader.

## 9. Monte Carlo methodology

**Efficiency (§26).** The deterministic trajectories from EXP-0002 (`DS-0001`) are **reused without
re-simulation**. Because the classifier is a quadratic form in Gaussian noise, the Monte Carlo can be
performed exactly in 18 dimensions rather than in 13 × N measurement dimensions:

With $w_j = y_j/(\eta\sigma)$ and true fault $i$, correct isolation requires
$\lVert v_j \rVert^2 - 2\,z\!\cdot\!v_j > 0$ for all $j \ne i$, where $v_j = w_j - w_i$ and
$z \sim \mathcal{N}(0, I)$. Writing $u_j = z\!\cdot\!v_j$, the vector $u$ is Gaussian with covariance
$G^{(i)}_{jk} = v_j\!\cdot\!v_k$, obtainable from a single 18×18 Gram matrix per (condition, window).
Correct isolation ⟺ $u_j < G^{(i)}_{jj}/2$ for all $j\ne i$.

This is **exact, not an approximation**, for Gaussian white noise, and reduces the cost by ~10⁴.
It is verified against direct full-dimensional simulation in the pilot.

**Replications:** N = 20 000 per cell. Justification, declared in advance: the binomial standard
error at the worst case $P=0.5$ is $\sqrt{0.25/20000} = 0.0035$, giving a 95% CI half-width of
±0.007 — sufficient to resolve the 0.95 contour. The count is fixed before results and is not
adjusted afterwards.

**Grid:** 4 valid flight conditions × 10 noise levels × 9 windows × 18 true faults × 20 000 = 130 M
classification trials.

**FC-4 is not used.** It remains invalid (FAIL-0001) and is not resurrected.

## 10. What EXP-0010 preserves from EXP-0002

Carried forward unchanged, and not to be overstated:

1. FC-4 is invalid and excluded.
2. The five-member ambiguity group is EXP-0002's strongest persistent finding.
3. Condition-dependent distinguishability exists; its practical significance was unresolved — that
   is what this experiment tests.
4. The closed-form bias/scale prediction is independently supported.
5. EXP-0002 was noise-free.
6. Neither experiment establishes that uncertainty-aware autonomy improves outcomes.

## 11. What EXP-0010 cannot establish

Declared in advance:

- It assumes the diagnoser knows all 18 template trajectories **exactly**. Real systems do not.
  Every $P$ reported is therefore an **upper bound**.
- **Fault magnitude is treated as known.** If magnitude were free, hypothesis classes would overlap
  and ambiguity would be strictly greater. This is quantified only for the F1_Vt/F2_Vt pair (§12 of
  the brief) and is recommended as the next experiment.
- Model uncertainty is not modelled; η is used as a proxy and labelled as such.
- One self-implemented aircraft (TV-D10), one excitation, one fault magnitude set.
- Nothing about real sensors, real aircraft, or operational applicability.

## 12. Validity attacks (required)

| ID | Attack | Purpose |
|---|---|---|
| V-A | Seed sensitivity: repeat with a different base seed; bootstrap CI over trials | Is the conclusion seed-dependent? |
| V-B | Noise distribution: Student-t(ν=4) and AR(1) coloured (ρ=0.5), by direct full-dimensional simulation | Does it survive non-Gaussian and correlated noise? |
| V-C | Exactness check: Gram-matrix Monte Carlo vs direct full-dimensional simulation | Is the efficient method correct? |
| V-D | Fault magnitude ×0.5 and ×2 (re-simulated) | Is the result an artefact of one magnitude? |
| V-E | Window: built into the primary design | Does longer observation dissolve ambiguity? |
| V-F | Consistency: recomputed $d_{ij}$ must reproduce EXP-0002's matrix | Is the pipeline reading the same data? |

## 13. Decision gate

At completion, classify the evidence as Outcome A (noise scales separation), B (noise creates new
ambiguity), C (noise interacts with flight condition), D (dominated by modelling assumptions),
E (mixed) — or several, if several are supported.

**No uncertainty-aware decision layer, estimator, or learning component is built in EXP-0010,
regardless of outcome.**
