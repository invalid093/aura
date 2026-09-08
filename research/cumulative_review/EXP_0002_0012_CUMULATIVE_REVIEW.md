# AURA — Cumulative Scientific Review, EXP-0002 → EXP-0012

**Date:** 2026-09-08 · **Type:** Synthesis and audit. No new simulation was run.
**Purpose:** determine whether AURA is still one coherent research programme, whether its original
premise survived, and whether EXP-0013 is justified.

Evidence classes are marked throughout: `FACT` / `CALCULATION` / `OBSERVATION` / `INTERPRETATION` /
`HYPOTHESIS` / `ASSUMPTION` / `LIMITATION`.

---

## Executive conclusion

**`INTERPRETATION`** AURA's original premise is **unsupported**. Four experiments looked for
diagnostic ambiguity under progressively weaker assumptions and did not find it in a form that
limits diagnosis.

**`INTERPRETATION`** The replacement phenomenon — misplaced confidence under hypothesis-support
mismatch — is real and measured, but its three components are each close to textbook: the softmax's
inability to express mismatch, the χ² residual test, and non-central χ² detectability. **AURA has
not yet demonstrated novelty**, and the systematic literature search that Phase 0 declared a
*blocking gate* on any novelty claim has still not been performed after four experiments.

**`INTERPRETATION`** On the central question the assignment poses, the honest answer is that this is
**more goalpost-shifting than refinement** — not because any single experiment was badly run, but
because *the intended solution never changed* while the target problem did. The bias check in §5
comes out negative.

**Two corrections to the project's own published claims are made in §8 and propagated.**

Decisions: **`EXP-0013 DECISION: DEFER`** · **`ML PHASE: NOT JUSTIFIED`**

---

## Original AURA hypothesis

Reconstructed from `docs/research_question.md`, `docs/hypotheses.md` and
`docs/decisions/ADR-0002-research-question.md`, written 2026-09-08 before any experiment.

| Element | As originally written |
|---|---|
| **Research question (RQ-1)** | "When an autonomous aircraft's operating regime departs from the conditions under which its diagnostic system was developed, does representing *evidential ambiguity* separately from *competence loss* produce better act / abstain / escalate decisions than a single scalar confidence?" |
| **Hypothesis H1** | A decision policy over $(A,N)$ achieves lower expected decision cost at matched autonomy coverage than the best single-scalar confidence gate |
| **Causal mechanism** | Ambiguity and competence loss have *opposite correct responses*; a scalar confidence cannot separate them; therefore separating them improves decisions |
| **Key variables** | $A$ = evidential ambiguity (which faults are indistinguishable); $N$ = competence loss (outside development conditions) |
| **Intended contribution** | An uncertainty decomposition validated against an analytic ground truth (structural isolability), in an aerospace flight-dynamics setting |
| **Motivation for uncertainty awareness** | "Two or more fault hypotheses explain the measurements equally well… more confidence would not help" |
| **Motivation for ML** | Baselines B2–B4 in `EXPERIMENTAL_DESIGN_PRELIMINARY.md`: deep ensembles, ensemble PNN with epistemic OOD gate — the planned destination |
| **Expected failure mode** | Recorded honestly in advance: "the most likely outcome is that H1 is falsified and H3 is supported" |

**`FACT`** The premise to be tested was explicitly: *fault diagnosis is limited by ambiguity among
plausible hypotheses under realistic uncertainty.*

---

## Experiment genealogy

