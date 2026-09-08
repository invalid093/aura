# EXP-0010 — Research Handoff

**Self-contained. No attachments required. Written for independent critical review.**

**Date:** 2026-09-08 · **Experiment:** EXP-0010 · **Status:** COMPLETED

---

## TASK

Determine whether the deterministic observability structure found in EXP-0002 survives contact with
measurement uncertainty: which fault hypotheses remain practically distinguishable, which become
statistically ambiguous, and whether the boundary depends on flight condition.

## OBJECTIVE

Test, not confirm. EXP-0002 was noise-free, so its distinguishability results were an idealised upper
bound. EXP-0010 measures what an optimal observer can actually infer under uncertainty.

## WORK PERFORMED

- Derived, **before running**, that EXP-0002's per-sample metric relates to the optimal-detection
  deflection by exactly $\sqrt{KN} = 153$ — which showed a noise-only sweep would measure nothing,
  and forced the design to sweep observation window as well.
- Pre-registered the noise model, uncertainty levels, windows, metrics, replication count and
  validity attacks.
- Implemented an exact 18-dimensional reduction of the Monte Carlo (60–70× cheaper) and verified it
  against direct full-dimensional simulation.
- Reused the EXP-0002 trajectories (DS-0001) with **no re-simulation** for the main study.
- Ran 130 M classification trials across 4 conditions × 10 uncertainty levels × 9 windows × 18
  faults, plus six validity attacks. Total 355 s.

## KEY FINDINGS

1. **At the reference sensor specification the ambiguity vanishes entirely.** $P_{\text{iso}} = 1.000$
   and **zero** practically ambiguous pairs at all four conditions. EXP-0002's five-member ambiguity
   group does not survive statistical analysis at realistic noise.
2. **But isolation takes ~5 seconds.** Even with perfect sensors, $P_{\text{iso}} = 0.45$ at 0.05 s
   and does not reach 0.95 until ≈ 5 s. **The binding constraint is time, not noise** — an outcome
   none of the five pre-declared decision-gate categories anticipated.
3. **EXP-0002's group was right about the hard set — but this is substantially implied, not
   independent.** The five hardest faults under noise are exactly {F0, F2_α, F2_q, F4_α, F4_Vt}.
   A circularity test (run because the concern is legitimate) gives rank correlation 0.77–0.98
   between statistical difficulty and deterministic nearest-neighbour distance, with up to a
   ten-position rank shift. Deterministic analysis is a useful *screening* tool, not a predictor.
4. **Condition dependence is real but modest:** η₉₅ spread 1.83×, ordering FC-1 < FC-2 ≈ FC-3 < FC-5
   preserved at every window and every fault magnitude. At η₅₀ the spread collapses to 1.04×.
5. **The closed-form bias/scale prediction survives** (r = 0.979), conservative by 1.2–2.1×.
6. **Temporally correlated noise costs 21%**, quantitatively explained by $\sqrt{(1+\rho)/(1-\rho)}$
   (r = 0.9993 against the prediction).
7. **Detection ≠ isolation.** At η = 50: detection 0.98, isolation 0.80, **false alarm 0.89**.

## FACTS

- $P_{\text{iso}}$ at 18 s: η=1 → 1.000 at all four conditions; η=5 → 0.982–0.997; η=10 → 0.952–0.981;
  η=50 → 0.803–0.854; η=1000 → 0.109–0.118.
- $P_{\text{iso}}$ at FC-1, η=1, by window: 0.452 (0.05 s), 0.559 (0.5 s), 0.701 (2 s), 0.997 (5 s),
  1.000 (10 s).
- Practically ambiguous pairs (P_disc < 0.95) at η=1: **0 of 153** at every valid condition.
- At η=10, 3 pairs are ambiguous, 3 of 3 inside the EXP-0002 group; at η=50, 11 pairs, 10 of 11 inside.
- Per-fault $P_{\text{iso}}$ at FC-1, η=50, five lowest: F0 0.11, F2_α 0.24, F2_q 0.40, F4_α 0.53,
  F4_Vt 0.65.
- η₉₅ at 18 s: FC-1 10.2, FC-2 15.1, FC-3 15.7, FC-5 18.7. η₅₀: 161, 162, 167, 166.
- Detection/false alarm at 18 s: η=1 → 1.000/0.000; η=50 → 0.98/0.89; η=200 → 0.99/0.98.
- Seed sensitivity: max |Δ| = 0.0007. Student-t(4): Δ ≤ 0.01 vs Gaussian. AR(1) ρ=0.5: −21% mean.
- Recomputed $d_{ij}$ matches EXP-0002 to 5.0 × 10⁻¹⁰.
- 355 s runtime; no new bulk data.

## CALCULATIONS

- $d' = d_{ij}\sqrt{KN} = 153.0\,d_{ij}$; EXP-0002's most ambiguous pair has $d' = 10.1$, giving
  optimal $P_e = 2.2\times10^{-7}$ at the reference noise. **EXP-0002's τ=1 was conservative by ≈153×.**
