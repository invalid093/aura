# EXP-0011 — Research Handoff

**Self-contained. No attachments required. Written for independent critical review.**

**Date:** 2026-09-08 · **Experiment:** EXP-0011 · **Status:** COMPLETED

---

## TASK

Determine whether uncertainty in fault *magnitude* creates meaningful fault-class ambiguity, and
whether it changes EXP-0010's conclusion. Magnitude was the largest remaining assumption: EXP-0010's
classifier knew both the fault templates and their magnitudes.

## OBJECTIVE

Treat fault magnitude as an unknown **nuisance parameter** — not as extra noise — and measure
fault-class isolation with magnitude marginalised out.

## WORK PERFORMED

- Derived a closed-form prediction **before simulating**: with magnitude free, a bias and a scale
  fault on a regulated channel separate only by the *fluctuation* of the signal, a 12–63× reduction,
  and exactly zero before the aircraft manoeuvres.
- Pre-registered the magnitude model, three knowledge conditions, metrics, bands and attacks.
- Generated a 9-level magnitude grid (416 new simulations; the m = 1 slice reused from DS-0001).
- Implemented a **continuous** manifold-intersection calculation, because a discrete grid can only
  sample near an intersection and would make the headline an artefact of grid resolution.
- Ran 4 conditions × 7 windows × 3 knowledge cases × 3 noise levels, 20 000 replications per cell.
- Ran six validity attacks; added two post-hoc analyses after finding flaws in my own design.

## KEY FINDINGS

1. **Not knowing the magnitude costs almost nothing.** Widening the prior to a 16× range costs at
   most **3.3 points** of class-isolation accuracy, falling to **0.0001** at the full window.
   The composite-hypothesis rescue of AURA's motivation **fails**.
2. **Being *wrong* about the magnitude costs 4–1000× more — and the penalty GROWS with observation.**
   A prior excluding the truth costs 0.065 at 0.25 s, worsening monotonically to **0.133 at 18 s**.
   Every other effect measured in this project shrinks with more data; this one does not, because a
   sharpening likelihood over a wrong support cannot self-correct.
3. **All magnitude-induced overlap is transient.** Every overlapping pair is resolved by 18 s at
   every condition. No fundamental cross-class ambiguity was found.
4. **Every overlapping pair is bias-versus-scale on the same channel**, at essentially chance
   (P = 0.52–0.57) before the manoeuvre — exactly as the closed form predicted.
5. **Pre-manoeuvre, some faults are *exactly* unobservable.** In trim, pitch rate is identically zero
   and normal acceleration exactly constant, so a scale fault on q and a stuck az sensor produce
   *literally* no change. A mathematical identity, not a numerical artefact.
6. **Measurement noise dominates unknown magnitude by 2.5–60×** — but they interact: the magnitude
   penalty grows 25× as noise rises.
7. **Analytic prediction confirmed at r = 0.973** over 28 cells, not refitted.

## FACTS

- Case A − Case C (cost of unknown magnitude), mean over conditions: +0.0293 (0.25 s), +0.0334
  (0.5 s), +0.0147 (2 s), +0.0036 (5 s), **+0.0001 (18 s)**.
- Case B − Case C (cost of a prior excluding the truth): −0.0649 (0.25 s), −0.0944 (1 s), −0.1076
  (2 s), −0.1310 (5 s), **−0.1329 (18 s)** — monotonically worsening.
- $P_{class}$ at 18 s = 1.000 for every condition in Cases A, C and B′; 0.847–0.890 in Case B.
- Overlapping visible pairs at 0.5 s: FC-1 F1_Vt/F2_Vt (0.569); FC-2 F1_α/F2_α (0.538), F1_Vt/F2_Vt
  (0.546); FC-3 F1_α/F2_α (0.543), F1_Vt/F2_Vt (0.551); FC-5 F1_α/F2_α (0.525), F1_Vt/F2_Vt (0.554).
- At 18 s: zero overlapping pairs at every condition.
- Noise sweep at 2 s: η 0.1 → 10 costs 0.206; unknown magnitude costs 0.003 / 0.015 / 0.082 at
  η = 0.1 / 1 / 10.
