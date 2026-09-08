# EXP-0002 — Experiment Specification

**Status:** PRE-REGISTERED. Written and committed **before** any simulation was run.
**Type:** Gate experiment (can invalidate the AURA design)
**Date specified:** 2026-09-08
**Tests:** the ground-truth premise underlying H2 (`docs/hypotheses.md`)
**Terminology correction:** `docs/decisions/ADR-0008-distinguishability-vs-structural-isolability.md`
**Model substitution:** `docs/decisions/ADR-0007-aircraft-model-licence-substitution.md`

> **Nothing in §§1–7 below may be changed after results are seen.** Metrics, thresholds, fault set,
> flight conditions and pass/fail criteria are fixed here.

---

## 1. Question

> **Do different faults produce distinguishable measured responses, and does the structure of that
> ambiguity change across flight conditions?**

The AURA design assumes the answer is yes on both counts. If fault distinguishability does not
depend on operating condition, the evidential-ambiguity component $A$ has no condition-dependent
ground truth, H2 loses its reference, and the research design must change.

## 2. Experimental hypothesis

**EH-1.** The pairwise fault distinguishability matrix of the GFW-1 aircraft, under a fixed
excitation, is neither diagonal nor dense, and its structure varies across flight conditions.

**Direction of prior belief, stated before running:** *uncertain, leaning against on one specific
point.* In a deterministic, noise-free simulation where every faulted channel is directly measured,
most single sensor faults are expected to be separable. The near-diagonal outcome is a live
possibility and would be a legitimate FAIL. The genuinely uncertain part is whether the
*continuous* distance structure — which pairs are closest, and by how much — reorders across
conditions.

## 3. Variables

### 3.1 Independent

| Variable | Levels |
|---|---|
| Flight condition | 4 (FC-1 … FC-4, §5) |
| Fault identity | 18 (F0 nominal + 16 sensor faults + 1 actuator fault, §4) |

Full factorial: 4 × 18 = **72 simulation runs**.

### 3.2 Dependent (declared before any run)

**Primary.** Pairwise normalised response distance $d_{ij}(c)$ between faults $i$ and $j$ at flight
condition $c$, computed on the 13-channel measured output vector over the post-onset interval
(§6). This is a **continuous** quantity; the binary matrix is a thresholded view of it.

**Derived (pre-declared).**
- Binary distinguishability matrix $D_{ij}(c) = [\,d_{ij}(c) > \tau\,]$ at $\tau = 1.0$.
- Fraction of distinguishable pairs per condition.
- Ambiguity degree per fault (number of faults it is not distinguishable from).
- Cross-condition change: number of pairs whose binary verdict differs between conditions.
- Spearman rank correlation of the vectorised $d_{ij}$ between condition pairs — the
  **threshold-free** measure of whether the ambiguity *structure* reorders.

**Not used:** no metric will be selected after inspecting results. Any additional quantity computed
later is labelled EXPLORATORY in the report.

### 3.3 Controlled (identical across all runs)

Aircraft model and every parameter; initial condition (trim for that flight condition);
simulation duration 20 s; RK4 fixed step $h = 0.002$ s; measurement sampling 100 Hz;
excitation command profile; controller structure and gains; fault onset time 2.0 s;
fault magnitudes (§4); no process noise; no measurement noise; no wind or turbulence;
float64 throughout; deterministic — no random number generation anywhere in the pipeline.

## 4. Fault set

From the Phase 0 taxonomy (`reports/phase0/EXPERIMENTAL_DESIGN_PRELIMINARY.md` §2), applied to the
four designated channels $\{q,\ a_z,\ V_t,\ \alpha\}$.

| Mechanism | Model | Class | Magnitude (pre-declared) |
|---|---|---|---|
| F1 bias | $y = y_{\text{true}} + b$ | abrupt | $b = 10\sigma_k$ |
| F2 scale | $y = k\, y_{\text{true}}$ | abrupt | $k = 1.10$ |
| F3 drift | $y = y_{\text{true}} + \dot b\,(t-t_0)$ | gradual | reaches $10\sigma_k$ at $t = 20$ s |
| F4 stuck | $y = y(t_0)$ | abrupt | — |
| F6 elevator effectiveness loss | $\delta_{e,\text{eff}} = \lambda \delta_e$ | abrupt | $\lambda = 0.7$ |

Giving 18 fault modes: `F0`, `F1_q F1_az F1_Vt F1_alpha`, `F2_*`, `F3_*`, `F4_*`, `F6`.