- AR(1) prediction: effective sample reduction $(1+\rho)/(1-\rho)=3$ → deflection ÷ $\sqrt{3}$.
  Mean |observed − predicted| = 0.0048, r = 0.9993 over 12 cells.
- Analytic η₉₅ from the $V_t$ channel alone vs measured over all 13: r = 0.979, ratio 1.22–2.05.
- Binomial 95% CI half-width at N=20 000: ±0.007 worst case; realised ±0.003–0.006.

## OBSERVATIONS

- In the realistic range (η ≤ 5), η changes $P_{\text{iso}}$ by < 0.02 while window changes it by 0.55.
- The 2 s → 5 s jump in $P_{\text{iso}}$ coincides with the excitation doublet (4–10 s): isolation
  depends on *observing the manoeuvre*, not on elapsed time alone.
- FC-1 (highest dynamic pressure, lowest α) is consistently the worst condition for isolation.
- Noise converts the EXP-0002 group from a binary label into a graded, probabilistic ambiguity; it
  does not reorder or contract it, and expands it beyond five members only at η ≥ 100.

## INTERPRETATIONS

*(Contestable.)*

- Ambiguity at realistic noise is **temporal**, not statistical.
- Deterministic distinguishability analysis is a useful cheap *screening* tool, but its ranking is
  not identical to the statistical one and it cannot predict where ambiguity emerges.
- The argmax decision rule is unusable under elevated uncertainty regardless of how uncertainty is
  represented.
- Because template error acts exactly like elevated η, the *realistic* operating regime may be η ≥ 10
  rather than η = 1 — but that is a hypothesis, not a result.

## HYPOTHESES

- Unknown fault magnitude will dominate every effect measured here, because F1 and F2 on a channel
  intersect exactly at $V^*$ when magnitude is free.
- Including template/model error would move the effective regime into the range where ambiguity and
  condition dependence are material.

## ASSUMPTIONS

- **Known templates** — the classifier knows all 18 trajectories exactly. Largest optimism; makes
  every $P$ an upper bound. (New threat **TV-M5**.)
- **Known fault magnitude** — composite-hypothesis overlap not measured.
- Gaussian white noise as primary; σ synthetic and representative, not from any datasheet.
- Model uncertainty not modelled; η used as its proxy.
- Equal fault priors.
- A-SIM-01 / A-SIM-07 / TV-D10 carried from EXP-0002: one self-implemented aircraft.

## DECISIONS

| Decision | Rationale |
|---|---|
| Sweep observation window as well as noise | Derived before running: a noise-only sweep at realistic σ would measure nothing |
| Reuse DS-0001 without re-simulation | 130 M trials in 355 s; no redundant computation |
| Exact 18-dim Monte Carlo reduction | Mathematically exact for Gaussian white noise; verified against direct simulation |
| Report every probability as an upper bound | The classifier knows templates; real systems do not |
| Label η ≥ 10 as stress levels, not sensor claims | Honest; they proxy total effective uncertainty |

## FILES CREATED / MODIFIED

**Created:** `analysis/practical_diagnosability.py`, `visualization/plot_exp0010.py`,
`experiments/EXP-0010/{experiment_spec.md, config/exp0010.yaml, pilot_verify.py, run_exp0010.py}`,
`reports/technical/EXP-0010_MEASUREMENT_UNCERTAINTY.md`, this handoff,
`results/validation/EXP-0010/{exp0010_results.json, P_iso_surface.npz}`, FIG-004/005/006 + sidecars.

**Modified:** experiment registry, FINDINGS.md, README.md, assumptions (TV-M5).

## EXPERIMENTS

EXP-0010, `COMPLETED`. 360 primary cells × 18 faults × 20 000 replications = 130 M trials, plus
6 validity attacks. Source dataset DS-0001 reused; no new bulk data generated.

## RESULTS

See FACTS. Central surface: `results/validation/EXP-0010/P_iso_surface.npz`.

## FAILURES

**None.** No experiment failed, no run was invalid, and no condition was excluded beyond FC-4, which
remains invalid from FAIL-0001 and was not resurrected.

The nearest thing to a negative result is scientific rather than procedural: **the motivating
ambiguity is absent at realistic sensor noise**, which weakens one of AURA's stated premises.

## LIMITATIONS

1. Known templates → upper bound of unknown tightness (**TV-M5**).
2. Known fault magnitude → composite ambiguity unmeasured.
3. Model uncertainty not modelled.
4. White noise primary; correlated noise costs a further 21%.
5. One self-implemented aircraft (TV-D10, HIGH, unmitigated).
6. One excitation; isolation demonstrably depends on observing it.
7. Equal priors.
8. No claim about real sensors, real aircraft, safer autonomy or operational applicability.

## OPEN QUESTIONS

1. How much ambiguity does **unknown fault magnitude** create? Probably the dominant effect.
2. How much does **template/model error** raise the effective η? If it reaches ≥ 10, the original
   motivation returns.
3. What is actually knowable in the first 5 seconds — the window where the real problem lives?
4. Does the 5 s isolation delay change with a different excitation?
5. Would a real airframe show the same condition ordering?

## PASS / FAIL

