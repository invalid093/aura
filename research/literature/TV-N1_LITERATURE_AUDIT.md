# TV-N1 — Blocking Literature & Novelty Audit

**Date:** 2026-09-08 · **Type:** Research-gate investigation. **No simulation was run. No ML was introduced.**
**Gate:** TV-N1, declared at Phase 0 as *blocking on any novelty claim* and never closed until now.
**Companions:** [`TV-N1_EVIDENCE_MATRIX.md`](TV-N1_EVIDENCE_MATRIX.md) ·
[`TV-N1_NOVELTY_MATRIX.md`](TV-N1_NOVELTY_MATRIX.md) · `literature_index.csv`

---

## 0. Outcome

# `NOVELTY GATE: FAIL`

**`INTERPRETATION`** Every substantive phenomenon AURA has measured is already established in the
literature, most of it decades ago, and the one direction the cumulative review proposed as
strongest — excitation-limited diagnosability of near-manifold unmodelled faults — was published in
September 2025 by an aerospace group, with theorems where AURA has simulations.

**Reason AURA currently lacks a defensible research gap:** AURA's findings F2–F7 are each
independently established — quantitative noise-aware diagnosability (Eriksson et al. 2013), fault-size
effects and open-set fault classification (Lundgren & Jung 2022), posterior concentration on the
KL-nearest wrong hypothesis under misspecification (Berk 1966), the residual/GLR consistency test
(classical FDI), degradation of open-set rejection as unknowns approach known classes (open-set
recognition literature), and excitation-limited diagnosability with active input design as the
remedy (Nikoukhah 1998; Scott et al. 2014; Kong et al. 2025) — and AURA's own strongest result,
that a closed-form classical threshold predicts its blind spots in 99.3% of cells, is itself
evidence that the phenomenon is already fully explained by existing theory rather than an open
question.

---

## 1. Research question at audit start

Unchanged and not rewritten for this audit (policy: historical claims are frozen):

> **RQ-1.** When an autonomous aircraft's operating regime departs from the conditions under which
> its diagnostic system was developed, does representing *evidential ambiguity* separately from
> *competence loss* produce better act / abstain / escalate decisions than a single scalar
> confidence?

The cumulative review (EXP-0002 → EXP-0012) had already found RQ-1's motivating premise
**unsupported** and had proposed a replacement direction. This audit evaluates **both** against the
literature.

---

## 2. Frozen record — what AURA actually established

Classified per `docs/methodology.md` §2. **These classifications are the audit's own and are
deliberately stricter than the original reports.**

| ID | Finding | Class | Note |
|---|---|---|---|
| **F1** | The original premise — diagnosis limited by ambiguity among plausible fault hypotheses under realistic uncertainty — is not supported | `OBSERVATION` (negative) | Holds for one airframe, one sensor suite, one excitation |
| **F2** | Measurement noise did not create substantial ambiguity at realistic levels in the tested configuration; $P_{iso}=1.000$ at reference noise | `CALCULATION` | Conditional on exactly-known templates (TV-M5) |
| **F3** | Unknown fault magnitude cost ≤3.3 points, 0.0001 at full observation | `CALCULATION` | Template *families* still exactly known |
| **F4** | Hypothesis-space mismatch produces confident-but-wrong diagnosis | `FACT` (analytic) + `CALCULATION` | The analytic part is a softmax identity |
| **F5** | A simple goodness-of-fit residual — **added in EXP-0012** — catches 47–83% of unseen-fault cases | `CALCULATION` | Not inherited from EXP-0010/0011 |
| **F6** | Some near-manifold unseen faults remain confidently misdiagnosed (5.8% of cells; 14–32 persistent) | `OBSERVATION` | Rate is a function of an authored fault set |
| **F7** | At least one dangerous case is excitation-dependent — UF-003's detectability ratio peaks at 0.80 when the doublet ends, then declines to 0.74 | `OBSERVATION` | Single fault, single condition |
| **F8** | The size of the "persistent dangerous set" is threshold-dependent (14–32) | `LIMITATION` | Not a finding; a robustness caveat |

**`LIMITATION`** F4's headline half ("the posterior cannot express mismatch") is an algebraic
identity, not an empirical discovery. F6's *mechanism* is confirmed; its *rate* is not an estimate of
anything in the world. Neither was allowed to enter this audit as a literature-grade claim.