- Condition dependence of the magnitude penalty: 0.0047 (FC-1) to 0.0689 (FC-3) — **14.7×**.
- Grid overstates near-intersection separation by median 1.00×, **max 19.9×**.
- Linear magnitude-family fit residual: mean 0.13–0.34%, max 4.28%.
- 7 templates excluded by the pre-declared validity rule (α > 25° or divergence), all at m ≥ 2.83.

## CALCULATIONS

- Closed form: $b^{*}=(\kappa-1)\overline V$, residual RMS $=(\kappa-1)\,\mathrm{std}(V)$; reduction
  11.9× (FC-1) to 63.4× (FC-5) versus fixed magnitude.
- Predicted vs measured $D_{\min}$ for F1_Vt/F2_Vt: r = 0.973 over 28 cells; predicted values are
  lower bounds (they use one channel; the measurement uses thirteen).
- Noise dominance: 0.206 / 0.003–0.082 → 2.5–60×.

## OBSERVATIONS

- The ambiguity that free magnitude creates is concentrated in one mechanism pair and one situation
  (before excitation).
- Isolation reaches 1.000 only after the manoeuvre — driven by **excitation**, not elapsed time,
  consistent with EXP-0010.
- FC-1 has the smallest magnitude penalty because its trim α ≈ −0.9° makes a scale fault on α
  invisible there, so fewer classes are in play at all.

## INTERPRETATIONS

*(Contestable.)*

- Unknown magnitude is **not** the hidden assumption that restores AURA's motivation.
- **Support misspecification is a qualitatively different failure from uncertainty**, and it is the
  only effect in this project that worsens with more evidence. Any system marginalising over a
  bounded fault model inherits it.
- The transient bias-vs-scale ambiguity is a *decision-timing* problem, not a diagnosability limit.

## HYPOTHESES

- The same mechanism will apply to the fault **taxonomy**: a class the model has never seen should
  be misassigned with *increasing* confidence as the window grows. Much larger version of the same
  effect; untested.
- Excitation design may be the main lever on time-to-isolation — more than sensors or estimators.

## ASSUMPTIONS

- **Template families still exactly known** (TV-M5). Only magnitude was freed.
- Magnitude range experimental, positive-only, zero excluded.
- Linear magnitude families (residual ≤ 4.28%).
- Gaussian white noise; synthetic σ; equal class priors; one aircraft (TV-D10); one excitation.

## DECISIONS

| Decision | Rationale |
|---|---|
| Continuous manifold minimum as the primary measure | A grid can only sample near an intersection; grid minima overstate separation by up to 19.9× for exactly the pairs that matter |
| Report both pre-registered and window-local detectability | The pre-registered floor (full-window) conflates non-detection with mis-isolation at short windows |
| Add exploratory Case B′ | Case B as pre-registered measures prior *misspecification*, not bounded knowledge |
| Keep Case B and report it prominently | It turned out to be the most informative condition in the experiment |
| F4 treated as magnitude-free | Freezing a signal is the same fault at any nominal magnitude |

## FILES CREATED / MODIFIED

**Created:** `analysis/magnitude_ambiguity.py`, `visualization/plot_exp0011.py`,
`experiments/EXP-0011/{experiment_spec.md, config/exp0011.yaml, generate_magnitudes.py,
run_exp0011.py}`, `experiments/EXP-0011.yaml`,
`reports/technical/EXP-0011_UNKNOWN_FAULT_MAGNITUDE.md`, this handoff,
`results/validation/EXP-0011/{exp0011_results.json, template_index.json, P_class_surface.npz}`,
`data/manifests/DS-0002.{yaml,sha256}`, FIG-010/011/012 + sidecars.

**Modified:** experiment registry, FINDINGS.md, README.md, assumptions, threats (TV-M6).

## EXPERIMENTS

EXP-0011, `COMPLETED`. 252 classifier cells × 20 000 replications, plus continuous manifold analysis
at 28 (condition, window) points and six validity attacks. 416 new simulations (DS-0002); the m = 1
slice reused from DS-0001. Runtime 1515 s.