| Exp | Question | Prediction | Result | Original hypothesis supported? | New problem discovered? | New assumption introduced? |
|---|---|---|---|---|---|---|
| **EXP-0002** | Does fault distinguishability vary with flight condition? | Non-trivial, condition-dependent ambiguity exists | Ambiguity exists deterministically (10–11 of 153 pairs); cross-condition rank correlation 0.98→0.66, monotone in operating-point separation; **only 1 of 153 pairs flips verdict**; closed-form bias/scale crossover confirmed r=0.979 | **Partially** — condition dependence real but far weaker than assumed | FC-4 departed controlled flight (FAIL-0001); its "perfect" matrix was divergence amplification | Structural isolability replaced by response-based distinguishability (ADR-0008); model substituted for licence reasons (ADR-0007) |
| **EXP-0010** | Does that survive measurement noise? | Noise creates practical ambiguity | **At reference noise, isolation is perfect** ($P_{iso}=1.000$, zero ambiguous pairs). Ambiguity needs 10–19× the reference σ. Isolation instead requires **~5 s of observation**. EXP-0002's threshold was conservative by exactly √(KN)≈153 | **No** — the motivating ambiguity is absent | Binding constraint is **time**, not noise; argmax false-alarms 89% at η=50 | Classifier knows templates and magnitudes exactly (TV-M5) |
| **EXP-0011** | Does unknown fault magnitude create it? | Free magnitude makes classes intersect | Not knowing magnitude costs ≤3.3 points, **0.0001 at full window**. But a prior *excluding* the truth costs 6.5–13.3 points and **worsens monotonically with more data**. All overlap transient | **No** — the composite-hypothesis rescue fails | **Support misspecification**: the only measured effect that gets worse with evidence | Template *families* still exactly known |
| **EXP-0012** | What if the true fault is absent from the library? | Posterior confidently wrong; residual may catch it | Confidently wrong in 5.8% of cells (16.7% at full window); 15–32 cells persist at 18 s depending on thresholds. A χ² residual catches 47–83%, **exactly when a closed-form threshold predicts (99.3%)** | **No** — a *different* mechanism | Near-manifold unseen faults are blind spots; posterior structurally cannot express mismatch | **A goodness-of-fit residual was added to the framework** (see §8B) |

---

## Evidence supporting the original hypothesis

**`FACT`** EXP-0002 found genuine ambiguity: a stable five-member group indistinguishable at every
valid flight condition, with a physically explicable mechanism (scale faults are unobservable on
near-zero signals).

**`FACT`** EXP-0002 found condition dependence with a clean signature: cross-condition rank
correlation monotone in operating-point separation across all six condition pairs, with the designed
control pair returning 0.984.

**`FACT`** Closed-form predictions were made before simulation and confirmed twice (r = 0.979 in
EXP-0002, r = 0.973 in EXP-0011).

**`INTERPRETATION`** This is the whole of the supporting evidence, and all of it concerns a
*deterministic, noise-free* setting.

---

## Evidence against the original hypothesis

**`FACT`** EXP-0010: at the reference sensor specification, $P_{iso} = 1.000$ and **zero of 153 pairs**
are practically ambiguous, at every valid flight condition. Ambiguity requires 10–19× the reference
uncertainty.

**`FACT`** EXP-0010: EXP-0002's ambiguity was an artefact of a per-sample threshold, conservative by
exactly √(KN) ≈ 153. Its "indistinguishable" pairs are separable with error ~10⁻⁷ by an observer that
integrates the window.

**`FACT`** EXP-0011: unknown magnitude — the strongest remaining candidate — costs 0.0001 at full
observation.

**`FACT`** EXP-0011: all magnitude-induced overlap resolves by 18 s. No persistent ambiguity.

**`INTERPRETATION`** The premise *"fault diagnosis is fundamentally limited by ambiguity among
plausible fault hypotheses under realistic uncertainty"* is **UNSUPPORTED**. Not weakly supported —
the measured quantity is 1.000 where the premise predicts degradation.

**`LIMITATION`** This verdict holds for one self-implemented aircraft, one sensor suite, one
excitation, and a classifier that knows the template families exactly. It is a statement about this
configuration, not about aircraft diagnosis generally.

---

## What EXP-0011 changed

**`FACT`** It converted the project's target from *uncertainty* to *misspecification*. Being
uncertain about magnitude is nearly free; being wrong about it is not, and uniquely worsens with data
(−0.065 at 0.25 s → −0.133 at 18 s).

**`INTERPRETATION`** This was the first genuinely new mechanism the project found, and it was found
**by accident**: Case B was intended to test bounded knowledge and instead tested prior
misspecification, because its truths were drawn from the full grid while its prior was not. That is
documented, but it means the project's most important pivot originated in a specification defect
rather than a designed test.

