# EXP-0012 — Unseen Faults and Hypothesis-Space Mismatch

**Experiment:** EXP-0012 · **Date:** 2026-09-08 · **Status:** COMPLETED
**Pre-registration:** [`experiments/EXP-0012/experiment_spec.md`](../../experiments/EXP-0012/experiment_spec.md)
**Results:** `results/validation/EXP-0012/exp0012_results.json` · **Data:** DS-0001, DS-0002, DS-0003
> **Correction (2026-09-08, cumulative review §8B).** An earlier version of this report described the
> χ² residual as a statistic the framework "already contains". That was wrong. Direct inspection of
> `analysis/practical_diagnosability.py` and of the EXP-0010 and EXP-0011 results files confirms
> that **no goodness-of-fit residual existed before EXP-0012** — it was added as part of this
> experiment. The scientifically correct statement is: *a simple non-learning residual, added to the
> framework in EXP-0012, catches most mismatch.* This distinction is preserved in all subsequent
> documentation, and it makes the "ML not needed" conclusion weaker, not stronger.

**Decision gate: A *and* D simultaneously** — the framework is mostly robust, and dangerously
non-robust in a specific, physically meaningful minority of cases.

> **Headline.** A simple non-learning statistic — the χ² residual, added to the framework in this
> experiment — catches hypothesis-space mismatch in 47–83% of cases, and it does so **exactly
> when a closed-form threshold predicts (1502 of 1512 cells, 99.3%)**. But in **5.8% of all cells
> and 16.7% at full observation** the system is *confidently wrong and the residual does not
> notice*. Every one of six unseen faults produces at least one such case that **persists at the
> full 18 s window**. The sharpest: a partially blocked pitot line is diagnosed as **no fault at
> all**, with confidence rising from 0.13 to 0.99 as more data arrives.

---

## 1. Research question

> When an aircraft experiences a fault absent from the diagnostic hypothesis library, does a
> physics-based diagnostic system recognise that its hypotheses are inadequate, or does it
> confidently assign the observation to an incorrect known fault?

## 2. Two facts established analytically before running

### FACT 1 — the posterior cannot express hypothesis-space mismatch

$P(j\mid y)=\exp(\mathrm{LL}_j)/\sum_k\exp(\mathrm{LL}_k)$. A uniform lack of fit adds the same
constant to every log-likelihood and **cancels in the softmax**. Verified numerically in the pilot:
displacing the unseen fault from *every* known hypothesis by a large orthogonal amount left
confidence at **1.0000 → 1.0000** while the residual rose **2637 → 7634**.

**Consequence:** "the classifier is confidently wrong about unseen faults" is close to mathematically
guaranteed. Reporting only that would satisfy the letter of the question while evading §25's warning.
The live question is the second one.

### FACT 2 — the residual is a χ² goodness-of-fit test with a computable threshold

$R=\min_j\lVert y-w_j\rVert^2/\eta^2 \sim \chi^2(KN)$ under a correct hypothesis, and
$\chi^2(KN)+\lVert\Delta_{\min}\rVert^2/\eta^2$ under mismatch. Mismatch is detectable iff

$$\lVert\Delta_{\min}\rVert/\eta \;>\; \sqrt{z_\alpha}\,(2KN)^{1/4}
\qquad(\text{9.2 at 0.5 s, 13.0 at 2 s, }\mathbf{22.4}\text{ at 18 s})$$

**This is a non-learning statistic, added to the framework in this experiment.** Gate D was
therefore a live possibility from the outset, and was pre-registered as such. It did not exist in
EXP-0010 or EXP-0011; see the correction note above.

## 3. Unseen-fault taxonomy

Six mechanisms, each physical, each absent from $H_{\text{known}}$ (F0; bias/scale/drift/stuck on
$\{q,a_z,V_t,\alpha\}$; elevator effectiveness F6):

