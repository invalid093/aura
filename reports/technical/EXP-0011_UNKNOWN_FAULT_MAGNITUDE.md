# EXP-0011 — Unknown Fault Magnitude and Composite-Hypothesis Uncertainty

**Experiment:** EXP-0011 · **Date:** 2026-09-08 · **Status:** COMPLETED
**Pre-registration:** [`experiments/EXP-0011/experiment_spec.md`](../../experiments/EXP-0011/experiment_spec.md)
**Results:** `results/validation/EXP-0011/exp0011_results.json` · **Data:** `DS-0001` + `DS-0002`
**Extends, does not replace:** [EXP-0010](EXP-0010_MEASUREMENT_UNCERTAINTY.md)

> **Headline.** Not knowing the fault magnitude costs almost nothing — at most 3.3 percentage
> points of class-isolation accuracy, falling to **0.0001** with a full observation window.
> **Being *wrong* about the magnitude is 1000× worse, and unlike every other effect measured in
> this project, it gets worse with more data** (−0.065 at 0.25 s worsening to −0.133 at 18 s).
> The experiment was designed to test whether uncertainty about magnitude creates ambiguity.
> It found that it barely does, and that misplaced confidence does.

---

## 1. Research question

> How does fault-isolation performance change when the diagnostic system does not know the
> magnitude of the fault?

Fault magnitude is treated as an **unknown nuisance parameter**, distinct from measurement noise,
model uncertainty and unknown onset. The objective is fault-**class** isolation with magnitude
marginalised out: $p(y\mid\text{class}) = \sum_m p(y\mid\text{class},m)\,p(m)$.

## 2. Motivation from EXP-0010

EXP-0010 found essentially perfect isolation at reference sensor noise, but its classifier knew both
the fault templates and the fault magnitude. Magnitude was the largest untested assumption, and one
that can only *increase* ambiguity: the EXP-0002 closed form already proves that a bias fault and a
scale fault on a regulated channel become identical when $b=(\kappa-1)V_0$, so with magnitude free
the two classes genuinely intersect.

## 3. Hypotheses

| ID | Statement | Outcome |
|---|---|---|
| EH-1 | Free magnitude creates cross-class overlap absent at fixed magnitude | **Supported, but small and confined to specific pairs** |
| EH-2 | Some overlap **persists** as the window grows | **Not supported** — every pair separates by 18 s |
| EH-3 | Unknown magnitude is a larger uncertainty source than reference sensor noise | **Not supported** — noise dominates by 2.5–60× |

## 4. The pre-registered closed-form prediction

Derived before any EXP-0011 simulation: on a regulated channel with magnitude free, minimising over
the bias leaves residual $-(\kappa-1)(V(t)-\overline V)$, so the classes separate only by the
**fluctuation** of airspeed — a 12–63× reduction versus the fixed-magnitude case, and **exactly zero
in any window preceding the excitation**.

| Condition | mean $V$ | std $V$ | $d$ magnitude known | $d$ magnitude free | reduction |
|---|---|---|---|---|---|
| FC-1 | 45.07 | 0.4147 | 0.987 | 0.083 | 11.9× |
| FC-2 | 28.04 | 0.3778 | 4.392 | 0.076 | 58.1× |
| FC-3 | 35.05 | 0.3809 | 2.990 | 0.076 | 39.2× |
| FC-5 | 28.03 | 0.3465 | 4.394 | 0.069 | 63.4× |

## 5. Diagnostic knowledge conditions

| Case | Classifier knows | Truths drawn from |
|---|---|---|
| **A** | The exact magnitude | Full grid |
| **B** | $m\in[0.5,2]$ (uniform) | **Full grid** — so the prior excludes the truth 4/9 of the time |
| **C** | $m\in[0.25,4]$ (uniform) | Full grid |
| **B′** *(exploratory, post-hoc)* | $m\in[0.5,2]$ | $[0.5,2]$ — matched |

**Case B as pre-registered measures prior *misspecification*, not bounded knowledge**, because
truths span the full grid. That was not the intent, but it turned out to be the most informative
condition in the experiment. B′ was added afterwards, clearly labelled, to answer the intended
question.

## 6. Experimental design