---

## What EXP-0012 changed

**`FACT`** It scaled the same mechanism from a magnitude sub-range to the fault taxonomy, and found
it larger and persistent: 15–32 cells confidently wrong at full observation depending on thresholds,
12 of them diagnosing a faulted aircraft as healthy.

**`FACT`** It introduced a χ² goodness-of-fit residual, which catches 47–83% of mismatch and whose
failure boundary is analytically predictable (99.3% agreement).

**`INTERPRETATION`** It is the first experiment in the sequence to find a failure mode that survives
adversarial attack. It is also the experiment with the most researcher-authored content (§9).

---

## EXP-0012 methodological audit

### A. FACT 1 — the softmax cannot express hypothesis-space mismatch

**`FACT`** Mathematically inevitable: a uniform lack of fit adds a constant to every log-likelihood
and cancels in the softmax.

**Verdict: a mathematical inevitability with limited novelty, and only weakly a scientific
limitation.** This property is *why out-of-distribution detection exists as a field*. Demonstrating
it in an aerospace setting shows the setting is not exempt; it does not constitute a discovery.

**`INTERPRETATION`** EXP-0012's report treats FACT 1 as motivating the experiment's design, which is
legitimate. It must not be presented as evidence *for* AURA, and it currently is not — but the
framing "confidence rises anyway" in figure titles risks implying novelty. Retained with this caveat
recorded.

### B. The χ² residual — a required correction to our own published wording

**`FACT`** Verified by direct inspection of the code and results files: `analysis/practical_diagnosability.py`
(EXP-0010) contains **zero** references to a residual or goodness-of-fit statistic; neither
EXP-0010's nor EXP-0011's results files contain any residual or χ² field. The five matches in
EXP-0011's module are a linear-fit residual used for manifold fitting — an unrelated quantity.

**`FACT`** The goodness-of-fit residual was **introduced in EXP-0012**.

**Therefore the claim "the framework already catches most mismatch" is wrong.** The correct wording
is:

> **"A simple non-learning residual test, added in EXP-0012, catches most mismatch."**

**`INTERPRETATION`** This distinction matters more than it might appear. The original wording credits
the physics-based framework with robustness it did not exercise, and thereby makes ML look *less*
necessary than the pre-EXP-0012 evidence warranted. The corrected wording is simultaneously more
honest and less favourable to the "no ML needed" conclusion — which is why it must be propagated.
**Corrected in the EXP-0012 report, the README and FINDINGS as part of this review.**

### C. The 5.8% / 16.7% rates

**`FACT`** 5.8% of all 1512 cells and 16.7% of full-window reference-noise cells are confidently
wrong with the residual silent.

**`INTERPRETATION`** **No scientific or engineering threshold exists against which to judge these.**
AURA has never defined an acceptable false-confidence rate. Calling 5.8% "unacceptable" would be an
engineering judgement dressed as a scientific finding, and this review declines to make it.

**What can be said:** the rate is non-zero, reproducible, and survives every validity attack. Whether
it matters is a question about operational requirements that this project has not posed and cannot
answer from simulation.

### D. Robustness of the "23 persistent cells"

Analysed from existing results, no new simulation:

| Confidence threshold τ | Persistent cells at 18 s | All windows |
|---|---|---|
| 0.80 | 32 | 112 |
| 0.90 | 23 | 91 |
| **0.95 (reported)** | **23** | **88** |
| 0.99 | 20 | 74 |
| 0.999 | 15 | 62 |

| χ² rejection cut | Persistent cells at 18 s |
|---|---|
| 0.10 | 14 |
| 0.25 | 23 |
| **0.50 (reported)** | **23** |
| 0.90 | 24 |

**`CALCULATION`** The count ranges **14–32** across defensible thresholds — a factor of 2.3.

**Verdict: robust in existence, not in magnitude.** "23" should never be quoted without its range.
The qualitative claim (a persistent non-empty set at every threshold) holds; the number does not.

