# EXP-0002 — Research Handoff

**Self-contained. No attachments required. Written for independent critical review.**

**Date:** 2026-09-08 · **Experiment:** EXP-0002 (gate) · **Status:** COMPLETED · **Verdict: PASS, with thin margins**

---

## TASK

Execute EXP-0002, the Phase 0 decision gate: determine whether the aircraft/fault system contains
the non-trivial, operating-condition-dependent ambiguity structure that the AURA research design
assumes. A negative result invalidates the design.

## OBJECTIVE

Answer: *do different faults produce distinguishable measured responses, and does the structure of
that ambiguity change across flight conditions?* — as a scientific experiment, not a software
milestone.

## WORK PERFORMED

- Resolved the blocking licence question (A-1) and substituted the aircraft model (ADR-0007).
- Corrected a definitional error in the Phase 0 specification (ADR-0008).
- Wrote a pre-registered experiment specification before any code ran.
- Implemented a nonlinear 6-DOF fixed-wing model, trim solver, closed-loop controller, fault
  injection, deterministic RK4 harness, and the distinguishability analysis (~900 lines, no scipy).
- Ran 31 pilot verification checks.
- Executed 90 primary runs (5 flight conditions × 18 faults) plus 4 sensitivity sweeps and a
  determinism replay — 951 s, 17.7 MiB.
- Ran the validity attack, which **invalidated one flight condition and removed the
  strongest-looking evidence**.
- Repaired the design, re-ran, and produced matrices, figures and this report.

## KEY FINDINGS

1. **PASS, but on thinner evidence than it first appeared.** Ambiguity exists at every valid
   condition (10–11 indistinguishable pairs of 153) and its structure varies with operating point —
   but at the pre-declared threshold only **one pair of 153** changes verdict between conditions.
2. **The headline result was an artefact and was discarded.** FC-4 returned a perfect diagonal and
   rank correlation of 0.37–0.46 against other conditions — dramatic apparent condition-dependence.
   The aircraft was stalling. See FAILURES.
3. **A stable five-member ambiguity group** {F0, F2_q, F2_α, F4_α, F4_Vt} persists at every valid
   condition, with a textbook observability mechanism.
4. **A condition-dependent ambiguity was predicted in closed form and confirmed at r = 0.979.**
5. **Cross-condition rank correlation is perfectly monotone in operating-point separation** (6/6
   pairs in order; the designed control pair returns 0.984, the extreme pair 0.658).
6. **A Phase 0 assumption was refuted in its specifics:** the predicted ambiguity pair (pitch-rate
   scale error vs elevator effectiveness loss) is distinguishable at every condition.

## FACTS

- Trim converged at all five conditions, residuals ≤ 5×10⁻¹⁵.
- Valid conditions: FC-1 (1000 m, 45 m/s, α=−0.88°, q̄=1126 Pa), FC-2 (1000 m, 28 m/s, α=5.15°,
  q̄=436 Pa), FC-3 (5000 m, 35 m/s, α=4.83°, q̄=451 Pa), FC-5 (5000 m, 28 m/s, α=10.15°, q̄=289 Pa).
- FC-4 (5000 m, 24 m/s) nominal run: α reaches 31.52°, |Δθ|=32.47°, |ΔV|=27.73 m/s, |Δh|=353.3 m.
- At τ=1 of 153 pairs: FC-1 142 distinguishable, FC-2/3/5 143 each. FC-4 (invalid) 153.
- {F0, F2_q, F2_α, F4_α, F4_Vt} mutually indistinguishable at all four valid conditions.
- `F1_Vt`/`F2_Vt` indistinguishable at FC-1 only — the single verdict flip.
- All 90 runs bitwise reproducible on replay.
- No process noise, no measurement noise, no wind, no RNG anywhere.

## CALCULATIONS

- Cross-condition Spearman ρ: 0.9843 (FC-2|FC-3, control pair) → 0.6577 (FC-1|FC-5, extreme pair).
  Rank correlation between ρ and |Δα| across the six pairs = **−1.000** (perfectly monotone).
- Bias/scale crossover: V* = b/(k−1) = 5.0/0.10 = **50 m/s**. Measured vs analytic distance across
  four conditions: **Pearson r = 0.979**.
- Metric dilution: 7 of 13 channels ever differ under longitudinal excitation → √(7/13) = 0.734.
  Uniform across all pairs; rankings unaffected.
- Runtime 951 s; 17.7 MiB compressed for 90 runs.

## OBSERVATIONS

- Ambiguity splits ≈40% detection-type (vs nominal) / 60% isolation-type (fault vs fault).
- The *amount* of ambiguity is nearly constant across valid conditions (10–11 pairs); its
  *composition and ordering* is what changes.
- FC-1 and FC-5 have identical pair counts at τ=3 (87 each) yet ρ = 0.658 — same quantity of
  ambiguity, different structure.
- Ambiguity is dominated by faults that are weak by construction, not by faults that mimic each other.

## INTERPRETATIONS

*(Contestable readings, not facts.)*

