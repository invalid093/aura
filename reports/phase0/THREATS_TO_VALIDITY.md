# Threats to Validity — Mandatory Validity Attack

**Date:** 2026-09-08
**Purpose:** §41 of the Phase 0 brief. Actively attempt to disprove the proposed research design
*before* recommending implementation.

Each threat has a severity, an honest assessment, and a mitigation — or an admission that there
isn't one. Threats with no mitigation are the important ones.

---

## N — Novelty threats

### TV-N1 — The novelty claim rests on a non-systematic search
**Severity: HIGH. Unmitigated.**
The gap analysis relies on a web-search reconnaissance, not a systematic database query. Absence of
evidence is not evidence of absence.
**Mitigation:** a systematic search (Scopus/WoS/IEEE Xplore/AIAA ARC) plus forward/backward citation
sweep from LIT-0004 and LIT-0005 is a **Phase 1 gate**. No novelty claim may be published first.
**If the gap is closed:** re-scope, record in an ADR, do not proceed and claim novelty anyway.
**Status 2026-09-08 (cumulative review):** **STILL UNMITIGATED after four experiments.** The gate was
declared blocking and has been run past four times. The cumulative review found at least three of
AURA's findings close to textbook, and concluded that **no novelty may presently be claimed for any
part of the project**. Closing this is now the recommended next action, ahead of any experiment.
See `research/cumulative_review/EXP_0002_0012_CUMULATIVE_REVIEW.md` §novelty.

### TV-N2 — LIT-0004's authors may close the gap first
**Severity: MEDIUM. Unmitigable.**
Mohammadi, Krysander, Jung & Frisk have the tools, the framework and the stated limitation. They
are better placed than AURA to quantify it.
**Response:** AURA's contribution is defined so it survives being scooped on the headline: the
aerospace flight-dynamics setting, the structural-isolability-as-ground-truth evaluation, and the
open reproducible benchmark retain value independently.

### TV-N3 — "Ambiguity vs novelty" may be a relabelling
**Severity: HIGH.**
Aleatoric/epistemic decomposition already exists (LIT-0007). If $A$ and $N$ are just those two under
new names, there is no contribution.
**Mitigation:** H2 is precisely this test, and it is a **gate on interpreting H1**. The distinguishing
claim is not the decomposition itself but that $A$ has an *analytic reference* (structural
isolability) that aleatoric uncertainty does not.

---

## D — Design threats

### TV-D1 — The result could be an artefact of simulator assumptions
**Severity: HIGH. Partially mitigated.**
The shift axes are constructed by the same person who constructs the diagnoser. "OOD" may mean only
"outside the box I drew".
**Mitigation:** axis S4 (alternate aero representation and independent implementation) introduces
*unmodelled structure*, not chosen parameters. Parameter randomisation alone would be a weak OOD
test — this is stated as a criticism of AURA's own design, not only of others'.
**Residual risk:** even S4 stays within the F-16 aero data lineage. Real unmodelled dynamics are not
represented. **Not solvable within scope.**

### TV-D2 — An unfair baseline could manufacture the result
**Severity: HIGH.**
Under-tuned baselines are the commonest way this class of paper reaches a positive result.
**Mitigation:** equal tuning budget, logged; identical evaluation code path; B4 implements the
closest prior work; coverage matching enforced. A per-baseline tuning log is required in the
experiment registry. **If AURA only wins against an untuned B4, the result is void.**

### TV-D3 — The cost model could be chosen to produce the answer
**Severity: HIGH. Mitigated by design.**
**Mitigation:** results are reported as curves over $\rho \in \{5,10,30,100\}$; a win at one $\rho$
is not a win. Declared before results exist.

### TV-D4 — The sensor suite could make diagnosis artificially easy or hard
**Severity: MEDIUM.**
**Mitigation:** EXP-0002 checks the isolability structure before data generation; EXP-0005 checks
that in-distribution isolation accuracy is neither >99% nor <20%. A GPS-included sensitivity run is
part of the design.

### TV-D5 — Some fault classes are fundamentally indistinguishable
**Severity: LOW — this is a feature, not a threat.**
It is the substrate of H2. The real risk is the *opposite*: that everything is isolable, or that
isolability does **not** vary with flight condition. If isolability is flight-condition-invariant,
$A$ has no mode-dependent ground truth and H2 loses its reference.
**Mitigation:** EXP-0002 is a hard gate that can invalidate the design at near-zero cost.