### E. The six unseen faults — selection independence

**`LIMITATION`** The taxonomy was designed by the same person who knew the hypothesis library, and
UF-003 was *pre-registered as "NEAR"* and then found to be the most dangerous.

**`INTERPRETATION`** This is circular in a limited but real sense. The *mechanism* (near-manifold
faults evade the residual) is confirmed independently, because the analytic threshold predicts which
faults evade it in 99.3% of cells without reference to the outcome. But the **rate** — 5.8% — is
entirely a function of how many near-manifold faults were chosen to include. It estimates nothing
about the real world and should never be quoted as a base rate.

**`INTERPRETATION`** A rule-based, researcher-independent unseen-fault population is the only way to
make the rate meaningful (see Alternative D).

---

## Researcher-degree-of-freedom audit

| Decision | When | Classification | Could it have changed the conclusion? |
|---|---|---|---|
| Research question replaced (ADR-0002) | Before any experiment | `PRE-REGISTERED` | Yes — chose the whole programme |
| Aircraft model substituted for licence (ADR-0007) | Before EXP-0002 | `JUSTIFIED MODIFICATION` | Possibly (TV-D10) |
| Structural → response-based distinguishability (ADR-0008) | Before EXP-0002 | `JUSTIFIED MODIFICATION` | Yes — the original gate would have failed definitionally |
| Flight conditions FC-1…FC-4 | Pre-registered | `PRE-REGISTERED` | — |
| **FC-4 excluded, FC-5 added** | After FC-4 failed | `JUSTIFIED MODIFICATION` | **Yes** — FC-4 was the strongest apparent evidence for condition dependence, and removing it materially weakened EXP-0002 |
| Validity gate (α<12°, etc.) | After FAIL-0001, before FC-5's matrix | `JUSTIFIED MODIFICATION` | Yes |
| τ = 1.0 distinguishability threshold | Pre-registered | `PRE-REGISTERED` | Yes — and it was later shown conservative by 153× |
| Sensor suite excluding GPS (ADR-0005) | Pre-registered, flagged as the most questionable choice | `PRE-REGISTERED` | **Yes, and the mandated sensitivity run has never been done** |
| Observation-window axis | Introduced in EXP-0010 after deriving that a noise-only sweep would measure nothing | `JUSTIFIED MODIFICATION` | Yes — it produced EXP-0010's main finding |
| Continuous vs grid manifold minimum | EXP-0011, decided before results | `JUSTIFIED MODIFICATION` | Yes — grid overstated separation by up to 19.9× |
| Window-local detectability | EXP-0011, after seeing confusing output | `POST-HOC EXPLORATORY` | Yes — changed which pairs count as ambiguous |
| Case B′ | EXP-0011, post-hoc | `POST-HOC EXPLORATORY` | No — supplementary |
| **χ² residual introduced** | EXP-0012 | **`POTENTIAL RESEARCHER DEGREES OF FREEDOM`** | **Yes** — it converts EXP-0012 from Gate A to Gate A-and-D, and is the basis of the "no ML needed" recommendation |
| **Unseen-fault taxonomy** | EXP-0012, designed with knowledge of the library | **`POTENTIAL RESEARCHER DEGREES OF FREEDOM`** | **Yes** — determines the 5.8% rate entirely |
| τ = 0.95, α = 0.01 | Reused from EXP-0010/0011 | `JUSTIFIED MODIFICATION` | Moderately (§8D) |
| Sequence of assumptions relaxed (noise → magnitude → taxonomy) | Each chosen after the previous null result | **`POTENTIAL RESEARCHER DEGREES OF FREEDOM`** | **Yes — this is the central issue (§ next)** |

**`OBSERVATION`** Individual experiments were pre-registered and their falsifications reported
faithfully. The degrees of freedom are concentrated not *within* experiments but *between* them.

---

## Goalpost-shifting assessment

**The assignment's central question:** legitimate hypothesis refinement, or goalpost shifting?

**Arguments for legitimate refinement:**
- **`FACT`** Each relaxed assumption was named as the largest limitation *in the previous
  experiment's own limitations section*, before the next experiment was designed.