---

## 3. Search protocol

**Conducted:** 2026-09-08. **Executor:** Claude (computational research engineer).

| Element | Value |
|---|---|
| Search interfaces | General web search; arXiv; Crossref REST API; Semantic Scholar Graph API; DiVA (refused connection); publisher sites |
| Formulations | 14 independent query formulations across 7 domains, mechanism × application × method terms |
| Conceptual variants searched | *near-manifold*, fault signature similarity, semantic proximity, incipient fault confusion, minimum detectable fault, model-set mismatch, M-open/misspecification, separating input, masquerading |
| Citation chaining | Backward from Scott et al. 2014 and Kong et al. 2025; forward via review articles |
| Inspection | 3 sources full-text inspected (local PDF/HTML text extraction); 3 abstract-verified verbatim; remainder citation-verified via Crossref |
| Citation verification | **Every citation below was checked against Crossref or the publisher record.** None is reproduced from memory |

**`LIMITATION`** No Scopus / Web of Science / IEEE Xplore / AIAA ARC institutional access. Several
key sources are paywalled and were assessed from verbatim abstracts plus verified metadata, not full
text. DiVA (Linköping's repository, host of several of the closest papers) refused connections
throughout. **This audit is therefore weaker than the systematic search Phase 0 specified** — but it
is weak in a direction that would tend to *understate* prior art, and it still returned multiple
independent hits against every AURA finding. A stronger search cannot overturn a FAIL; it can only
deepen it.

---

## 4. Domain A — classical FDI and residual-based unknown-fault detection

**Question:** is EXP-0012's residual-based mismatch detection established classical FDI?

**`FACT`** Yes, and not marginally. The residual + statistical-test architecture — build a residual
from analytical redundancy, then test it against a threshold to decide consistency — is the defining
structure of model-based FDI. Massoumnia, Verghese & Willsky (1989, *IEEE TAC* 34:316–321,
doi:10.1109/9.16422) established the geometric conditions under which failures can be detected and
uniquely identified in LTI systems, and characterised the **undetectable set** via unobservability
subspaces. That is a design-time characterisation of a diagnostic system's blind spots, published 37
years ago.

**`INTERPRETATION`** AURA's χ² goodness-of-fit test is the noise-domain instance of this: consistency
testing against the modelled hypothesis set. Its "distance below threshold ⇒ invisible" criterion is
the classical **minimum detectable fault**, a standard quantity with its own dedicated literature.
Two 2023 papers compute exactly this quantity **for active fault diagnosis**: Xu (2023, *IEEE TAC*
68:1138–1145, doi:10.1109/tac.2022.3148305), “Minimal Detectable and Isolable Faults of Active
Fault Diagnosis”, and Chen, Liu, Xu & Liang (2023, *IFAC-PapersOnLine* 56:5536–5541,
doi:10.1016/j.ifacol.2023.10.449). **Design-time computation of which faults a diagnostic system
cannot see, as a function of the input, is an explicitly named research object with its own paper
title in the literature.**

**Closest methods and their assumptions:** GLR-based residual evaluation assumes a known noise model
and a modelled fault direction; geometric FDI assumes LTI dynamics and exact models. AURA assumes a
known nonlinear model, Gaussian sensor noise, and exactly-known fault templates — a *stronger* set of
assumptions than the classical work, not a weaker one.

**Verdict: N0 — established.**

---

## 5. Domain B — diagnosability, distinguishability, and operating-point dependence

**Question:** are EXP-0002's and EXP-0010's results established?

**`FACT`** Eriksson, Frisk & Krysander (2013, *Automatica* 49:1591–1600,
doi:10.1016/j.automatica.2013.02.045) define **distinguishability** as a Kullback–Leibler divergence
between the observation distributions under two fault modes, use it to quantify *how hard* fault
pairs are to separate under noise, and relate it to achievable residual-generator performance. This
is the same construct as AURA's deflection coefficient, published thirteen years earlier and in
greater generality (stochastic descriptor models, sensor selection).

**`FACT`** Liu, Wang, Zhang & Zhou (2022, *IEEE TAC*, doi:10.1109/tac.2021.3108587) give necessary and
sufficient diagnosability conditions for stochastic systems using the Bhattacharyya distance — again
the same family of quantity.

**`FACT`** That diagnosability depends on the input and operating point is standard in the nonlinear
diagnosability literature (functional and multiple-fault diagnosability via analytical redundancy
relations, *Control Engineering Practice* 2015 and 2018) and is stated explicitly in the active-FDI
literature: Scott et al. (2014) open by noting that faults "may not be detectable in the available
measurements, or cannot be diagnosed without exciting the system."

**`INTERPRETATION`** EXP-0002's condition-dependence result and EXP-0010's noise-dependence result are
instances of an established quantitative framework. AURA's finding that its own EXP-0002 threshold
was conservative by √(KN) is a self-correction, not a contribution.

**Verdict: N0 — established.**

---

## 6. Domain C — active / excitation-based diagnosis (the proposed EXP-0013)

This is where the cumulative review placed AURA's best remaining hope. It does not survive.

**`FACT`** Active fault diagnosis — injecting an auxiliary/probing input to make faults
distinguishable — is a mature field with foundational work by Nikoukhah (1998), Campbell & Nikoukhah
(2004), Šimandl & Punčochář (2009), and Niemann (2006).

**`FACT`** Scott, Findeisen, Braatz & Raimondo (2014, *Automatica* 50:1580–1589,
doi:10.1016/j.automatica.2014.03.016 — full text inspected) compute, using zonotopes, the set of
inputs **guaranteed** to produce outputs consistent with at most one fault scenario, and explicitly
handle the case where that set is empty. This is a stronger result than EXP-0013 proposed to obtain:
a guarantee rather than a simulation sweep.

**`FACT`** **Kong, McMahon & Lahijanian (2025, arXiv:2509.04708, Univ. of Colorado Boulder Aerospace
Engineering Sciences — full text inspected)** is the decisive source. Its abstract:

> a Bayesian framework that explicitly accounts for unmodeled faults, a new quantitative
> diagnosability definition revealing when passive fault identification is fundamentally limited by
> the given control sequence, and an active strategy that designs control inputs for better fault
> identification.

Point by point against AURA:

| AURA element | Kong et al. 2025 |
|---|---|
| Bayesian classifier over a known fault library | Same |
| Unmodelled faults outside the library (EXP-0012) | §III-C, explicitly |
| χ² consistency test to reject mismatch (F5) | Hypothesis-test rejection returning `null` |
| Near-manifold residue where rejection fails (F6) | **Assumption 2** — assumed away |
| Excitation-limited detectability (F7) | **Definition 3**, "fundamentally limited" when λ = 0 |
| Proposed EXP-0013: does excitation help? | **Lemma 1** — optimal controls over a non-degenerate admissible set guarantee λ > 0 |
| Aerospace setting | Aerospace department, nonlinear discrete-time, Gaussian noise |

**`INTERPRETATION`** The analytical identifiability study the cumulative review recommended as the
redesigned EXP-0013 — *can any admissible excitation lift the near-manifold set above threshold?* —
is answered by Lemma 1, in the affirmative, under a stated richness condition, with a proof. AURA
would be reproducing it in simulation.

**Verdict: N0 — established, and specifically anticipated.**

---

## 7. Domain D — unknown faults and hypothesis-space mismatch (EXP-0012's core)

**`FACT`** **Berk (1966, *Annals of Mathematical Statistics* 37:51–58,
doi:10.1214/aoms/1177699597)** proves that when the true data-generating process lies outside the
model class, the posterior concentrates on the parameter minimising KL divergence to the truth.
Confident convergence to the nearest wrong hypothesis under misspecification is a sixty-year-old
theorem. AURA's FACT 1 and its "nearest known fault at rising confidence" are instances of it.
*(Citation verified via Crossref; the paper itself was not read — classified `SECONDARY` in the
literature index.)*

**`FACT`** In the aircraft FDI setting specifically, Lu, Van Eykeren, van Kampen, de Visser & Chu
(2015, *Control Engineering Practice* 36:39–57, doi:10.1016/j.conengprac.2014.12.007) state that both
MMAE and IMM "display deteriorated performance in case where the model set does not contain a model
corresponding to the true system" — the known-limitation form of AURA's F4, in a paper using **real
flight data**. The same group published air-data-sensor FDD on real flight data
(doi:10.2514/6.2015-1311).

**`FACT`** Lundgren & Jung (2022, *Control Engineering Practice* 121:105006,
doi:10.1016/j.conengprac.2021.105006; arXiv:2009.04756 — abstract verified verbatim) build a
KL-divergence framework for fault-diagnosis analysis **and** open-set classification handling unknown
fault classes **and** fault-size estimation, noting that "different fault classes can result in
similar residual outputs, especially for small faults, which causes classification ambiguities."
That single paper spans AURA's EXP-0010, EXP-0011 and EXP-0012.

**`FACT`** The open-set fault-diagnosis literature states the phenomenon in AURA's own terms: closed-set
methods cause "previously unseen fault modes to be incorrectly assigned to known ones with high
confidence" (PHM Society European Conference, open-set recognition for unknown fault modes).

**Verdict: N0 — established, with a 1966 theorem underneath it.**

---

## 8. Domain E — confidence, uncertainty, abstention; and Domain F — OOD / open-set

**`FACT`** Rejection/abstention is classical (Chow 1970). Selective classification, conformal
prediction and open-set recognition are large, active literatures with established distance-based and
likelihood-based rejection mechanisms and calibration evaluations.

**`FACT`** On the hardest OOD cases, the open-set literature is explicit: performance "consistently
degrades" as the semantic proximity of unknown classes to known classes increases. **AURA's F6 — that
near-manifold unseen faults are the dangerous ones — is the named, expected result of that field, not
a discovery.**

**`INTERPRETATION`** AURA's distinction between statistical uncertainty (under a known model) and
model/hypothesis uncertainty (the truth may be unrepresented) is correct and important — and is
exactly the distinction the M-open literature and the OOD literature already draw. AURA must not
present it as its own.

**Verdict: N0 — established.**

---

## 9. Domain G — aircraft-specific literature

**`FACT`** Lima Lopes, Travé-Massuyès, Jauberthie & Alcalay (2024, *DX 2024*, OASIcs vol. 125, art. 3,
pp. 3:1–3:20, doi:10.4230/OASIcs.DX.2024.3 — full text inspected) review air-data-sensor FDI from an
Airbus / LAAS-CNRS perspective: AURA's exact sensors (pitot, static, AoA vane), exact fault classes,
and exact motivation (pitot blockage has caused transport-category accidents; hardware voting can be
deceived by coherent simultaneous faults).

Their stated challenges include, verbatim in substance, AURA's F4/F6 premise:

> A variety of types and modes of faults exist, **some modes being discovered only after being
> observed in operation.**

and

> faults can have many different causes and present themselves in non predicted forms … practical
> implementations of supervised methods might suffer from the lack of generality.

**`INTERPRETATION`** Fault-library incompleteness is not an unrecognised problem in AURA's application
domain; it is a stated design driver, and the field's recommended response — semi-supervised anomaly
detection trained on nominal data, plus hybrid model/data architectures — is already published as the
way forward. Their identified *open* problems are **interpretability/explainability for certification**
and **when false alarms are most prevalent** — neither of which AURA studies.

**Verdict: N0 — established; and AURA is not working on the gaps this domain actually declares.**

---

## 10. Closest-paper test

> *If a reviewer knew these three papers, what exactly would they say AURA adds?*

**Candidate claim:** *"Near-manifold unseen faults can remain confidently misdiagnosed despite
residual testing, and the undetectable set is predictable at design time from a closed-form
threshold."*

**Three closest papers:** Kong et al. 2025 · Lundgren & Jung 2022 · Scott et al. 2014.
*(A fourth, Xu 2023 IEEE TAC, names AURA's candidate contribution in its title.)*

**The reviewer's answer, written honestly:**

> "Kong et al. already give a Bayesian framework that accounts for unmodelled faults, define exactly
> when identification is fundamentally limited by the control sequence, and prove that active input
> design escapes that limit. Lundgren & Jung already give KL-based diagnosability analysis with
> open-set classification and fault-size estimation, and already note that small faults produce
> ambiguous residuals. Scott et al. already compute guaranteed separating inputs and already handle
> the empty case. What AURA adds is that it ran this on its own 6-DOF fixed-wing simulation with six
> unseen faults it designed itself, and reported the fraction that evaded rejection. The fraction is
> a property of the fault set the authors chose. The threshold that predicts blindness is the
> classical minimum detectable fault. **This is a different aircraft model.**"

Per §15 of the audit specification, an answer of that form is **N1**, not novelty.

**`INTERPRETATION`** There is one place where AURA touches something the closest paper does not prove:
Kong et al. *assume* (Assumption 2) that an unmodelled fault is diagnosable — i.e. that rejection
works — where AURA *measured* what happens when that assumption fails. That seam is real but does not
support a research programme, for three reasons: the open-set literature already establishes the
qualitative answer (near classes degrade rejection); the analytic answer is the classical
minimum-detectable-fault threshold; and AURA's own best result is that this threshold predicts its
blind spots in **1502 of 1512 cells (99.3%)**. A phenomenon predicted by a closed-form classical
expression to 99.3% is not an open empirical question — **AURA's strongest result is simultaneously
the strongest evidence against its own novelty.**

---

## 11. Red-team of the strongest remaining claim

A second search was run specifically to destroy the near-manifold claim, using conceptual rather than
literal variants: *fault signature similarity*, *minimum detectable fault*, *semantic proximity of
unknown classes*, *masquerading*, *model-set mismatch*, *M-open*, *open-set boundary cases*.

Every variant returned prior art. The claim did not survive any of them:

| Attack | Result |
|---|---|
| Is "confidently wrong under mismatch" known? | Berk 1966 (theorem); Lu et al. 2015 (MMAE, real flight data); open-set FD literature (verbatim phrasing) |
| Is "near unknowns are hardest" known? | Yes — established, quantified relationship in open-set recognition |
| Is the blind-spot threshold known? | Yes — unobservability subspaces (Massoumnia et al. 1989); and *Minimal Detectable and Isolable Faults of Active Fault Diagnosis* is a 2023 IEEE TAC paper title (Xu) |
| Is excitation-limited diagnosability known? | Yes — Scott et al. 2014; Kong et al. 2025 Definition 3 |
| Can excitation fix it? | Kong et al. 2025 Lemma 1 — proved, under a richness condition |

**`INTERPRETATION`** A sceptical reviewer would not have to strain. Five independent literatures each
contain a direct answer.

---

## 12. Does the "ML gap" exist?

Applying §19's test: *what problem remains unsolved after applying the strongest existing
non-learning methods?*

| Function | Established non-learning method exists? |
|---|---|
| Uncertainty estimation | Yes — Bayesian/stochastic diagnosability, KL and Bhattacharyya measures |
| OOD / unknown-fault detection | Yes — residual consistency tests, set-membership, GLR |
| Confidence calibration | The defect under mismatch is not calibration; it is the hypothesis space |
| Open-set recognition | Yes — distance/EVT-based rejection, and Kong et al.'s null-return |
| Abstention | Yes — Chow 1970 onward; conformal prediction |
| Active diagnosis | Yes — guaranteed separating inputs, with proofs |

**Answer: none that AURA has demonstrated.**

**`INTERPRETATION`** The residue AURA identified is bounded below by an information-theoretic limit
(a fault too close to a known fault relative to noise carries insufficient information), and learning
does not add information that geometry lacks. The one honest statement AURA could make — "existing
methods assume rejection works; here is a measurement of how often it does not" — depends on an
unbiased fault population AURA does not have.

---

## 13. Publishability assessment

| Dimension | Verdict |
|---|---|
| **Scientific novelty** | **None.** Every finding has established prior art |
| **Methodological novelty** | **None.** χ² consistency testing, marginal likelihood over magnitude, and manifold distance are all standard |
| **Evaluation novelty** | **Weak.** The pre-registered closed-form-prediction-then-test discipline (r = 0.979, 0.9993, 0.973, 99.3%) is unusually rigorous for the field, but rigour of execution is not a contribution |
| **Application novelty** | **Only this.** A self-implemented 6-DOF fixed-wing model — and TV-D10 (never cross-validated) makes even that weak, versus Lu et al.'s real flight data |
| **Negative-result value** | **Low as it stands.** F1 is a negative result about a premise the literature never asserted, on a self-built model. A negative result is publishable when it overturns a belief the field holds; the field does not hold that ambiguity dominates aircraft fault diagnosis at realistic noise |

**`INTERPRETATION`** What would make AURA's negative result valuable is a comparison the project
cannot currently make: showing on a *shared, published* benchmark that a standard method fails where
the field expects it to work. AURA's model is its own.

---

## 14. The cumulative story, argued both ways

**AURA's strongest case.** Four experiments, each pre-registered with falsification criteria, each
reporting its own falsification prominently; four closed-form predictions made before simulation and
confirmed unrefitted; two self-corrections of published claims; a documented departure-from-controlled-
flight failure caught and recorded rather than buried. The project has repeatedly chosen the answer
that damages it. That is real scientific hygiene, and it produced a coherent quantitative picture of
where a template-based diagnostic system is blind.

**The sceptical reviewer.** Every element of that picture was already known, most of it before the
authors were born; the one direction proposed next was published last year with theorems; the
headline rate is an artefact of a fault set the author designed knowing the library; the model is
self-implemented and never validated against flight data; and the project's own best result — a
classical threshold predicting its findings to 99.3% — demonstrates that classical theory already
accounts for everything observed. Rigour of process does not create a contribution.

**`INTERPRETATION`** **The sceptical reviewer is stronger, decisively.** Good methodology applied to a
solved problem yields a well-documented reproduction.

---

## 15. Does EXP-0013 survive?

Per §23, EXP-0013 asked: *can additional excitation resolve near-manifold fault ambiguity?*

**Already solved.** Kong et al. 2025 Lemma 1 proves that optimal controls over a non-degenerate
admissible set guarantee positive separation; Scott et al. 2014 computes guaranteed separating inputs
set-theoretically and handles the empty case. Simulation is not merely unnecessary — it would be a
weaker instrument than the analysis already published.

# `EXP-0013: CANCEL`

---

## 16. Does ML survive?

No unresolved problem was identified for which learning is the appropriate instrument, and per §24
the default therefore stands.

# `ML PHASE: NOT JUSTIFIED`

---

## 17. Major uncertainties and limitations of this audit

**`LIMITATION`** No institutional database access (Scopus, WoS, IEEE Xplore, AIAA ARC). Coverage is
narrower than the Phase 0 protocol specifies.

**`LIMITATION`** Three sources full-text inspected; three abstract-verified verbatim; the remainder
citation-verified via Crossref with content drawn from abstracts and secondary descriptions. Berk
(1966) is cited on the strength of its verified bibliographic record and its standard characterisation
in the misspecification literature — **the paper itself was not read.** Marked `SECONDARY` in the index.

**`LIMITATION`** Absence of a hit is never treated here as evidence of novelty; no N4 is claimed
anywhere in this audit. The FAIL rests on *positive* hits, not on gaps.

**`ASSUMPTION`** Kong et al. (2025) is an arXiv preprint and may not be peer-reviewed. Its priority
claim is therefore weaker than a journal paper's — but it does not stand alone: Scott et al. (2014,
*Automatica*) independently establishes the same conclusion for EXP-0013.

**`INTERPRETATION`** A deeper search would strengthen this verdict, not weaken it. The failure mode of
a thin search is *missing* prior art.

---

## 18. Required final statement

**Reason AURA currently lacks a defensible research gap:**

> Every phenomenon AURA measured — noise-dependent and input-dependent diagnosability, the negligible
> cost of unknown fault magnitude, confident misdiagnosis when the true fault is outside the modelled
> hypothesis set, residual-based rejection of unmodelled faults, the concentration of failures among
> unknown faults that lie close to known ones, and the excitation-dependence of those failures — is
> independently established in the classical FDI, quantitative-diagnosability, Bayesian
> misspecification, open-set recognition, and active-fault-diagnosis literatures, with the specific
> combination AURA proposed to pursue next published in 2025; and AURA's own strongest result, that a
> closed-form classical detectability threshold predicts its blind spots in 99.3% of cells,
> demonstrates that existing theory already accounts for its observations rather than leaving a
> question open.

**What AURA reproduced, stated plainly:** classical model-based FDI residual testing, quantitative
stochastic diagnosability, Bayesian posterior behaviour under M-open misspecification, open-set
recognition's near-class failure mode, and the motivating observation of active fault diagnosis — in
a self-implemented aircraft simulation.

**What remains unknown:** how often unmodelled-fault rejection fails under a *representative* fault
population, rather than an authored one — a question AURA cannot currently answer, whose qualitative
answer is already known, and whose quantitative answer its own 99.3% threshold agreement suggests is
analytically available without new experiments.

**`INTERPRETATION`** Per §30 and §26: no gap is being invented to justify the time already invested.
The correct scientific action is to record this result, publish the negative outcome as the honest
end of the branch, and not begin EXP-0013.