**Magnitudes are referenced to the pre-declared sensor noise scale $\sigma_k$ (§6.2), not tuned.**
A magnitude sensitivity analysis is required (§8).

### F5 (increased noise) is excluded — and why

**FACT, not a finding:** a fault that changes only the *variance* of a measurement has an identical
mean response to nominal. In a deterministic noise-free simulation, F5 is identical to F0 **by
construction**. Including it would inject a guaranteed ambiguous pair that is an artefact of the
experimental design rather than a property of the aircraft.

F5 is therefore excluded from EXP-0002 and deferred to a stochastic experiment. Reporting it as
"ambiguous" here would be misleading.

### Affected measurements, declared in advance

| Fault | Directly corrupts | Expected indirect effect |
|---|---|---|
| F1/F2/F3/F4 on `q` | `q` | all channels, via the pitch-rate feedback path |
| F1/F2/F3/F4 on `az` | `az` | all channels, via normal-acceleration feedback |
| F1/F2/F3/F4 on `Vt` | `Vt` | all channels, via autothrottle |
| F1/F2/F3/F4 on `alpha` | `alpha` | all channels, via the α-feedback term |
| F6 | none directly | all channels, via reduced pitch control authority |

All four faulted channels are in the control loop. This is deliberate: a fault on an unused channel
would appear in exactly one measurement and be trivially separable, which tests nothing.

## 5. Flight conditions

Four conditions spanning dynamic pressure and trim angle of attack. FC-2 and FC-3 are chosen to
have **similar dynamic pressure at different altitude and airspeed**, so that density and speed
effects can be separated from dynamic-pressure effects.

| ID | Altitude | Airspeed | Regime probed | Rationale |
|---|---|---|---|---|
| FC-1 | 1000 m | 45 m/s | High $\bar q$, low $\alpha$ | Maximum control effectiveness; smallest trim α |
| FC-2 | 1000 m | 28 m/s | Low $\bar q$, moderate $\alpha$ | Low-speed, high-density |
| FC-3 | 5000 m | 35 m/s | Similar $\bar q$ to FC-2, different $\rho$ and $V$ | **Control**: separates $\bar q$ from altitude/speed |
| FC-4 | 5000 m | 24 m/s | Lowest $\bar q$, highest $\alpha$ | Approaches the nonlinear region of the lift curve |

Trim $\alpha$, $\bar q$ and trim controls are **computed and reported**, not assumed.

**Excitation (identical at every condition):** a longitudinal pitch-attitude doublet on
$\theta_{\text{cmd}}$ — $+3°$ over $[4,7)$ s, $-3°$ over $[7,10)$ s, zero otherwise. Excitation is
required: a scale-factor fault on a signal that is identically zero produces no response, so a pure
trim hold would make several faults degenerate for a reason that has nothing to do with the
aircraft.

## 6. Mathematical definition of distinguishability

### 6.1 Response vector

$\mathbf{y}(t) \in \mathbb{R}^{13}$ — the measured output vector as a diagnoser would see it:
$[p, q, r, a_x, a_y, a_z, V_t, \alpha, \beta, h, \phi, \theta, \psi]$, sampled at 100 Hz.

Sensor faults corrupt $\mathbf{y}$ directly **and** propagate through the closed loop. The actuator
fault propagates only through the plant.

### 6.2 Normalisation

Each channel is normalised by a **fixed, pre-declared sensor noise standard deviation** $\sigma_k$,
an instrument property — not a data-derived scale. Data-derived normalisation is avoided because it
can be influenced by the results.

| Channel | $\sigma_k$ | Channel | $\sigma_k$ |
|---|---|---|---|
| $p,q,r$ | 0.5 °/s = 8.727e-3 rad/s | $V_t$ | 0.5 m/s |
| $a_x,a_y,a_z$ | 0.05 m/s² | $\alpha,\beta$ | 0.5° = 8.727e-3 rad |
| $\phi,\theta,\psi$ | 0.2° = 3.491e-3 rad | $h$ | 1.0 m |

### 6.3 Distance

Over the comparison interval $[t_0, t_{\text{end}}] = [2, 20]$ s ($N = 1801$ samples, post-onset
only), for faults $i, j$ at condition $c$:

$$d_{ij}(c) \;=\; \sqrt{\frac{1}{K N}\sum_{k=1}^{K}\sum_{n=1}^{N}\left(\frac{y_{i,k}(t_n)-y_{j,k}(t_n)}{\sigma_k}\right)^{2}}$$