| ID | Mechanism | Cat. | Why outside the library |
|---|---|---|---|
| UF-001 | AoA vane stiction | A | `F4` is a *total* freeze; this is a partial, signal-dependent one |
| UF-002 | Rate-gyro saturation | A | `F2` is a linear scale error; this is a nonlinearity |
| UF-003 | Pitot line partial blockage (pneumatic lag) | A | No dynamic/filtering fault exists |
| UF-004 | Static-port blockage | B | Cross-channel; **no library fault acts on altitude at all** |
| UF-005 | Pitch static-stability loss | C | `F6` changes *control* effectiveness, not *stability* |
| UF-006 | Airframe icing drag rise | C | No aerodynamic-degradation hypothesis exists |

All six are detectable: deflections from nominal 16.6–479.7 against a floor of 4.65.

**A physical insight found during the pilot and worth recording:** a pneumatic lag is a *continuum
between two library hypotheses* — τ→0 is no fault, τ→∞ is a stuck sensor. It can never be far from
the library, which makes UF-003 the strongest near-manifold case rather than a weak one. Its
deviation saturates at ~2σ per sample even at τ = 8 s.

## 4. Control (Case A)

**56 of 56 cells correct**, with normalised residual **1.000** — exactly the χ² expectation for a
true hypothesis. Any OOD failure below is therefore not general classifier failure.

## 5. Primary results

### Failure-mode census (the three modes kept strictly separate, spec §8)

| Subset | poorly explained (caught) | not yet detectable | ambiguous | **confidently wrong** |
|---|---|---|---|---|
| All 1512 cells | 47.4% | 39.9% | 6.9% | **5.8%** |
| η=1, magnitude ×1 (168) | 57.1% | 31.0% | 1.2% | **10.7%** |
| Full 18 s window (216) | 66.7% | 17.1% | 5.6% | **10.6%** |
| Full window, η=1, ×1 (24) | 83.3% | — | — | **16.7%** |

### The two sharpest cases (FC-1, η=1, nominal magnitude)

**UF-003 — pitot lag diagnosed as NO FAULT.** The classifier's confidence in `F0` rises from
**0.133 at 0.25 s to 0.993 at 18 s**, while the χ² test rejects only **14%**. A real fault, growing
confidence that nothing is wrong, and the fit statistic silent.

| Window | 0.25 s | 1 s | 2 s | 5 s | 10 s | 18 s |
|---|---|---|---|---|---|---|
| winner | F3_α | **F0** | F4_α | **F0** | **F0** | **F0** |
| confidence | 0.133 | 0.146 | 0.159 | 0.930 | 0.939 | **0.993** |
| χ² rejects | 0.008 | 0.008 | 0.008 | 0.019 | 0.191 | 0.142 |

**UF-005 — pitch-stability loss diagnosed as elevator-effectiveness loss (`F6`).** Confidence is
**1.0000 at every window from 0.25 s**, and the χ² test rejects only 2–5% for the first 2 s.
Physically these are different failures with different maintenance actions: one is a damaged
stabiliser or a shifted centre of gravity, the other a control-surface problem.

### Persistent danger

**23 cells remain confidently wrong at the full 18 s window**, and **every one of the six unseen
faults contributes at least one.** More observation does not reliably fix it.

| Unseen fault | persistent cells | wrong diagnosis given | confidence | χ² rejects |
|---|---|---|---|---|
| UF-003 | 8 | `F0` (no fault) | 0.993–1.000 | 0.020–0.142 |
| UF-006 | 6 | `F2_Vt`, `F2_α` | 0.981–1.000 | 0.025–0.236 |
| UF-001 | 3 | `F0`, `F2_α` | 1.000 | 0.216–0.225 |
| UF-004 | 3 | `F2_Vt`, `F3_Vt` | 0.995–1.000 | 0.027–0.090 |
| UF-005 | 2 | `F6` | 1.000 | 0.014–0.049 |
| UF-002 | 1 | `F0` | 0.981 | 0.069 |

## 6. Test of the pre-registered prediction P2

> The χ² residual detects mismatch exactly when the nearest-known distance exceeds
> $\sqrt{z_\alpha}(2KN)^{1/4}$.