- **`FACT`** Every experiment was pre-registered with falsification criteria, and every falsification
  was reported prominently rather than buried.
- **`FACT`** Negative results were published as headline findings, including in the public README.

**Arguments for goalpost shifting:**
- **`FACT`** The target mechanism changed: from *ambiguity among plausible hypotheses* (RQ-1) to
  *misplaced confidence under support mismatch*. These are different phenomena with different
  causes.
- **`FACT`** The **intended solution never changed.** Phase 0 planned uncertainty-aware diagnosis
  with abstention and ML baselines; that is still the proposed destination after four null results
  on the premise that motivated it.
- **`INTERPRETATION`** A programme in which the problem is repeatedly redefined while the solution is
  held fixed is, at the programme level, **not falsifiable** — even though each experiment is
  individually falsifiable. Nothing in the observed sequence would have ended the project.

### The bias check the assignment requires

> *Would this research direction still have been selected if EXP-0012 had produced a negative result?*

**`INTERPRETATION`** **Almost certainly not.** The documented plan in EXP-0011's handoff was to
relax the *next* assumption (template/model error) had EXP-0012 come out negative. The pattern would
have continued. This is the clearest available evidence that the programme was searching for a
justifying problem rather than testing a hypothesis.

**Verdict: substantially goalpost shifting, with genuinely legitimate execution inside each step.**
The individual science is sound; the programme-level logic is not. That distinction is the most
important output of this review.

---

## Candidate research directions

Detailed in [`RESEARCH_DIRECTION_OPTIONS.md`](RESEARCH_DIRECTION_OPTIONS.md). Summary and ranking:

| Rank | Direction | Why ranked here |
|---|---|---|
| **1** | **Close the novelty gate first** (systematic literature search, TV-N1) | It is a *blocking* Phase 0 gate that four experiments have bypassed. If residual-based blind-spot analysis is standard FDI practice, the entire remaining branch is redundant and no experiment can fix that |
| **2** | **Excitation-aware diagnosability** (analytical identifiability + excitation optimisation) | Directly supported by evidence (§ next); largely answerable analytically |
| **3** | **Rule-based unseen-fault population** (make the 5.8% mean something) | Removes the largest researcher degree of freedom |

**Not ranked: an ML direction.** §10 of this review finds no scientifically defined problem that a
learning method is uniquely suited to address.

---

## Is EXP-0013 (excitation) supported by the evidence?

Analysed from existing results — no new simulation.

**`CALCULATION`** The χ² detection threshold grows as $(2KN)^{1/4} \propto N^{1/4}$. A fault with a
*persistent* per-sample mismatch accumulates distance as $\sqrt{N}$, so its detectability ratio grows
as $N^{1/4}$ and it is eventually always caught. A fault whose mismatch appears only during
*transients* stops accumulating in quiescent flight, so its ratio **plateaus and then declines** as
the threshold keeps growing.

**`FACT`** Measured, for UF-003 (pitot lag, the most dangerous fault) at FC-1 — the excitation
doublet runs 4–10 s:

| Window | 0.25–2 s | 5 s | **10 s** | 18 s |
|---|---|---|---|---|
| distance / threshold | 0.00 | 0.41 | **0.80** | **0.74** |

**The ratio peaks exactly when the manoeuvre ends and then declines.** More quiescent observation
makes this fault *harder* to detect, not easier.

**`INTERPRETATION`** This is direct evidence that the near-manifold failure is an **excitation**
problem rather than an observation-time problem, for faults whose signature is transient. It is the
strongest available support for pursuing excitation.

**But three qualifications:**

1. **`FACT`** It holds for UF-003 and faults like it. UF-006's ratio plateaus at ~16.8, far above
   threshold — excitation is irrelevant there.
2. **`INTERPRETATION`** Whether *any admissible* excitation can lift a near-manifold fault above
   threshold is an **identifiability question answerable analytically**, not one requiring a large
   simulation sweep. The originally proposed EXP-0013 ("test whether a second excitation helps") is
   the weaker form of the right question.