with $K = 13$. Units: **multiples of per-sample, per-channel RMS sensor noise.** The metric is a
trajectory comparison (not pointwise), aggregates channels by root-mean-square, and is symmetric
with $d_{ii} = 0$.

### 6.4 Threshold and its justification

**Primary threshold $\tau = 1.0$, declared a priori.**

Justification, independent of results: if two fault responses differ by less than the RMS sensor
noise on a per-sample, per-channel basis, then a single-realisation observer has no consistent
signal to separate them. $\tau = 1$ is the point at which the mean separation equals the noise floor.

This threshold is deliberately **conservative in the direction that makes PASS harder**: a matched
filter integrating over $N = 1801$ samples could separate signals well below 1σ, so $\tau = 1$
over-reports ambiguity relative to an optimal detector. It cannot manufacture the "not diagonal"
half of the pass criterion — it can only manufacture the "not dense" half, which the threshold sweep
(§8) exists to expose.

**Threshold sensitivity is mandatory**, over $\tau \in \{0.1, 0.3, 1, 3, 10, 30, 100\}$. The
qualitative conclusion must survive it, and the primary cross-condition result (Spearman rank
correlation of $d_{ij}$) is **threshold-free by construction**.

### 6.5 Categories

| Category | Condition |
|---|---|
| Distinguishable | $d_{ij} > \tau$ |
| Indistinguishable | $d_{ij} \le \tau$ |
| Numerically identical | $d_{ij} < 10^{-9}$ — flagged separately as a likely implementation artefact, not a physical result |

### 6.6 Treatment of noise and correlated states

**No noise is simulated.** Distinguishability is evaluated **before measurement uncertainty** —
noise enters only through the normalisation $\sigma_k$, i.e. as a *scale* for what counts as a
meaningful difference, not as a *realisation*. This is stated explicitly because it bounds what the
experiment can conclude (§9).

Naturally correlated channels (e.g. $\alpha$ and $a_z$ are aerodynamically linked) are **not**
decorrelated. Whitening would require a covariance estimated from the data, which would make the
metric data-dependent and thus influenceable by the results. The consequence — that correlated
channels contribute partially redundant evidence, inflating $d$ somewhat — is a stated limitation.

## 7. Pass / fail criterion (pre-declared, not to be changed)

### PASS requires **all four**

1. The binary matrix is **not fully diagonal** at every condition (some genuine ambiguity exists).
2. The binary matrix is **not fully dense** at every condition (some faults are separable).
3. The ambiguity is meaningful — at least one indistinguishable pair is a physically motivated
   confusion, not an artefact.
4. The structure **differs across flight conditions** — at least one pair changes verdict between
   conditions, **and** the threshold-free rank correlation of $d_{ij}$ between conditions is
   materially below 1.

### FAIL if any of

- fully diagonal at all conditions;
- fully dense at all conditions;
- ambiguity exists but does not change across conditions;
- the observables cannot support a defensible distinction;
- numerical or model artefacts dominate;
- the experiment cannot be reproduced bitwise.

## 8. Required sensitivity analyses (§12 of the brief)

| # | Sweep | Purpose |
|---|---|---|
| S-A | Integration step $h \in \{0.004, 0.002, 0.001\}$ | Numerical convergence — is the result solver-dependent? |
| S-B | Threshold $\tau$, 7 levels | Does the qualitative conclusion survive threshold choice? |
| S-C | Fault magnitude ×{0.5, 1, 2} | Is the matrix an artefact of one arbitrary magnitude? |
| S-D | Simulation duration {10, 20} s | Does more data change the verdict? |
| S-E | Determinism: identical re-run, bitwise compare | Reproducibility |

Noise sensitivity is **not** run — no noise is simulated (§6.6). This is stated rather than skipped.

## 9. What this experiment cannot establish

Declared in advance so it cannot be quietly overstated afterwards:

- It cannot show that uncertainty-aware diagnosis will work.
- It cannot show that a *statistical* diagnoser would find these faults ambiguous — it is
  deterministic and noise-free.
- It cannot generalise beyond GFW-1, one excitation, and these magnitudes (TV-D10, ADR-0007).
- It cannot establish structural isolability in the Frisk/Krysander sense (ADR-0008).

At most it can establish whether **ambiguity and operating-condition-dependent diagnosability are
legitimate research problems in a nonlinear fixed-wing model.**

## 10. Provenance

Every result traces: `EXP-0002` → flight condition → fault ID → configuration file (hashed) →
code version (git commit) → simulation output → analysis → matrix. Run manifests conform to
`infrastructure/schemas/run_manifest.schema.json`.
