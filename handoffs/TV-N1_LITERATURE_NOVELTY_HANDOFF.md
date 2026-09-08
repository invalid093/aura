# HANDOFF — TV-N1 Blocking Literature & Novelty Audit

**Date:** 2026-09-08 · **Type:** Research-gate investigation.
**No simulation was run. No ML was introduced. No experimental result was modified.**

This handoff is self-contained and independently reviewable without repository access.

---

## Research question at audit start

> **RQ-1.** When an autonomous aircraft's operating regime departs from the conditions under which its
> diagnostic system was developed, does representing *evidential ambiguity* separately from
> *competence loss* produce better act / abstain / escalate decisions than a single scalar confidence?

AURA is an independent computational research project on uncertainty-aware fault diagnosis for
uncrewed aircraft. It uses a self-implemented nonlinear 6-DOF fixed-wing model (GFW-1), a sensor suite
without GPS, and a library of sensor and actuator fault modes. RQ-1 was written before any experiment
and has **not** been rewritten for this audit.

## What the experiments actually established

| ID | Finding | Evidence class |
|---|---|---|
| F1 | The original premise — diagnosis limited by ambiguity among plausible fault hypotheses under realistic uncertainty — is **not supported** | `OBSERVATION` (negative) |
| F2 | At the reference sensor specification, isolation is perfect ($P_{iso} = 1.000$); ambiguity requires 10–19× that noise | `CALCULATION` |
| F3 | Unknown fault magnitude costs ≤3.3 percentage points, and 0.0001 at full observation | `CALCULATION` |
| F4 | When the true fault is absent from the library, the system is confidently wrong; the posterior softmax is *structurally* incapable of expressing this | `FACT` (algebraic) + `CALCULATION` |
| F5 | A χ² goodness-of-fit residual, **added during EXP-0012**, catches 47–83% of mismatch, exactly when a closed-form threshold predicts (1502/1512 cells, **99.3%**) | `CALCULATION` |
| F6 | 5.8% of cells (16.7% at full observation) remain confidently wrong with the residual silent; 14–32 persist at 18 s | `OBSERVATION` |
| F7 | UF-003's detectability ratio peaks at 0.80 when the excitation doublet ends, then **declines** to 0.74 — the failure is excitation-limited, not time-limited | `OBSERVATION` |
| F8 | The size of the persistent dangerous set is threshold-dependent (14–32) | `LIMITATION` |

## Original premise status

**UNSUPPORTED.** Four experiments looked for diagnostic ambiguity under progressively weaker
assumptions and did not find it. The prior cumulative review also judged the programme
**substantially goalpost-shifting**: the target problem changed repeatedly while the intended
solution (uncertainty-aware diagnosis, eventually ML) never did.

## Literature search scope

Seven domains: classical FDI and residual methods; diagnosability and indistinguishability;
active/excitation-based diagnosis; unknown-fault and hypothesis-space mismatch; confidence,
uncertainty and abstention; OOD and open-set recognition; aircraft-specific FDI. Fourteen independent
query formulations, plus conceptual variants (*fault signature similarity*, *semantic proximity*,
*minimum detectable fault*, *model-set mismatch*, *M-open*, *separating input*, *masquerading*), plus
backward citation chaining.

**Inspection discipline:** three sources read in full text; three abstracts read verbatim; every
citation verified against Crossref or a publisher record. **No citation is reproduced from memory.**

**`LIMITATION`** No institutional database access (Scopus, WoS, IEEE Xplore, AIAA ARC). DiVA refused
connections. This audit is **weaker than the systematic search Phase 0 specified** — but a thin search
errs by *missing* prior art, so a deeper search could only strengthen the verdict below.

## Key literature