4 flight conditions × 18 classes × 9 magnitudes × 7 windows × 3 noise levels × 3 knowledge cases,
20 000 Monte Carlo replications per cell. 416 new simulations; the $m=1$ slice reused from DS-0001.
Runtime 1515 s. **FC-4 not resurrected** (FAIL-0001).

## 7. Flight conditions

FC-1 (1000 m, 45 m/s, α = −0.88°), FC-2 (1000 m, 28 m/s, α = 5.15°), FC-3 (5000 m, 35 m/s,
α = 4.83°), FC-5 (5000 m, 28 m/s, α = 10.15°).

## 8. Fault classes

18: F0 nominal; F1 bias, F2 scale, F3 drift, F4 stuck on each of $\{q, a_z, V_t, \alpha\}$;
F6 elevator effectiveness. **F4 has no magnitude parameter** — freezing a signal is the same fault
at any nominal magnitude — so it contributes one template per channel, not nine.

## 9. Magnitude ranges

$m/m_{\text{nom}} \in \{0.25 … 4\}$, √2-spaced, 9 levels, spanning a factor of 16. **Experimental
range, not physically calibrated.** Positive only; zero excluded. Seven templates were excluded by
the pre-declared validity rule (divergence or α > 25°), all at magnitudes ≥ 2.83×.

## 10. Observation windows

0.25, 0.5, 1, 2, 5, 10, 18 s after onset. Fault onset is 2 s; the excitation doublet runs 4–10 s, so
windows ≤ 2 s are entirely **pre-manoeuvre**.

## 11. Noise assumptions

Additive Gaussian white, per-channel σ from the EXP-0002 synthetic MEMS-grade spec, multiplier
η ∈ {0.1, 1, 10}. σ provenance: synthetic and representative; **not a claim about a real sensor**.

## 12. Statistical methodology

Bayes-optimal classifier with known template *families*; magnitude marginalised by log-sum-exp over
the prior. The Monte Carlo reduces exactly to the template space: with $y = w_i + \eta z$, the score
of template $j$ is $\lVert w_j\rVert^2 - 2M_{ij} - 2\eta t_j$ where $t = z\!\cdot\!w \sim N(0,M)$,
which depends on neither the true template nor η — so one draw serves every cell.

**The primary manifold measure is the *continuous* minimum over magnitude, not the grid minimum.**
Each class family is fitted as $w(m)\approx w_0 + m\,u$ and the minimum distance between two
segments computed in closed form. Fit residuals: mean 0.13–0.34%, max 4.28%.

---

## 13. Results

### 13.1 The cost of not knowing the magnitude (Case A − Case C, η = 1)

| Window | FC-1 | FC-2 | FC-3 | FC-5 | mean |
|---|---|---|---|---|---|
| 0.25 s | +0.0047 | +0.0233 | +0.0689 | +0.0204 | **+0.0293** |
| 0.5 s | +0.0181 | +0.0267 | +0.0672 | +0.0215 | **+0.0334** |
| 2 s | +0.0108 | +0.0109 | +0.0258 | +0.0115 | +0.0147 |
| 5 s | +0.0042 | +0.0030 | +0.0053 | +0.0018 | +0.0036 |
| 18 s | +0.0001 | +0.0001 | +0.0001 | +0.0000 | **+0.0001** |

**Widening the magnitude prior to a 16× range costs at most 3.3 points, and essentially nothing once
the manoeuvre has been observed.**

### 13.2 The cost of being *wrong* about the magnitude (Case B − Case C, η = 1)

| Window | mean loss |
|---|---|
| 0.25 s | −0.0649 |
| 1 s | −0.0944 |
| 2 s | −0.1076 |
| 5 s | −0.1310 |
| 18 s | **−0.1329** |

**This is the central result.** A prior that excludes the true magnitude costs 6.5–13.3 points —
4× to 1000× the cost of simple uncertainty — and **the penalty grows monotonically with observation
length**. Every other effect measured in this project shrinks with more data; this one does not.

The mechanism is straightforward and worth stating because it generalises: as the window lengthens,
the likelihood sharpens onto a hypothesis set that does not contain the truth, so additional evidence
increases confidence in a wrong class rather than correcting it. More data cannot repair a support
error.