**Agreement: 1502 of 1512 cells — 99.3%.** The closed form, derived before any simulation and not
refitted, predicts when the framework catches itself and when it does not.

This is the strongest quantitative result in the experiment, and it is *constructive*: it says
exactly which unseen faults are dangerous — those whose nearest-known distance falls below the
threshold, i.e. those sitting on or near a known manifold.

## 7. Nearest-manifold analysis

False confidence tracks proximity to a known manifold (FIG-014). The dangerous cells are precisely
those with small nearest-known distance:

| Fault | nearest distance at 18 s | threshold | caught? |
|---|---|---|---|
| UF-003 | 16.6 | 22.4 | **no** |
| UF-001 | 31.4 | 22.4 | yes (98%) |
| UF-005 | 68.0 | 22.4 | yes (100%) |
| UF-002 | 166.9 | 22.4 | yes (100%) |
| UF-004 | 207.0 | 22.4 | yes (100%) |
| UF-006 | 375.9 | 22.4 | yes (100%) |

At short windows UF-001, UF-002, UF-003 and UF-005 all have nearest distances **below** threshold —
which is why the dangerous mode concentrates there.

## 8. Validity attacks

| ID | Attack | Result |
|---|---|---|
| **W-A** | Nearest-known (UF-003, UF-005) | **The main result survives and is strongest here** — these are the persistent cases |
| **W-B** | Easy OOD (UF-004, UF-006) | **Rejected immediately** by the existing residual, 100% at every window. Obvious OOD needs no ML |
| **W-C** | Pre-manoeuvre windows | Correctly classified as *not yet detectable*, not as confident misdiagnosis. **Apparent OOD confidence is not merely non-detection** — the dangerous cells sit at 5–18 s, after the manoeuvre |
| **W-D** | η ∈ {0.1, 1, 10}, magnitude ×{0.5, 1, 2} | Effect survives; the persistent set shifts but never empties |
| **W-E** | Known-fault control | 56/56 correct, residual 1.000 |
| **W-F** | Envelope validity | 0 of 72 trajectories excluded; all within α ≤ 25° |

Condition dependence is weak: 4–6 confidently-wrong cells of 42 at each of the four conditions.

## 9. FACTS

- Control: 56/56 known-fault cells correctly diagnosed; normalised residual 1.000.
- Census over 1512 cells: 47.4% caught by the residual, 39.9% not yet detectable, 6.9% ambiguous,
  **5.8% confidently wrong and undetected**.
- At full window, reference noise, nominal magnitude: **16.7% (4 of 24) confidently wrong**.
- 23 cells confidently wrong at 18 s; all six unseen faults represented.
- UF-003 confidence in `F0`: 0.133 → 0.993 across the window sweep; χ² rejects 14%.
- UF-005 confidence in `F6`: 1.0000 at every window; χ² rejects 2–5% up to 2 s.
- P2 agreement: 1502/1512 = 99.3%.
- Nearest-known distances at 18 s: 16.6 (UF-003) to 375.9 (UF-006); threshold 22.4.

## 10. CALCULATIONS

- χ² detection threshold $\sqrt{z_{0.01}}(2KN)^{1/4}$: 7.8 / 9.2 / 13.0 / 16.3 / 22.4 at
  0.25 / 0.5 / 2 / 5 / 18 s.
- Pilot sizing: worst-case binomial half-width 0.01 at 95% requires N = 9604 → **N = 10 000 chosen**.
- Exact Monte Carlo verified against direct full-dimensional simulation at η = 1 and η = 10.

## 11. OBSERVATIONS

- The dangerous cells are concentrated at **intermediate-to-long windows** (5–18 s), *after* the
  manoeuvre — not at short windows where non-detection dominates.
- The winning wrong hypothesis is frequently `F0`, i.e. **"no fault"**. Of the 23 persistent cases,
  12 diagnose a genuinely faulted aircraft as healthy.
- Confidence and correctness diverge cleanly: confidence rises monotonically with window while the
  diagnosis stays wrong.

## 12. INTERPRETATIONS

*(Contestable.)*