| Source | Bearing on AURA |
|---|---|
| **Berk 1966**, *Ann. Math. Statist.* 37:51–58 | Under misspecification the posterior concentrates on the KL-nearest member of the model class. **AURA's F4 is a 1966 theorem** |
| **Massoumnia, Verghese & Willsky 1989**, *IEEE TAC* 34:316–321 | Design-time characterisation of undetectable faults via unobservability subspaces |
| **Eriksson, Frisk & Krysander 2013**, *Automatica* 49:1591–1600 | Distinguishability as KL divergence between fault-mode distributions — AURA's deflection coefficient, 13 years earlier and more general |
| **Scott, Findeisen, Braatz & Raimondo 2014**, *Automatica* 50:1580–1589 | Computes inputs **guaranteed** to separate fault scenarios; handles the empty case; states faults "cannot be diagnosed without exciting the system" |
| **Lu et al. 2015**, *Control Eng. Practice* 36:39–57 | MMAE/IMM "display deteriorated performance in case where the model set does not contain a model corresponding to the true system" — **on real flight data** |
| **Lundgren & Jung 2022**, *Control Eng. Practice* 121:105006 | KL diagnosability + open-set classification + fault-size estimation in one paper — spans EXP-0010, EXP-0011 and EXP-0012 |
| **Xu 2023**, *IEEE TAC* 68:1138–1145 | "Minimal Detectable and Isolable Faults of Active Fault Diagnosis" — AURA's candidate contribution is this paper's title |
| **Lima Lopes, Travé-Massuyès, Jauberthie & Alcalay 2024**, DX 2024 | Airbus/LAAS review of air-data-sensor FDI: AURA's exact sensors and faults; names library incompleteness as a design driver |
| **Kong, McMahon & Lahijanian 2025**, arXiv:2509.04708 | **Decisive.** Bayesian FID accounting for unmodelled faults; diagnosability "fundamentally limited by the given control sequence"; active input design; Lemma 1 proves optimal controls guarantee separation |

## Strongest prior-art challenges

1. **Berk 1966** makes EXP-0012's core a sixty-year-old theorem.
2. **Kong et al. 2025** anticipates AURA's *entire* post-EXP-0012 direction — unmodelled faults,
   excitation-limited diagnosability, and active input design — in an aerospace department, with
   theorems where AURA has simulations.
3. **Scott et al. 2014** provides a *guarantee* where EXP-0013 proposed a simulation sweep.
4. **Lu et al. 2015** documents AURA's F4 as a known limitation of aircraft multiple-model FDI, on
   real flight data, against AURA's never-validated self-built model.
5. **Lima Lopes et al. 2024** shows that fault-library incompleteness is a stated design driver in
   AURA's exact application domain, and that the field's declared open problems — interpretability
   for certification, and *when* false alarms cluster — are ones AURA does not study.

## Strongest potential novelty

Kong et al. **assume** (Assumption 2) that an unmodelled fault is diagnosable — i.e. that rejection
works. AURA **measured** what happens when that assumption fails.

**This does not survive scrutiny.** The qualitative answer is already established (open-set rejection
degrades as unknowns approach known classes); the quantitative answer is the classical
minimum-detectable-fault threshold; AURA's 5.8% rate is determined entirely by six unseen faults the
author designed while knowing the library; and — decisively — **AURA's own strongest result, that the
closed-form threshold predicts blindness in 99.3% of cells, is evidence that classical theory already
accounts for the phenomenon.** A result predicted to 99.3% by a textbook expression is not an open
question. Classified **N2**, and not adequate to justify a programme.

## Novelty matrix summary

Thirteen candidate claims were classified. **Twelve are N0 (established) or N1 (known principle, new
implementation). One is N2. None reaches N3 or N4.** No N4 is claimed anywhere; the verdict rests on
positive prior-art hits, never on absence of search results.

## Closest-paper comparison

> *If a reviewer knew Kong et al. 2025, Lundgren & Jung 2022 and Scott et al. 2014, what would they
> say AURA adds?*
>
> "That it ran this on its own 6-DOF fixed-wing simulation with six unseen faults it designed itself,
> and reported the fraction that evaded rejection — a fraction determined by the fault set the author
> chose. **This is a different aircraft model.**"

Per the audit specification, an answer of that form is **N1**, not novelty.

## Red-team findings

A second search was run specifically to destroy the near-manifold claim, using conceptual rather than
literal variants. Every variant returned prior art; the claim survived none of them. Five independent
literatures each contain a direct answer: Bayesian misspecification, classical FDI, quantitative
diagnosability, open-set recognition, and active fault diagnosis.