## RESULTS

See FACTS. Surface: `results/validation/EXP-0011/P_class_surface.npz`.

## FAILURES

No experiment failed. **Three defects in my own work, all found by testing and all corrected:**

1. **Bug (code).** The nominal class F0 was excluded from the admissible set, because the
   detectability filter asks d(F, F0) ≥ 4.65 and F0 trivially fails against itself. This dropped F0
   from the manifold analysis (136 pairs instead of 153) and made it **unselectable by the Case B/C
   classifier while Case A could still choose it** — biasing precisely the comparison the experiment
   exists to make. The first run's numbers were discarded and the experiment re-run.
2. **Design flaw (pre-registration).** The detectability floor was declared at the full window, so at
   short windows it admits faults that are not visible at all, conflating "these two faults look
   alike" with "neither is visible yet". A window-local analysis was added post-hoc and labelled.
3. **Design flaw (pre-registration).** Case B draws truths from the full grid while restricting the
   prior, so it measures prior misspecification rather than bounded knowledge. Kept and reported —
   it produced the experiment's most important finding — with an exploratory Case B′ added.

Also: a patch to the generator failed silently on a whitespace mismatch and produced nine duplicate
F0 templates. Caught by an assertion added after the first silent failure. All subsequent patches
are assertion-checked.

## LIMITATIONS

1. Template families exactly known (TV-M5) — every probability is an upper bound.
2. Magnitude range experimental and positive-only; a negative bias could intersect other classes.
3. Linear family fits: separations below ~4% of family norm are unresolvable.
4. One self-implemented aircraft (TV-D10), one excitation, equal priors.
5. The pre-registered detectability floor and Case B were both flawed; corrections are post-hoc.
6. No claim about real sensors, real aircraft, safer autonomy or operational applicability.

## OPEN QUESTIONS

1. **Does support misspecification generalise from magnitude to the fault taxonomy?** If a class the
   model has never seen is misassigned with growing confidence, that is a far larger effect than
   anything measured so far — and it is the assumption every diagnostic system in this literature
   makes.
2. How much does template/model error raise the effective noise level?
3. Is excitation design the real lever on time-to-isolation?
4. Would a negative-magnitude range create intersections the positive-only grid cannot?
5. Would an independently sourced airframe show the same behaviour (TV-D10)?

## PASS / FAIL

Not a pass/fail gate. **Decision gate: Outcome B (dominant) + E, with C supported only
pre-manoeuvre, D partial, and A not supported** — plus a finding outside all five categories:
*being wrong about magnitude is far worse than being uncertain about it, and uniquely worsens with
more data.*

## RECOMMENDATION

**Do not build the uncertainty-aware decision layer.** Three experiments have now failed to find the
diagnostic ambiguity AURA was designed around: it is absent at realistic noise (EXP-0010), absent
with unknown magnitude (EXP-0011), and transient where it exists at all.

But the same three experiments have repeatedly surfaced a *different* problem that is well
evidenced: **misplaced confidence**. The argmax rule false-alarms 89% of the time under elevated
noise; a prior excluding the truth becomes more confidently wrong with more data. That is a stronger
and better-measured motivation for abstention than ambiguity ever was.

The honest position is that AURA's premise has been **narrowed by evidence three times** and has
landed somewhere more defensible than it started.

## NEXT SCIENTIFIC ACTION

**EXP-0012 — an unmodelled fault class (support misspecification of the taxonomy).** Hold out one
fault class, present it to the classifier, and measure how confidently it is misassigned as the
observation window grows. It is the same mechanism as §13.2 at a much larger scale, uses the
existing machinery, and is the first experiment in this sequence whose expected outcome would
genuinely support AURA's premise — which is a reason to design it adversarially rather than
optimistically.

---