Not a pass/fail gate. **Decision-gate outcome: A (dominant) + E, with C partially supported, B not
supported, D partial** — plus a finding outside all five categories: *the binding constraint is the
observation window, not the uncertainty level.*

## RECOMMENDATION

**Do not build the uncertainty-aware decision layer.** EXP-0010 has just shown the motivating
ambiguity is absent at realistic sensor noise with known templates. Building now would build on the
weakest version of AURA's own case.

Two assumptions must be relaxed first, because both can only *increase* ambiguity and either could
restore the motivation on measured evidence rather than assumption: unknown fault magnitude, and
template/model error.

The honest summary is that AURA's problem has **moved**: from "which fault is it?" — which is easy
here — to "what should the aircraft do during the several seconds in which isolation is impossible?"
That question is better grounded, because it was measured rather than assumed.

## NEXT SCIENTIFIC ACTION

**EXP-0011 — isolation with unknown fault magnitude (composite hypotheses).** Largest untested
assumption; reuses the same machinery; the closed form already proves the classes intersect at $V^*$.

---

```text
AURA_CONTEXT:
experiment=EXP-0010
status=COMPLETED
primary_question=which fault hypotheses remain practically distinguishable under measurement uncertainty, and does the boundary depend on flight condition
noise_model=additive zero-mean Gaussian white, independent across channels and time, per-channel sigma from the EXP-0002 synthetic MEMS-grade spec, uniform multiplier eta; Student-t(4) and AR(1) rho=0.5 tested as alternatives
noise_levels=eta in {1,2,5,10,20,50,100,200,500,1000}; eta=1 is the reference spec, eta>=10 are labelled experimental stress levels proxying total effective uncertainty
replications=20000 per cell, 130M classification trials, seed base 20261008, per-cell seeds derived deterministically
valid_flight_conditions=FC-1, FC-2, FC-3, FC-5 (FC-4 remains INVALID per FAIL-0001, not resurrected)
primary_metric=P_iso, probability of correct 18-way isolation under the Bayes-optimal KNOWN-TEMPLATE classifier -- an UPPER BOUND on any real diagnoser
key_result=at the reference sensor spec P_iso=1.000 with ZERO practically ambiguous pairs, but isolation requires ~5 s of observation even with perfect sensors; the binding constraint is TIME, not noise
ambiguity_result=EXP-0002's five-member group dissolves at eta=1 but is exactly the set that degrades first under stress (5 hardest faults at eta=10 and eta=50); noise makes the ambiguity graded rather than binary, and does not reorder it
condition_dependence=real but modest -- eta95 spread 1.83x with ordering FC-1<FC-2~FC-3<FC-5 preserved across all windows and fault magnitudes; eta50 spread only 1.04x
analytical_prediction_result=EXP-0002 closed-form bias/scale prediction survives, r=0.979, conservative by 1.2-2.1x; correctly ranks conditions
validity_attack_result=seed-independent (max diff 0.0007); robust to heavy tails; AR(1) costs 21% but is quantitatively predicted by sqrt((1+rho)/(1-rho)) at r=0.9993; Gram reduction verified exact against direct simulation; condition ordering preserved at fault magnitudes x0.5 and x2
limitations=known templates and known fault magnitude make every probability an upper bound (TV-M5); model uncertainty unmodelled; one self-implemented aircraft (TV-D10); one excitation; equal priors
research_implication=the case for uncertainty-aware ISOLATION at realistic sensor noise is WEAK; the problem relocates to the ~5 s transient during which isolation is impossible; the argmax rule fails badly (P_FA=0.89 at eta=50); deterministic analysis is a useful screening tool but its ranking is only 0.77-0.98 correlated with the statistical one, so the 'group predicts difficulty' claim was downgraded after a circularity test
next_experiment=EXP-0011 isolation with unknown fault magnitude (composite hypotheses)
```

---

# FOR AN INDEPENDENT REVIEWER

**Criticise, not confirm.** Attacks worth making:

- **Is the known-template classifier so optimistic that the whole study is uninformative?** It knows
  all 18 trajectories exactly. Does an upper bound of unknown tightness tell us anything actionable?
- **Is η ≥ 10 a legitimate device or a rescue?** The report reframes it as "total effective
  uncertainty" *after* finding no ambiguity at η = 1. Is that principled, or motivated?
- **Is the 5 s isolation delay a property of the aircraft or of the excitation?** The jump coincides
  exactly with the doublet. A different manoeuvre might change everything.
- **Does reusing EXP-0002 trajectories inherit its flaws?** Same model, same magnitudes, same
  excitation, same experimenter-chosen parameters (TV-D10).
- **Is the ambiguity-group result circular?** This was tested and the claim downgraded as a result
  (report §13): rank correlation 0.77–0.98, 8–9 of 18 faults ranked differently, F6 shifting ten
  positions. Is the residual non-trivial content — that the mapping stays monotone under a
  many-hypothesis classifier — worth reporting at all, or should the claim have been dropped?
- **Is P_FA = 0.89 a real finding or an artefact of equal priors over 18 hypotheses?**
- **Should this experiment have been run before the composite-hypothesis case**, given that unknown
  magnitude is likely to dominate?