3. **`LIMITATION`** Excitation is a *control* variable. Introducing it expands AURA into active
   diagnosis — a scope increase (§ scope assessment) that the evidence does not yet compel.

---

## Novelty assessment

> *What would AURA teach that is not already obvious from the mathematical structure or the existing
> diagnostic literature?*

| Finding | Novelty verdict |
|---|---|
| Softmax cannot express hypothesis-space mismatch | **None.** Textbook; the reason OOD detection exists |
| χ² residual detects model mismatch | **None.** This is the classical model-based FDI residual test, standard since the 1970s |
| Closed-form detectability threshold $\sqrt{z_\alpha}(2KN)^{1/4}$ | **Minimal.** Elementary non-central χ² detectability |
| Ambiguity absent at realistic noise; isolation limited by observation time | **Possibly**, as a negative result in an aerospace setting — but it is a property of this configuration |
| Support misspecification worsens with data | **Low.** A known property of Bayesian inference over a misspecified support |
| **Design-time enumeration of a fault library's blind spots** by combining manifold geometry with the detectability threshold | **The only candidate.** Constructive, auditable, and not obviously standard — but see below |

**`LIMITATION`** **TV-N1 remains open.** Phase 0 declared a systematic literature search a *blocking
gate on any novelty claim*, and it has never been performed. **AURA therefore cannot claim novelty
for anything**, including the one candidate above. Four experiments have been run past a gate that
was declared blocking.

**`INTERPRETATION`** This is the single most consequential finding of this review. It is a process
failure, not a scientific one, and it is cheap to fix.

---

## Falsifiability assessment

| Direction | What would falsify it |
|---|---|
| Close the novelty gate | A systematic search finding residual-based library-completeness analysis already established → the branch is redundant |
| Excitation-aware diagnosability | An identifiability analysis showing no admissible excitation raises near-manifold separation above threshold → excitation cannot help |
| Rule-based fault population | The confidently-wrong rate collapses toward zero under an unbiased fault population → the 5.8% was an artefact of fault selection |

**`OBSERVATION`** All three are falsifiable and cheap. That is a better position than the programme
has been in since Phase 0.

---

## Scope assessment

**`OBSERVATION`** AURA currently spans: aircraft modelling, fault modelling, state observation,
detection, isolation, magnitude estimation, OOD behaviour, and a planned decision layer. The
proposed EXP-0013 would add **active excitation**, i.e. control.

**`INTERPRETATION`** The smallest coherent scientific problem that preserves the strongest evidence
is:

> **Given a fault library and an observation protocol, which physically plausible faults are
> undetectable-as-novel, and can that set be characterised in advance?**

This retains the χ² threshold, the manifold geometry, and the near-manifold finding. It excludes
decision-making, degraded modes, human interaction, and ML. It does *not* require excitation unless
the question becomes "and can we shrink that set by acting?"

---

## Causal research chain

For the recommended direction (after the novelty gate):

> **Question:** which physically plausible unseen faults are undetectable-as-novel by a given fault
> library and observation protocol?
> **Hypothesis:** the undetectable set is exactly $\{UF : \min_j d(UF, H_j) < \sqrt{z_\alpha}(2KN)^{1/4}\}$
> and is computable at design time.
> **Controlled variable:** the fault library and the observation protocol (window, excitation).
> **Mechanism:** χ² detectability of a non-central shift.
> **Experiment:** rule-based unseen-fault population + analytic threshold, validated against
> Monte Carlo.
> **Metric:** predicted vs actual rejection rate (already 99.3% on the authored set).
> **Falsification:** the threshold fails to predict rejection on an unbiased fault population.
> **Contribution:** a design-time completeness check for fault libraries — *if* the literature search
> shows it is not already standard.

**`OBSERVATION`** This chain writes cleanly. The chain for the *original* RQ-1 no longer does,
because its premise is unsupported.

---

## EXP-0013 recommendation

# `EXP-0013 DECISION: DEFER`

