# HANDOFF — Cumulative Scientific Review, EXP-0002 → EXP-0012

**Date:** 2026-09-08 · **Type:** Review and audit. **No new simulation was run.**
**Full review:** `research/cumulative_review/EXP_0002_0012_CUMULATIVE_REVIEW.md`
**Direction options:** `research/cumulative_review/RESEARCH_DIRECTION_OPTIONS.md`

This handoff is self-contained. It assumes no memory of the conversation that produced it.

---

## 1. What was asked

Before running EXP-0013 or introducing any machine-learning component, determine whether the
accumulated evidence from EXP-0002, EXP-0010, EXP-0011 and EXP-0012 still constitutes **one coherent
research question**, or whether the project has been shifting its goalposts to survive four null
results. The instruction was explicit: *do not defend AURA.*

## 2. What AURA originally claimed

RQ-1, written before any experiment: does representing **evidential ambiguity** separately from
**competence loss** produce better act / abstain / escalate decisions than a single scalar
confidence? Its premise: *fault diagnosis is fundamentally limited by ambiguity among plausible
fault hypotheses under realistic uncertainty.* The planned destination was uncertainty-aware
diagnosis with ML baselines (deep ensembles, ensemble PNN with an epistemic OOD gate).

## 3. What the four experiments actually found

| Exp | Finding | Premise supported? |
|---|---|---|
| EXP-0002 | Deterministic ambiguity exists (5-member group, stable at all conditions); condition dependence real but weak — **1 verdict flip in 153 pairs**; closed-form prediction confirmed r = 0.979 | Partially |
| EXP-0010 | **At reference noise, P_iso = 1.000 — zero ambiguous pairs.** Ambiguity needs 10–19× reference σ. The binding constraint is **observation time (~5 s)**, not noise. EXP-0002's threshold was conservative by exactly √(KN) ≈ 153 | **No** |
| EXP-0011 | Unknown magnitude costs **0.0001** at full window. But a prior *excluding* the truth costs 6.5–13.3 points and **worsens with more data**. All overlap transient | **No** |
| EXP-0012 | With the true fault absent from the library: confidently wrong and residual silent in **5.8%** of cells (**16.7%** at full window); a χ² residual catches 47–83%, exactly when a closed-form threshold predicts (**1502/1512, 99.3%**) | **No — a different mechanism** |

## 4. Verdict on the original premise

**UNSUPPORTED.** Not weakly supported — the measured quantity is 1.000 where the premise predicts
degradation. Ambiguity is absent at realistic noise, absent under unknown magnitude, and transient
where it exists at all.

## 5. Verdict on goalpost-shifting

**Substantially goalpost-shifting, with legitimate execution inside each step.**

Each experiment was pre-registered, each falsification was reported prominently, and each relaxed
assumption was named as the largest limitation in the *previous* experiment's own limitations
section. That is the case for refinement.

Against it: the target mechanism changed (ambiguity → misplaced confidence under support mismatch)
while **the intended solution never changed**. A programme that redefines the problem and holds the
solution fixed is not falsifiable at the programme level, even when every experiment inside it is.

The required bias check — *would this direction still have been selected had EXP-0012 been
negative?* — comes out **no**: the documented fallback was to relax the next assumption and continue.

## 6. Two corrections to AURA's own published claims

**(a) The χ² residual did not pre-exist EXP-0012.** Verified by direct inspection:
`analysis/practical_diagnosability.py` has zero references to a goodness-of-fit statistic, and
neither the EXP-0010 nor the EXP-0011 results files contain a residual field. The report's wording
"the framework already contains a non-learning statistic" was **wrong** and has been corrected
throughout to "a simple non-learning residual, added in EXP-0012, catches most mismatch". This makes
the "ML not needed" conclusion *weaker*, not stronger, which is why it had to be fixed. A dated
correction note is now in the EXP-0012 report.

**(b) "23 persistent cells" is not a robust number.** Across defensible confidence thresholds
(0.80–0.999) and χ² rejection cuts (0.10–0.90) the count ranges **14–32**. The qualitative claim — a
non-empty persistent set at every threshold — holds. The number does not, and is now always quoted
with its range.

## 7. Novelty

At least three of AURA's findings are close to textbook: the softmax's structural inability to
express hypothesis-space mismatch (this is *why* OOD detection exists as a field), the χ² residual
(the classical model-based FDI residual test), and the detectability threshold (elementary
non-central χ²). The one candidate contribution is **design-time enumeration of a fault library's
undetectable blind spots** by combining manifold geometry with that threshold.

**But TV-N1 is open.** Phase 0 declared a systematic literature search a *blocking gate on any
novelty claim*, and four experiments have run past it. **AURA cannot currently claim novelty for
anything.** This is the single most consequential finding of the review, it is a process failure
rather than a scientific one, and it costs no compute to fix.