*(Case B′, with truths matched to the prior, gives 0.709 / 0.866 / 1.000 at 0.5 / 2 / 18 s. It sits
slightly below Case C at short windows because restricting truths removes the easy large-magnitude
cases, so B′ and C are not a like-for-like comparison. It does reach 1.000 at the full window,
confirming that bounded-but-correct knowledge behaves like Case C.)*

### 13.3 Class-isolation performance

| Condition | 0.5 s (A / C) | 2 s (A / C) | 18 s (A / C) |
|---|---|---|---|
| FC-1 | 0.747 / 0.729 | 0.886 / 0.875 | 1.000 / 1.000 |
| FC-2 | 0.761 / 0.735 | 0.890 / 0.879 | 1.000 / 1.000 |
| FC-3 | 0.762 / 0.695 | 0.890 / 0.864 | 1.000 / 1.000 |
| FC-5 | 0.775 / 0.753 | 0.898 / 0.886 | 1.000 / 1.000 |

## 14. Fault-manifold analysis

Two analyses are reported because the pre-registered one has a flaw found after the fact.

**Pre-registered (detectability at the full window).** At 0.5 s this reports 17–24 "structurally
intersecting" pairs — but the worst pairs are all *fault versus nominal* (F0/F2_q, F0/F4_az). That
is **non-detection, not isolation ambiguity**: in trim, pitch rate is identically zero and normal
acceleration is exactly constant, so a scale fault on $q$ and a stuck $a_z$ sensor produce *exactly*
no change until the aircraft manoeuvres. The pre-registered floor, evaluated at the full window,
does not screen these out.

**Post-hoc (detectability within the window).** Restricting to faults actually visible in the window
isolates the genuine isolation question:

| Condition | 0.5 s | 2 s | 5 s | 18 s |
|---|---|---|---|---|
| FC-1 | F1_Vt/F2_Vt **0.569** | F1_Vt/F2_Vt 0.909 | none | **none** |
| FC-2 | F1_α/F2_α **0.538**, F1_Vt/F2_Vt 0.546 | F1_α/F2_α 0.555 | F1_α/F2_α 0.986 | **none** |
| FC-3 | F1_α/F2_α **0.543**, F1_Vt/F2_Vt 0.551 | F1_α/F2_α 0.560 | none | **none** |
| FC-5 | F1_α/F2_α **0.525**, F1_Vt/F2_Vt 0.554 | F1_α/F2_α 0.539 | F1_α/F2_α 0.916 | **none** |

**Every overlapping pair is bias versus scale on the same channel**, at essentially chance
(P = 0.52–0.57) before the manoeuvre — and **every one is fully resolved by 18 s.**

Classification of the relationships, against the pre-declared bands: F1/F2 pairs on $V_t$ and α are
**structurally intersecting** pre-manoeuvre and **clearly separated** post-manoeuvre. All other pairs
are clearly separated throughout. No pair is *persistently* overlapping.

## 15. Analytical crossing analysis

The prediction was **tested, not refitted**.

| Condition | 0.5 s pred / meas | 2 s pred / meas | 18 s pred / meas |
|---|---|---|---|
| FC-1 | 0.00 / 0.35 | 0.00 / 2.67 | 3.52 / 20.47 |
| FC-2 | 0.00 / 0.23 | 0.00 / 2.35 | 3.21 / 14.52 |
| FC-3 | 0.00 / 0.26 | 0.00 / 1.76 | 3.23 / 12.79 |
| FC-5 | 0.00 / 0.27 | 0.00 / 1.57 | 2.94 / 14.41 |

**Pearson r = 0.973 across all 28 cells.** The closed form predicts exactly zero pre-manoeuvre
(because std(V) = 0 in trim); the measured value is 0.23–0.35, i.e. still near chance
(P = 0.55–0.57), the difference being closed-loop propagation into the other twelve channels. The
prediction is a **lower bound** that tracks the measurement well and correctly identifies *where*
discrimination fails.

## 16. Flight-condition comparison

The magnitude penalty is condition-dependent and **more strongly so than anything in EXP-0010**:
at 0.25 s the Case A−C gap is 0.0047 at FC-1 but 0.0689 at FC-3, a **14.7× spread** (EXP-0010's
condition dependence was 1.83×). FC-1, with trim α ≈ −0.9°, has the smallest penalty because a scale
fault on a near-zero α is invisible there, so fewer classes are in play at all.