### TV-D6 — Data leakage across the split
**Severity: HIGH — most likely concrete failure.**
Time windows drawn from a single simulation run appearing in both train and test would inflate
performance and corrupt calibration estimates.
**Mitigation:** splits are by **scenario**, never by window. Enforced by an automated check in
`infrastructure/validation/`. Any run's identifier appearing on both sides fails the build.

### TV-D7 — The model might learn the fault labels through a shortcut
**Severity: MEDIUM.**
E.g. the fault-injection code changes a signal's numeric properties (quantisation, dtype, exact
onset alignment) in a way that leaks the label.
**Mitigation:** injection applied uniformly to all runs including nominal (with zero magnitude);
onset times randomised in nominal runs too; a **label-shuffling control** — if a method achieves
above-chance accuracy on shuffled labels, the pipeline leaks.

### TV-D8 — The experiment could be too broad
**Severity: MEDIUM.**
7 methods × 6 shift axes × 4 magnitudes × 4 cost ratios × 30 seeds is a large factorial with a real
multiple-comparisons problem.
**Mitigation:** exactly **one** primary confirmatory comparison (H1 at S6), pre-declared. Everything
else is explicitly secondary/exploratory and labelled as such. Holm–Bonferroni for confirmatory
claims.

### TV-D9 — The experiment could be too narrow to support the conclusion
**Severity: MEDIUM. Partially unmitigated.**
One aircraft model, one sensor suite, seven fault modes.
**Mitigation:** conclusions are scoped in language to the tested configuration. A second airframe
(C5, small UAS) is a Phase 2 option, not a Phase 1 promise.

### TV-D10 — The aircraft model is now self-implemented as well as single
**Severity: HIGH. Unmitigated. Added 2026-09-08.**
ADR-0007 substituted a self-contained model (GFW-1) for AeroBenchVVPython after the latter was
found to be GPL-3.0. GFW-1's equations are standard and published, but its **parameter set was
chosen by the same person running the experiment**. A result that depends on that parameter set
cannot be distinguished from a result about aircraft in general.
**Why it is worse than TV-D9:** TV-D9 is about generality across airframes. TV-D10 additionally
removes the independence between the model and the experimenter.
**Mitigation required before any EXP-0002 conclusion becomes load-bearing:** reproduce on an
**independently sourced** airframe model — either accepting GPL-3.0 and using AeroBench, or
obtaining a permissively-licensed published parameter set.
**Partial mitigation in place:** every parameter is disclosed in version-controlled configuration,
so a reader can check that the values are physically consistent and re-run with their own.

---

## M — Measurement threats

### TV-M1 — "Calibrated" could be claimed on the basis of a bad metric
**Severity: HIGH. Mitigated.**
ECE is not a proper scoring rule and can be trivially satisfied by an uninformative model
(LIT-0010, LIT-0011).
**Mitigation:** proper scoring rules and expected decision cost are primary; ECE is secondary and
always labelled as such.

### TV-M2 — Confidence could be mistaken for uncertainty
**Severity: MEDIUM. Mitigated by definition.**
"Confidence" is reserved for baselines that literally use a softmax score. Enforced by terminology
rules in `CLAUDE.md`.

### TV-M3 — The OOD test might not be genuinely OOD
**Severity: HIGH.**
If the development condition box is drawn wide enough, "OOD" test conditions may be interpolations.
**Mitigation:** report a *measured* shift magnitude (e.g. a two-sample statistic between development
and test feature distributions) alongside the nominal axis level. **If measured shift is small, the
OOD claim is dropped regardless of the nominal design.**

### TV-M6 — Support misspecification: a wrong hypothesis set gets worse with more data
**Severity: HIGH. Unmitigated. Added 2026-09-08 (EXP-0011).**
Every diagnostic system in this project marginalises over a declared hypothesis support: a magnitude
range, and a fault taxonomy. EXP-0011 measured what happens when that support excludes the truth: the
cost is 6.5-13.3 percentage points of class-isolation accuracy, and — uniquely among every effect
measured in this project — **it grows monotonically with observation length** (-0.065 at 0.25 s to
-0.133 at 18 s). More evidence sharpens the likelihood onto a set that does not contain the answer,
so confidence in a wrong class increases rather than correcting.
**Why this is worse than it sounds:** it was measured for a magnitude sub-range, which is the mildest
possible version. The taxonomy version — a fault class the model has never seen — is the same
mechanism at a much larger scale, and no experiment here has tested it.
**Mitigation:** none yet. **EXP-0012 is designed to measure it.**