- **The framework is mostly self-protecting, once the residual is added.** A single non-learning
  statistic — introduced here, not inherited — catches most
  hypothesis-space mismatch, with no ML, and its failure boundary is analytically predictable. That
  is a stronger form of robustness than "we trained a detector".
- **Where it fails, it fails silently and dangerously**, and the failures are exactly the
  near-manifold cases — the ones a designer is least likely to anticipate, because they look like
  faults the library *does* contain.
- **The most dangerous single behaviour is diagnosing a faulted aircraft as healthy with rising
  confidence.** That is not a calibration problem; it is a support problem, continuous with
  EXP-0011's finding that a wrong hypothesis support worsens with more data.

## 13. HYPOTHESES (suggested, not established)

- The χ² threshold gives a *design rule*: any candidate fault mechanism whose nearest-known distance
  falls below $\sqrt{z_\alpha}(2KN)^{1/4}$ is a blind spot of that library. This is checkable at
  design time, before flight, without ML.
- An abstention rule built on the residual would capture most of the available benefit; the residual
  is already sufficient for 47–83% of cases.

## 14. LIMITATIONS

1. The classifier knows the known-fault template families exactly (TV-M5); only the *true* fault is
   outside the library.
2. Six unseen faults on one self-implemented aircraft (TV-D10), one excitation, equal class priors.
3. The χ² test uses a normal approximation to the χ² tail — adequate at $KN\ge338$ but approximate.
4. "Confidently wrong" is judged at τ = 0.95, reused from EXP-0010/0011 rather than tuned here.
5. Unseen-fault magnitudes are experimental, not physically calibrated.
6. No claim about real sensors, real aircraft, safer autonomy or operational applicability.

## 15. Decision gate

**Gate D holds for the majority.** The existing physics-based framework indicates poor fit for most
unseen faults, via a non-learning statistic added in this experiment, with an analytically
predictable boundary. **An
ML OOD detector is not needed for those cases and inventing one would be unjustified.**

**Gate A holds for a specific minority.** At least four physically meaningful unseen faults produce
high confidence in a wrong known fault, with sufficient observable evidence, surviving every validity
attack, and **persisting at full observation**. UF-003 and UF-005 are the clearest.

The spec permitted both, and both are supported. Forcing a single verdict would misrepresent the
evidence.

**§25's threshold is met.** This is not "the classifier gets unseen faults wrong" — it is *the
classifier becomes more confident in a wrong diagnosis as evidence accumulates, while the
goodness-of-fit statistic remains silent.*

## 16. Implications for AURA

1. **A reproducible reliability problem now exists**, measured rather than assumed — the first time
   in this project that a hypothesised failure mode has actually appeared under adversarial test.
2. **But the right response is not immediately ML.** The residual already catches 47-83% of mismatch
   cases. The scientific target is now narrow and well defined: *near-manifold unseen faults, where
   the residual is provably blind.*
3. **The threshold is a design tool.** Because the failure boundary is closed-form, a library's blind
   spots can be enumerated at design time — arguably more valuable than a learned detector, and
   certainly more auditable.
4. **Continuity with EXP-0011.** Both experiments find the same underlying mechanism: a wrong
   hypothesis *support* produces confident, worsening error. EXP-0011 measured it for magnitude;
   EXP-0012 measures it for the taxonomy, and finds it larger and persistent.

## 17. Recommended next experiment

**EXP-0013 — can anything help where the residual is provably blind?**

Scope it to the near-manifold regime only ($\lVert\Delta_{\min}\rVert/\eta$ below threshold), and ask
whether *any* additional information resolves it: a second excitation designed to increase separation
(cheap, non-ML, and directly suggested by the fact that isolation is excitation-driven); additional
sensors; or a longer horizon. **Only if all non-learning options fail is an uncertainty/ML approach
scientifically justified** — and by then the target would be precisely defined rather than assumed.

**Not recommended:** building an ML OOD detector now. The evidence says 47–83% of the problem needs
no such thing, and the remainder has not yet been shown to be beyond non-learning methods.