## 17. Sensitivity analysis

| ID | Attack | Result |
|---|---|---|
| **W-A** | Grid vs continuous minimum | Median ratio **1.00**, but **max 7.5–19.9×**. The grid is adequate for typical pairs and badly wrong for exactly the near-intersecting pairs that matter |
| **W-B** | Magnitude range [0.5,2] vs [0.25,4] | See §13.2 — the dominant result |
| **W-C** | Observation window | Built into the design; overlap is fully transient |
| **W-D** | Noise η ∈ {0.1, 1, 10} | See §18 |
| **W-E** | Linearity of magnitude families | Mean residual 0.13–0.34%, max 4.28%. Separations below ~4% of family norm are not resolvable |
| **W-G** | Detectability floor on/off | Minimum unchanged (0.000 either way), because F0-versus-invisible-fault is exactly coincident regardless |

## 18. Validity attacks — which uncertainty dominates

At a 2 s window, mean over conditions:

| η | magnitude known | magnitude unknown | cost of unknown magnitude |
|---|---|---|---|
| 0.1 | 0.9040 | 0.9008 | +0.0032 |
| 1 | 0.8909 | 0.8761 | +0.0147 |
| 10 | 0.6983 | 0.6166 | **+0.0816** |

Raising noise 100× (η 0.1 → 10) costs **0.206**; not knowing magnitude costs 0.003–0.082.
**Measurement noise dominates by 2.5–60×** — but the two **interact**: the magnitude penalty grows
25× as noise rises, because noise blurs the evidence that would otherwise pin the magnitude down.

## 19. Facts

- Case A − Case C: +0.0293 (0.25 s) → +0.0001 (18 s), mean over conditions.
- Case B − Case C: −0.0649 (0.25 s) → −0.1329 (18 s); **monotonically worsening**.
- $P_{\text{class}}$ reaches 1.000 at 18 s in every condition and every knowledge case except B.
- All overlapping visible pairs at ≤ 2 s are bias-vs-scale on the same channel, at P = 0.52–0.57.
- No pair remains overlapping at 18 s at any condition.
- Analytic prediction vs measurement: r = 0.973 over 28 cells.
- Grid overstates near-intersection separation by up to 19.9×.
- Linear magnitude-family fit residual: mean 0.13–0.34%, max 4.28%.
- Seven templates excluded by the pre-declared validity rule.

## 20. Calculations

- Closed-form crossing: $b^{*}=(\kappa-1)\overline V$; residual RMS $=(\kappa-1)\,\mathrm{std}(V)$;
  reduction 11.9–63.4× versus fixed magnitude.
- Condition dependence of the magnitude penalty: 0.0689 / 0.0047 = **14.7×**.
- Noise vs magnitude at 2 s: 0.206 versus 0.003–0.082 → noise dominant by 2.5–60×.

## 21. Observations

- Pre-manoeuvre, multiplicative and stuck faults on a non-varying signal are **exactly**
  unobservable — a mathematical identity, not a numerical artefact.
- The ambiguity that free magnitude creates is concentrated in one mechanism pair (bias vs scale)
  and one situation (before excitation).
- The classifier reaches 1.000 only after the manoeuvre; isolation is driven by **excitation**, not
  elapsed time — consistent with EXP-0010.

## 22. Interpretations

*(Contestable.)*

- **Unknown magnitude is not the hidden assumption that rescues AURA's motivation.** It was the
  leading candidate; it costs almost nothing.
- **Support misspecification is a qualitatively different failure.** It is the only effect measured
  in this project that *worsens* with more evidence, because a sharper likelihood over a wrong
  support cannot self-correct. Any system that marginalises over a bounded fault model inherits this.
- The transient bias-vs-scale ambiguity is genuine but narrow, and resolved by manoeuvring — which
  makes it a *decision-timing* problem, not a fundamental diagnosability limit.

## 23. Hypotheses (suggested, not established)

- The same support-misspecification effect will apply to the fault *taxonomy* itself: a fault class
  absent from the model should produce confident, wrong, and increasingly confident answers.
  **This is the natural next experiment and is a much larger version of the same effect.**