### TV-M5 — Known-template and known-magnitude assumptions make EXP-0010 an upper bound
**Severity: HIGH. Unmitigated. Added 2026-09-08.**
EXP-0010's classifier knows all 18 fault template trajectories exactly and knows the fault magnitude.
No real diagnoser does either. Every probability it reports is therefore an **upper bound of unknown
tightness**, and its central negative finding — that ambiguity is absent at realistic sensor noise —
holds only under those assumptions.
**Why it cuts both ways:** template error acts exactly like elevated effective noise, so the realistic
operating regime may sit where EXP-0010 *does* find ambiguity (η ≥ 10). This threat could therefore
restore AURA's motivation rather than undermine it — which is precisely why it must be measured
rather than assumed in either direction.
**Mitigation planned:** EXP-0011 relaxes known magnitude; a later experiment must relax known
templates.

### TV-M4 — A simpler method might produce the same result
**Severity: HIGH — and this is the question worth asking.**
**Mitigation:** B0 (fixed threshold) and B1 (MMAE) are in the baseline set precisely so this can be
detected. If a $\chi^2$ threshold matches AURA at matched coverage, **that is the finding** and it
must be reported as the headline, not buried.

---

## S — Statistical threats

### TV-S1 — Test-set reuse
**Severity: HIGH.** Repeated evaluation until a good number appears is the most common integrity
failure in this kind of work.
**Mitigation:** the frozen test set is hashed before training; every evaluation is logged in the
registry with a timestamp regardless of outcome; hyperparameter tuning on test is prohibited
(`CLAUDE.md`).

### TV-S2 — Seed-level variance mistaken for a method effect
**Severity: MEDIUM.** **Mitigation:** ≥30 seeds; paired bootstrap; distributions reported, not point estimates.

### TV-S3 — Equivalence is asserted from a non-significant difference
**Severity: MEDIUM.** A non-significant difference is not evidence of equivalence.
**Mitigation:** explicit TOST equivalence test with a pre-declared margin (δ = 2% of baseline cost).

---

## F — Framing threats

### TV-F1 — Defence relevance substituting for a research question
**Severity: MEDIUM.**
The brief warns against this explicitly. An F-16 model is attention-grabbing.
**Mitigation:** the aircraft choice is justified in `AIRCRAFT_MODEL_SURVEY.md` purely on envelope
width and equation availability, and the survey states that a small-UAS model would have won on
structural analysability. All work is public/unclassified. No operational or threat context is used.

### TV-F2 — "Self-aware aircraft" framing overstating the finding
**Severity: MEDIUM.**
AURA measures whether a two-component uncertainty representation changes decisions in simulation. It
does not demonstrate machine self-awareness in any meaningful sense.
**Mitigation:** the literal research question in `docs/research_question.md` is the claim of record.
The philosophical framing is motivation and is labelled as such.

---

## The falsification question

> **What result would cause us to abandon the hypothesis?**

Answered concretely in `docs/hypotheses.md` §"What would cause AURA to be abandoned". In short:
H2 and H3 both falsified; or a systematic search closing G4 and G6; or EXP-0002 showing
flight-condition-invariant isolability.

---

## Honest overall assessment

The design's **strongest** features: H3 measures a previously unmeasured quantity with a
well-motivated mechanism and is independent of AURA's own method; EXP-0002 is a cheap gate that can
kill the design before expense is incurred; the falsification conditions are concrete and were
written before any data existed.

The design's **weakest** features: TV-N1 (novelty unverified), TV-D1 (residual simulation bias that
cannot be fully removed), and TV-D9 (single airframe). None is fatal, but all three must appear in
the limitations section of any output.

**The single most likely outcome, on current evidence, is that H1 is falsified and H3 is
supported.** That combination is a good paper. It should be planned for, not feared.