**`INTERPRETATION`** Excitation *is* supported by the evidence — the UF-003 ratio declining after the
manoeuvre ends is direct, quantitative support, and it was obtained from existing data. But it must
not be the next action, for two reasons:

1. **The novelty gate has been open for four experiments.** If a systematic search shows that
   residual-based detection of unmodelled faults is standard FDI practice — which is plausible,
   given that the residual test is 1970s technology — then no excitation experiment can rescue the
   branch. Running EXP-0013 first risks spending compute on a question whose answer is already
   published.
2. **The proposed form is the weaker version of the right question.** "Does a second excitation
   help?" should be "can *any* admissible excitation lift the near-manifold set above threshold?",
   which is an identifiability problem substantially answerable analytically.

**Sequence:** systematic literature search (TV-N1) → if clear, analytical identifiability study →
only then, if analysis is inconclusive, an excitation-optimisation experiment.

## ML-phase recommendation

# `ML PHASE: NOT JUSTIFIED`

| Candidate ML function | Demonstrated problem? | Non-ML alternative exists? | Evidence sufficient? |
|---|---|---|---|
| OOD detection | Yes — 5.8% of cells evade detection | **Yes** — the χ² residual catches 47–83%, with an analytic boundary | No |
| Uncertainty estimation | **No** — ambiguity absent at realistic noise (EXP-0010, EXP-0011) | Not needed | No |
| Confidence calibration | Partly — the posterior is structurally miscalibrated under OOD | **Yes** — the residual is the correct statistic; calibration is not the defect | No |
| Abstention | Yes, in the residue | **Yes** — a residual-threshold rejection rule is non-learning and auditable | No |
| Learned fault representation | **No** — physics templates already give $P_{iso}=1.000$ on known faults | — | No |
| Adaptive diagnosis | **No** — never tested | — | No |

**`INTERPRETATION`** There is no scientifically defined problem remaining that a learning method is
*uniquely* suited to address. The residue — near-manifold unseen faults — is a geometry problem, and
learning does not add information that geometry lacks.

**`INTERPRETATION`** Note that §8B's correction makes this conclusion *weaker*, not stronger: the
non-ML alternative was authored during EXP-0012 rather than pre-existing. The conclusion still holds,
because the residual is standard and transparent — but it should be stated as "a simple non-learning
test suffices", not "the framework already sufficed".

---

## Strongest remaining uncertainty

**`LIMITATION`** Whether any of this is novel. TV-N1 is open, and at least three of the findings are
textbook. Everything else in this review is conditional on that gate.

Secondary: the 5.8% rate is determined by an authored fault set (§8E); the GPS-exclusion sensitivity
run mandated in ADR-0005 has never been performed; and TV-D10 (self-implemented aircraft) remains
unmitigated across all four experiments.

## What would change the conclusion

- **A systematic literature search finding the blind-spot analysis unpublished** → novelty claim
  becomes available, direction 2 becomes strong, EXP-0013 proceeds in its redesigned form.
- **A rule-based fault population showing the confidently-wrong rate is ~0** → the replacement
  phenomenon is an artefact of fault selection; the branch should stop.
- **An identifiability analysis showing no excitation can separate near-manifold faults** → the
  residue is irreducible without changing the hypothesis space, which *would* be a genuine argument
  for a learned representation and would move ML to `PRELIMINARILY JUSTIFIED`.
- **A stated operational false-confidence requirement** → the 5.8% could finally be judged.

## Final scientific recommendation

**`INTERPRETATION`** AURA's original hypothesis was not supported, and the experiments revealed an
adjacent mechanism that is real but of unverified novelty. The programme's individual experiments
were well executed; its programme-level logic — holding the solution fixed while redefining the
problem — was not.

**The correct next action is not an experiment.** It is to close the novelty gate that Phase 0
declared blocking and that four experiments have bypassed. That is a day of literature work, it is
the cheapest action available, and it is the only one that can determine whether anything here is
worth continuing.

If the gate clears, the smallest coherent problem is design-time characterisation of a fault
library's blind spots, with excitation as a possible second stage. If it does not clear, this branch
should stop, and that would be an acceptable scientific outcome.