- Condition-dependence is real but **modest**; the evidence is in the continuous rank structure, not
  the binary matrix. The monotone ρ ordering plus the control pair at 0.984 argues it is physics,
  not numerical noise.
- The closed-form-predictable ambiguity is more valuable to AURA than the size of the effect,
  because it gives the ambiguity component a *derivable* reference.
- The stable ambiguity group justifies set-valued diagnostic output.
- Because ambiguity is driven by fault weakness, AURA's decision layer needs *detectability-aware*
  abstention as much as isolation-aware abstention.

## HYPOTHESES (suggested, not established)

- Excitation may matter more than flight condition; untested.
- With measurement noise, the ambiguity group will grow.
- The near-stall regime may have genuinely different structure; it remains unprobed.

## ASSUMPTIONS

- **A-SIM-01 / A-SIM-07:** GFW-1 is a representative fixed-wing model, not a validated airframe;
  parameters were chosen by the experimenter (TV-D10).
- **A-SIM-05:** algebraic actuators, no lag.
- **A-SEN-01:** no GPS in the suite.
- Sensor σ values are pre-declared instrument properties used only for normalisation.
- Aleatoric noise is not simulated.

## DECISIONS

| ID | Decision |
|---|---|
| ADR-0007 | AeroBenchVVPython is **GPL-3.0**; not vendored. EXP-0002 uses the self-contained GFW-1. **Researcher decision required before Phase 1b.** |
| ADR-0008 | "Structural isolability" was the wrong term; the experiment measures response-based distinguishability. Structural isolability is condition-invariant by construction and the gate would have failed for a definitional reason. |
| FAIL-0001 | FC-4 marked INVALID and excluded; FC-5 added as the replacement high-α probe, selected by a validity rule declared before its matrix was computed. |

## FILES CREATED / MODIFIED

**Created:** `aircraft/gfw1.py`, `aircraft/trim.py`, `faults/faults.py`,
`simulation/controller.py`, `simulation/simulate.py`, `analysis/isolability.py`,
`visualization/plot_exp0002.py`, `experiments/EXP-0002/{experiment_spec.md, config/exp0002.yaml,
pilot_verify.py, run_exp0002.py}`, `experiments/EXP-0002.yaml`,
`experiments/failures/FAIL-0001.md`, `docs/decisions/ADR-0007…`, `ADR-0008…`,
`reports/technical/EXP-0002_STRUCTURAL_ISOLABILITY.md`, `data/manifests/DS-0001.{yaml,sha256}`,
results matrices and FIG-001/002/003.

**Modified:** `docs/assumptions.md` (A-LIC-01 refuted in part, A-UNC-03 amended, A-SIM-01 extended,
A-SIM-07 added), `reports/phase0/THREATS_TO_VALIDITY.md` (TV-D10 added).

## EXPERIMENTS

EXP-0002, `COMPLETED`. 90 primary runs + 15 sweep grids + 1 determinism replay. Dataset `DS-0001`
(git-ignored, regenerable, checksummed).

## RESULTS

| Condition | Distinguishable / 153 | Indistinguishable | Status |
|---|---|---|---|
| FC-1 | 142 | 11 | VALID |
| FC-2 | 143 | 10 | VALID |
| FC-3 | 143 | 10 | VALID |
| FC-5 | 143 | 10 | VALID |
| FC-4 | 153 | 0 | **INVALID** |

Sensitivity: step size — identical counts, ρ ≥ 0.9992 vs base. Threshold — structure exists for
τ ∈ [0.1, 3]; at τ ≥ 10 all valid conditions collapse to zero distinguishable pairs. Magnitude —
condition-dependence persists at ×0.5, ×1, ×2 (min ρ 0.797 / 0.658 / 0.736). Duration — identical
at 10 s and 20 s. Determinism — 90/90 bitwise.

## FAILURES

**FAIL-0001 (`EXPERIMENTAL_INVALIDITY`).** FC-4 departs controlled flight. Its perfect diagonality
and low cross-condition correlation are divergence amplification, not diagnosability. **Root cause
was a defect in my own pilot**: it checked closed-loop boundedness at FC-1 only, and trim
convergence (2×10⁻¹⁵) was mistaken for flyability. A validity gate is now part of the pipeline.

Two minor defects, fixed and recorded: sensitivity step 0.004 s does not divide the 100 Hz sample
interval (→ 0.005 s); determinism summary line printed a hard-coded "72 runs" while checking all 90
(label only).

## LIMITATIONS

1. Deterministic and noise-free — results are upper bounds on achievable separation.
2. One self-implemented aircraft; parameters chosen by the experimenter (TV-D10, **HIGH,
   unmitigated**).
3. One excitation profile.
4. Single fault magnitude in the primary matrix.
5. 13-channel dilution shifts absolute distances relative to τ (uniform; rankings unaffected).
6. Correlated channels not decorrelated.
7. High-α regime (>12°) not covered — the condition intended to probe it was invalid.
8. Structural isolability outer bound not computed.