## Remaining research gap

**None that is defensible.** What remains genuinely unknown is how often unmodelled-fault rejection
fails under a *representative* fault population rather than an authored one — a question whose
qualitative answer is already published, whose analytic answer AURA has itself already confirmed to
99.3%, and which AURA cannot currently address because it has no unbiased fault generator.

**No gap is being invented to justify the time already invested.**

## Major uncertainties

- Kong et al. (2025) is an arXiv preprint whose peer-review status is unconfirmed. Its priority claim
  is therefore weaker than a journal paper's — but it does not stand alone: Scott et al. (2014,
  *Automatica*) independently supports the same EXP-0013 conclusion.
- Berk (1966) is cited on its verified bibliographic record and its standard characterisation in the
  misspecification literature. **The paper itself was not read**, and it is marked `SECONDARY` in the
  literature index.
- Three of AURA's own limitations remain unmitigated and unaffected by this audit: TV-D10
  (self-implemented airframe, never cross-validated), the ADR-0005 GPS-exclusion sensitivity run that
  was mandated at Phase 0 and never performed, and the absence of any stated operational
  false-confidence requirement.

## Limitations of the literature search

Narrower than the Phase 0 protocol requires: no institutional database access, no formal
forward-citation sweep, several key sources assessed from verbatim abstracts plus verified metadata
rather than full text. **This is a real weakness and should be recorded as one.** It cannot, however,
reverse the verdict: the failure mode of a thin search is missing prior art, and this search still
returned multiple independent hits against every AURA finding.

---

# NOVELTY GATE: FAIL

Every substantive phenomenon AURA measured is already established, most of it decades ago, and the
one direction the cumulative review identified as strongest was published in September 2025 with
proofs. AURA's findings map one-to-one onto Berk's 1966 misspecification theorem, the classical
model-based FDI residual test, the quantitative stochastic diagnosability literature, open-set
recognition's near-class failure mode, and the founding premise of active fault diagnosis. The one
seam — that Kong et al. assume rejection works where AURA measured it failing — is undercut by AURA's
own best result: a closed-form classical threshold predicts its blind spots in 99.3% of cells, which
shows existing theory already explains the observations rather than leaving a question open. A FAIL is
a valid scientific outcome and is recorded here as one: the branch has been well executed and is
redundant.

# EXP-0013: CANCEL

EXP-0013 asked whether additional excitation can resolve near-manifold fault ambiguity. That question
is already solved, and by stronger instruments than the one proposed. Scott et al. (2014) compute the
set of inputs guaranteed to separate fault scenarios and explicitly handle the case where no such
input exists; Raimondo et al. (2016) extend this to the closed loop AURA operates in; Kong et al.
(2025) Lemma 1 proves that optimal controls over a non-degenerate admissible control set guarantee
positive separation, in a Bayesian framework that already accounts for unmodelled faults. Running
EXP-0013 would reproduce in simulation, on an unvalidated airframe, a result that exists in the
literature as a theorem. Cancelled rather than deferred or redesigned: this is not a scoping problem
that a narrower question would fix.

# ML PHASE: NOT JUSTIFIED

Established non-learning methods exist for every function AURA contemplated giving to a learned
model: uncertainty estimation (KL- and Bhattacharyya-based stochastic diagnosability), OOD and
unknown-fault detection (residual consistency tests, set-membership methods, GLR), open-set
recognition with rejection (distance- and EVT-based, and Kong et al.'s null return), abstention (the
reject option, selective classification, conformal prediction), and active diagnosis (guaranteed
separating inputs). Applying the audit's own test — *what problem remains unsolved after the strongest
existing non-learning methods have been applied?* — the answer is none that AURA has demonstrated. The
residue AURA identified is bounded below by an information-theoretic limit: a fault too close to a
known fault relative to noise carries insufficient information to distinguish, and learning adds no
information that geometry lacks. ML remains not justified, and the original intention to reach an ML
phase is not a reason to proceed.