```text
AURA_CONTEXT:
experiment=EXP-0011
status=COMPLETED
primary_question=how does fault-class isolation change when the diagnostic system does not know the fault magnitude
fault_magnitude_model=unknown nuisance parameter; 9-level sqrt(2)-spaced grid spanning 0.25x-4x the EXP-0002 nominal (16x range); positive only; zero excluded; constant within a run; EXPERIMENTAL range, not physically calibrated
knowledge_conditions=A known exactly; B prior [0.5,2] with truths from the full grid (= prior MISSPECIFICATION); C prior [0.25,4]; B-prime exploratory with matched truths
valid_flight_conditions=FC-1, FC-2, FC-3, FC-5 (FC-4 remains INVALID per FAIL-0001, not resurrected)
observation_windows=0.25, 0.5, 1, 2, 5, 10, 18 s after onset; the excitation doublet runs 4-10 s so windows <= 2 s are pre-manoeuvre
primary_metric=P_class, correct fault-CLASS identification with magnitude marginalised, Bayes-optimal with known template FAMILIES -- an upper bound
key_result=not knowing the magnitude costs at most 3.3 points and 0.0001 at the full window; being WRONG about it costs 6.5-13.3 points and the penalty GROWS monotonically with observation length
magnitude_uncertainty_effect=small and transient; noise dominates by 2.5-60x, though the two interact (magnitude penalty grows 25x as noise rises)
persistent_ambiguity=NONE. every overlapping pair resolves by 18 s at every condition. overlap exists only pre-manoeuvre and only for bias-vs-scale on the same channel, at P=0.52-0.57
condition_dependence=14.7x spread in the magnitude penalty (FC-1 0.0047 to FC-3 0.0689), stronger than EXP-0010's 1.83x
analytical_prediction_result=confirmed, not refitted: r=0.973 over 28 cells; closed form is a lower bound predicting exactly zero pre-manoeuvre against a measured 0.23-0.35 (still near chance)
validity_attack_result=grid minima overstate near-intersection separation by up to 19.9x (hence the continuous method); linear magnitude families fit to 0.13-0.34% mean residual; detectability floor does not change the minimum; three defects in our own design found and corrected, including an F0-admissibility bug that biased the central comparison and forced a full re-run
limitations=template FAMILIES still assumed exactly known (TV-M5); positive-only experimental magnitude range; linear-family resolution floor ~4%; one self-implemented aircraft (TV-D10); one excitation; equal priors
research_implication=the composite-hypothesis rescue FAILS -- unknown magnitude does not restore AURA's motivating ambiguity. But support MISSPECIFICATION emerges as a well-evidenced and qualitatively different problem: it is the only effect in this project that worsens with more data. AURA's motivation shifts from diagnostic ambiguity to misplaced confidence
next_experiment=EXP-0012 unmodelled fault class (support misspecification of the taxonomy)
```

---

# FOR AN INDEPENDENT REVIEWER

**Criticise, not confirm.** Attacks worth making:

- **Is the headline finding an artefact of how Case B was built?** Case B's prior excludes the truth
  4/9 of the time by construction. Is "a prior that excludes the truth performs badly, and worse with
  more data" a discovery, or an inevitable property of Bayesian inference over a wrong support that
  did not need an experiment?
- **Is the positive-only magnitude range hiding intersections?** A negative bias could plausibly
  mimic a different class. This was excluded by pre-registration and is a real limitation.
- **Is the linear magnitude-family approximation load-bearing?** Fit residuals reach 4.28%. Some
  reported near-intersections are below that resolution.
- **Were the post-hoc additions (window-local detectability, Case B′) genuinely corrective, or
  result-driven?** Both were added after seeing that the pre-registered versions gave confusing
  answers. Check whether the pre-registered numbers are still reported prominently — they are, but
  judge whether the framing favours the post-hoc ones.
- **Does the F0 bug undermine confidence in the rest of the pipeline?** It biased the central
  comparison and was found only by inspecting an anomalous pair count. What else might be wrong?
- **Is "isolation reaches 1.000" too good to be true?** The classifier knows the template families
  exactly. Would any of these conclusions survive template error?
- **Three experiments have now failed to find the motivating ambiguity.** At what point does the
  correct conclusion become that AURA's premise is wrong, rather than that the next assumption should
  be relaxed?