## 8. New evidence produced by the review (from existing data only)

**Near-manifold failure is excitation-limited, not time-limited.** For UF-003 (pitot lag, the most
dangerous unseen fault) at FC-1, where the doublet runs 4–10 s:

| Window | 0.25–2 s | 5 s | **10 s** | 18 s |
|---|---|---|---|---|
| distance / detection threshold | 0.00 | 0.41 | **0.80** | **0.74** |

The ratio **peaks exactly when the manoeuvre ends, then declines** — more quiescent observation makes
this fault *harder* to detect, because the threshold grows as N^¼ while a transient signature stops
accumulating. UF-006, whose signature is persistent, plateaus at ~16.8 and is never at risk.

This is the strongest available support for an excitation direction, and it was obtained without
running anything.

## 9. Files created or changed

**Created**
- `research/cumulative_review/EXP_0002_0012_CUMULATIVE_REVIEW.md` — full 20-section review
- `research/cumulative_review/RESEARCH_DIRECTION_OPTIONS.md` — three candidate directions, ranked
- `handoffs/CUMULATIVE_RESEARCH_REVIEW_HANDOFF.md` — this file

**Changed**
- `reports/technical/EXP-0012_UNSEEN_FAULTS.md` — dated correction note + four wording fixes (§6a)
- `handoffs/EXP_0012_HANDOFF.md` — same correction propagated
- `FINDINGS.md` — cumulative-review entry added; "23 cells" given its range; wording corrected
- `README.md` — status rewritten; RQ-1 **retained unedited and marked** rather than rewritten
- `experiments/REGISTRY.md` — review recorded; TV-N1 search added as next; EXP-0013 marked `DEFERRED`

No code, configuration, results file or dataset was modified. All prior results remain valid as run.

## 10. What the next session should do

1. **The systematic literature search (TV-N1).** Declared databases, declared query strings,
   declared inclusion criteria, recorded counts, written to `reports/phase0/LITERATURE_SEARCH.md`.
   Question: is residual-based characterisation of a fault library's blind spots already established?
2. **If it clears:** the analytical identifiability study — *can any admissible excitation raise a
   near-manifold fault above the χ² threshold?* — before any simulation sweep.
3. **If it does not clear:** stop this branch. That is an acceptable scientific outcome and should be
   recorded as one.

**Do not run EXP-0013 in its original form.** "Does a second excitation help?" is the weaker version
of a question that is substantially answerable analytically.

## 11. Still awaiting the researcher

- **Licensing (ADR-0007):** accept GPL-3.0 and use AeroBench, source a permissive airframe, or keep
  GFW-1 and accept TV-D10 permanently.
- **ADR-0005:** the GPS-exclusion sensitivity run was mandated at Phase 0 and has never been done.
- **No operational false-confidence requirement exists**, which is why the review declines to call
  5.8% unacceptable. Someone has to state what rate would matter.

---

# EXP-0013 DECISION: DEFER

Excitation is genuinely supported by the evidence — UF-003's detectability ratio peaking at the end
of the doublet and then declining is direct, quantitative support, and it was obtained from data
already in hand. But EXP-0013 must not be the next action. The novelty gate that Phase 0 declared
blocking has been open for four experiments, and if a systematic search shows that residual-based
detection of unmodelled faults is standard FDI practice — plausible, given that the residual test is
1970s technology — then no excitation experiment can rescue the branch. Separately, the proposed form
of EXP-0013 is the weaker version of the right question: "does a second excitation help?" should be
"can *any* admissible excitation lift the near-manifold set above threshold?", which is an
identifiability problem largely answerable analytically and at far lower cost. Deferred pending the
literature search, then to be redesigned in analytical form.

# ML PHASE: NOT JUSTIFIED

There is no scientifically defined problem remaining for which a learning method is uniquely suited.
The ambiguity that motivated uncertainty estimation is absent at realistic noise and under unknown
magnitude. The one real failure mode found — confident misdiagnosis under hypothesis-space
mismatch — is caught in 47–83% of cases by a simple non-learning residual with an analytically
predictable failure boundary, and the residue consists of near-manifold faults, which is a geometry
problem that learning does not add information to. Note that this conclusion is *weaker* than the
project previously stated: the residual was authored during EXP-0012 rather than inherited, so the
correct claim is "a simple non-learning test suffices", not "the framework already sufficed". ML
would become preliminarily justified if an identifiability analysis showed the near-manifold residue
is irreducible under any admissible excitation — that would be the first evidence-based argument for
a learned representation. Until then, building one would repeat the pattern this review was
commissioned to detect.