## OPEN QUESTIONS

1. How much of the 142/153 "distinguishable" survives measurement noise on a single realisation?
2. Does excitation change the matrix more than flight condition does?
3. Does the result reproduce on an independently sourced aircraft model?
4. Can a controller hold trim near stall, so the high-α regime can be probed?
5. Is a single verdict flip in 153 pairs enough condition-dependence to justify a
   condition-dependent ambiguity model at all — or is a single condition-independent ambiguity group
   sufficient?

**Question 5 is the one that most threatens AURA's design, and this experiment does not settle it.**

## PASS / FAIL

**PASS** on all four pre-declared criteria, evaluated on valid conditions only.

Qualifications: the margin on the condition-dependence criterion is thin (1 flip in 153) and rests
mainly on the threshold-free rank correlation; the exclusion of FC-4 removed the strongest-looking
evidence and a reviewer should check that judgement; and criterion 1 was ambiguously worded relative
to its FAIL clause (moot here because all valid conditions show ambiguity, but a genuine
specification defect).

## RECOMMENDATION

Proceed — but narrow the claim. The premise survives: ambiguity is real, stable, physically
explicable, partially derivable in closed form, and it varies with operating point. It varies
**less** than the Phase 0 design assumed.

**Do not proceed to any learning component, uncertainty estimator or decision layer yet.** EXP-0002
shows the substrate exists; it does not show a learned uncertainty estimate is needed to exploit it.

Two items require researcher decisions: the GPL-3.0 licensing choice (ADR-0007) and whether a
single verdict flip constitutes enough condition-dependence to justify the design (open question 5).

## NEXT SCIENTIFIC ACTION

**EXP-0010 — repeat the distinguishability matrix with measurement noise over repeated realisations.**
This is the largest limitation and the prerequisite for hypothesis H3. Second priority: reproduce
the cross-condition result on an independently sourced aircraft model to retire TV-D10.

---

```text
AURA_CONTEXT:
experiment=EXP-0002
status=COMPLETED
pass_fail=PASS (thin margin on condition-dependence; one flight condition invalidated)
flight_conditions=5 run, 4 valid (FC-1,FC-2,FC-3,FC-5), FC-4 INVALID per FAIL-0001
fault_count=18 (F0 nominal + 4 mechanisms x 4 channels + F6 actuator); F5 excluded by construction
distinguishability_definition=normalised RMS response distance over 13 measured channels, 1801 post-onset samples, normalised by pre-declared sensor sigma; distinguishable iff d > tau = 1.0
key_result=stable 5-member ambiguity group at every valid condition; cross-condition Spearman rho 0.984 (control pair) to 0.658 (extreme pair), perfectly monotone in operating-point separation; bias/scale crossover predicted in closed form and confirmed at r=0.979
key_failure=FAIL-0001 -- FC-4 departs controlled flight; its perfect-diagonal matrix and rho=0.37-0.46 were divergence amplification and were discarded, removing the strongest-looking evidence
key_limitation=deterministic and noise-free; one self-implemented aircraft with experimenter-chosen parameters (TV-D10); only 1 of 153 pairs changes verdict between conditions at the pre-declared threshold
research_implication=premise survives with narrowed scope -- ambiguity is real and set-valued output is justified, but condition-dependence is a reordering of magnitudes rather than a restructuring of the ambiguity set; A-FLT-03 refuted in its specifics
next_experiment=EXP-0010 (distinguishability under measurement noise, repeated realisations)
```

---

# FOR AN INDEPENDENT REVIEWER

**Criticise, not confirm.** Specific attacks worth making:

- **Is PASS justified?** One verdict flip in 153 pairs at the pre-declared threshold. Is the
  threshold-free rank correlation (0.658–0.984) enough to carry criterion 4, or is this a PASS by
  the narrowest reading of a criterion the experimenter wrote?
- **Was excluding FC-4 correct, or convenient?** It was the only condition supporting strong
  condition-dependence. The validity thresholds were declared before the replacement's matrix was
  computed — check that claim against the commit history, and re-run the envelope scan.
- **Was adding FC-5 legitimate?** It was selected by a validity rule, but by the same person who
  wanted the experiment to pass. Would a different valid high-α condition give a different answer?
- **Is the aircraft model doing the work?** GFW-1's parameters were chosen by the experimenter
  (TV-D10). Would a real airframe show the same monotone ρ ordering?
- **Is the metric fair?** Normalising by sensor σ, aggregating 13 channels by RMS when only 7 ever
  differ, and not decorrelating channels — do any of these choices favour the conclusion?
- **Is the analytic prediction circular?** V* = b/(k−1) uses the fault magnitudes the experimenter
  set. Does confirming it demonstrate anything beyond arithmetic consistency?
- **Does the ambiguity group mean anything?** It consists largely of faults too weak to detect. Is
  "these faults are nearly invisible" a finding about diagnosability, or about a poor choice of
  fault magnitude?
- **Should the noise-free result be reported at all**, given that every conclusion may change once
  measurement noise is added?
