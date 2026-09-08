# AURA — Candidate Research Directions after EXP-0002 → EXP-0012

Companion to [`EXP_0002_0012_CUMULATIVE_REVIEW.md`](EXP_0002_0012_CUMULATIVE_REVIEW.md).
Three candidates, ranked. None of them is the original RQ-1, whose premise the cumulative review
found unsupported.

**`ASSUMPTION`** All three assume the existing GFW-1 model, sensor suite and fault library are kept.
TV-D10 (self-implemented aircraft, never cross-validated) applies to all three equally.

---

## Direction 1 — Close the novelty gate *(ranked first; not an experiment)*

**Research question.** Has the design-time characterisation of a fault library's undetectable
blind spots — the combination of manifold geometry with a χ² detectability threshold — already been
established in the model-based FDI, structural-analysis or set-membership-diagnosis literature?

**Hypothesis (`HYPOTHESIS`).** It has. The residual test dates to the 1970s and structural
isolability analysis is a mature field; the specific composition may nonetheless be unpublished.

**Novelty.** Not applicable — this *determines* whether novelty exists for anything else here.

**Required experiments and data.** None. A systematic literature search per the Phase 0 protocol:
declared databases, declared query strings, declared inclusion criteria, recorded counts, written up
in `reports/phase0/LITERATURE_SEARCH.md`. Closes **TV-N1**.

**Role of physics.** None directly; the search is over physics-based FDI literature.

**Role of ML.** None.

**Main risk.** That the answer is "yes, this is standard" — which would terminate the branch. That is
a feature, not a risk to the science.

**Falsification criterion.** The search is not a hypothesis test; its *outcome* falsifies or permits
Directions 2 and 3. If ≥2 independent sources describe residual-based library-completeness analysis
for fault diagnosis, the constructive contribution identified in the review is not novel.

**Expected contribution.** Either a defensible novelty claim, or an honest and early stop.

**`INTERPRETATION`** This is ranked first because Phase 0 declared it a *blocking* gate and four
experiments have run past it. Every downstream direction is conditional on it, and it costs no
compute.

---

## Direction 2 — Excitation-limited identifiability of near-manifold faults

**Research question.** For a fault whose signature is confined to transients, is there *any*
admissible excitation that raises its distance from the known-fault manifold above the χ² detection
threshold — and can the answer be determined analytically at design time?

**Hypothesis (`HYPOTHESIS`).** The distance-to-threshold ratio for a transient-signature unseen
fault is maximised by an excitation that concentrates energy in the frequency band where the fault's
transfer-function error is largest, and admissible excitation is bounded by the flight-envelope
validity gate — so the set of unresolvable faults is non-empty and computable in advance.

**Novelty.** Conditional on Direction 1. Related to input design for identifiability (a mature field)
and to active fault diagnosis; the specific target — separating an *unmodelled* fault from a known
library rather than estimating parameters — is the part that may be new.

**Required experiments and data.** Primarily analytical: linearise about each flight condition,
express each unseen fault's residual signature as a frequency-domain error, and optimise excitation
energy subject to the α/load-factor validity gate. A confirmatory simulation of the optimised and
baseline excitations on the six existing unseen faults — of the order of a few hundred runs, well
inside the storage forecast. Reuses `analysis/hypothesis_mismatch.py` unchanged.

**Role of physics.** Central. Manifold geometry, the χ² threshold, and the linearised dynamics do all
the work.

**Role of ML.** None. If the analysis shows the residue is irreducible under *any* admissible
excitation, that would be the first evidence-based argument for a learned representation — but that
is an outcome, not a plan.

**Main risk.** **Scope creep into control.** Excitation is a control variable, and pursuing it
expands AURA from passive diagnosis into active diagnosis. `LIMITATION` The evidence does not yet
compel that expansion; the analytical form is chosen specifically to test the question without
building a controller.

**Falsification criterion.** Pre-registered: if the optimised excitation fails to raise the
distance/threshold ratio above 1.0 for UF-003 at any flight condition, the near-manifold residue is
not excitation-limited and this direction is closed.

**Expected contribution.** A design-time answer to "which unmodelled faults can this diagnostic
system never see, no matter how it is flown?"

**`FACT`** Supporting evidence already in hand: UF-003's distance/threshold ratio rises to 0.80 at
the 10 s window — exactly when the excitation doublet ends — then *declines* to 0.74 at 18 s. More
quiescent observation makes this fault harder to detect. UF-006, whose signature is persistent,
plateaus at ~16.8 and is never at risk.

---

## Direction 3 — A researcher-independent unseen-fault population

**Research question.** Under a fault population generated by rule rather than by researcher choice,
what fraction of unmodelled faults are undetectable-as-novel — and does the closed-form threshold
still predict which ones?

**Hypothesis (`HYPOTHESIS`).** The threshold's predictive accuracy (99.3% on the authored set)
survives an unbiased population, but the *rate* of confidently-wrong-and-undetected cases changes
substantially, because the authored set over-represents near-manifold faults by construction.

**Novelty.** Low as a contribution in itself; high as a correction. It converts an
unfalsifiable-in-magnitude number into a measured one.

**Required experiments and data.** Define an unseen-fault generator by rule — e.g. random
first-order sensor dynamics, random actuator rate/deadband perturbations, random aerodynamic
derivative shifts — with parameters sampled from declared ranges and *no* inspection of the known
library. Sample ~200 faults, run the existing EXP-0012 pipeline unchanged. Storage comparable to
DS-0003.

**Role of physics.** Central: the generator must produce physically plausible faults, and the
threshold prediction is analytic.

**Role of ML.** None.

**Main risk.** The declared ranges are themselves a researcher choice; this reduces the degree of
freedom rather than eliminating it. `LIMITATION` The ranges must be pre-registered before any run.

**Falsification criterion.** If the confidently-wrong-and-undetected rate falls below 1% under the
rule-based population, EXP-0012's 5.8% was an artefact of fault selection and the replacement
phenomenon is not established at a meaningful rate.

**Expected contribution.** Either a defensible rate, or a retraction of one.

---

## Directions deliberately *not* proposed

**`INTERPRETATION`**

- **Any ML direction.** The cumulative review found no problem for which learning is uniquely suited:
  ambiguity is absent, the OOD residue is handled by a standard non-learning test, and the remainder
  is a geometry problem. Proposing an ML direction here would be exactly the goalpost-shifting the
  review identified.
- **A decision layer (act / abstain / escalate).** Its motivating premise — separable ambiguity and
  competence loss — is unsupported by EXP-0010 and EXP-0011.
- **"Relax the next assumption" (model/template error).** This was the documented fallback had
  EXP-0012 failed. Continuing that sequence is the mechanism the review identified as making the
  programme unfalsifiable, and it should not be taken without an external reason.