- Excitation design, not sensor quality or estimator sophistication, may be the main lever on
  time-to-isolation.

## 24. Limitations

1. **Template families still assumed exactly known** (TV-M5). Only magnitude was freed.
2. Magnitude range is experimental, positive-only; a negative bias could intersect other classes.
3. Linear magnitude families: separations below ~4% of family norm are unresolvable.
4. One self-implemented aircraft (TV-D10); one excitation; equal class priors.
5. The pre-registered detectability floor conflates non-detection with mis-isolation at short
   windows; corrected post-hoc, but the pre-registration was flawed.
6. Case B measures prior misspecification rather than the bounded knowledge it was meant to measure.
7. No claim about real sensors, real aircraft, safer autonomy, or operational applicability.

## 25. Threats to validity

Carried forward: TV-N1, TV-D1, TV-D9, TV-D10, TV-M5. **New: TV-M6 — support misspecification.** The
finding that a wrong hypothesis support degrades with more data is measured here for magnitude only;
whether it generalises to the fault taxonomy is untested and is the most consequential open question
in the project.

## 26. Decision gate

| Outcome | Verdict |
|---|---|
| **A — known magnitude was the main hidden assumption** | **NOT SUPPORTED.** Cost ≤ 3.3 points, → 0.0001 at full window |
| **B — magnitude uncertainty is manageable; problem remains transient** | **SUPPORTED, dominant.** All overlap resolves by 18 s |
| **C — fundamental cross-class ambiguity exists** | **NOT SUPPORTED** at full observation. Supported *only* pre-manoeuvre, where it is exact and at chance |
| **D — model assumptions dominate** | **PARTIAL.** Excitation timing determines when ambiguity resolves; linear-fit residual bounds resolution |
| **E — mixed across fault classes** | **SUPPORTED.** Two of eighteen classes (bias/scale on regulated channels) behave completely differently from the rest |

### Outside the pre-declared categories

**Being wrong about the magnitude is far more damaging than being uncertain about it, and it is the
only effect in this project that worsens with more observation.** None of A–E anticipated a
distinction between uncertainty and misspecification.

## 27. Implications for AURA

1. **The composite-hypothesis rescue fails.** Unknown magnitude was the strongest remaining candidate
   for restoring AURA's motivating ambiguity. It does not: at reference noise with a full window,
   isolation is still perfect.
2. **The problem has moved again — and this time somewhere more interesting.** Across EXP-0010 and
   EXP-0011 the recurring finding is that AURA's diagnostic problem is not *uncertainty* but
   *misplaced confidence*: the argmax rule with equal priors false-alarms 89% of the time under
   elevated noise (EXP-0010), and a prior that excludes the truth becomes more confidently wrong with
   more data (EXP-0011). **That is a much better-grounded motivation for an abstention mechanism
   than diagnostic ambiguity ever was — and it was measured, not assumed.**
3. **Pre-manoeuvre, several faults are exactly unobservable.** Not hard to see — *identically*
   invisible. Combined with EXP-0010's 5 s time-to-isolation, this says the aircraft's first seconds
   after a fault are genuinely information-poor, irrespective of sensors or algorithms.
4. **What AURA may not claim:** that unknown fault magnitude creates meaningful diagnostic ambiguity.
   On this evidence it does not.

## 28. Recommended next experiment

**EXP-0012 — an unmodelled fault class (support misspecification of the taxonomy).**

Rationale: §13.2 shows that a hypothesis support excluding the truth produces errors that *grow*
with evidence. That was measured for a magnitude sub-range. The taxonomy version — a fault the model
has never seen — is the same mechanism at a much larger scale, is the assumption every diagnostic
system in this literature makes, and is directly testable with the existing machinery by holding out
one class and measuring how confidently the classifier misassigns it as the window grows.

**This is the first experiment in the sequence whose expected outcome genuinely supports AURA's
premise** — which is a reason to design it carefully rather than optimistically.

Deliberately **not** recommended: any learning component, uncertainty estimator or decision layer.
Three experiments have now failed to find the ambiguity AURA was designed around; a fourth should
test the mechanism that has actually shown itself, not build on the ones that have not.
