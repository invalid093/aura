# Case study — how AURA's research branch was terminated, and what it taught the framework

**Date:** 2026-09-08 · **Type:** methodology case study

This is the record of a research programme that ran four pre-registered experiments,
falsified its own premise, corrected two of its own published claims, failed its own
blocking novelty gate, and stopped. It is presented as a case study because the *process*
is the transferable result — and because most of AURA's engineering design is a direct
response to something in it.

---

## 1. The original hypothesis

**RQ-1**, written before any experiment:

> When an autonomous aircraft's operating regime departs from the conditions under which
> its diagnostic system was developed, does representing **evidential ambiguity**
> separately from **competence loss** produce better act / abstain / escalate decisions
> than a single scalar confidence?

The causal claim underneath it: ambiguity and competence loss have *opposite* correct
responses, a scalar confidence cannot separate them, therefore separating them improves
decisions. The premise this rested on was that **diagnosis is fundamentally limited by
ambiguity among plausible fault hypotheses under realistic uncertainty**.

Phase 0 recorded, in advance, that the most likely outcome was that the main hypothesis
would be falsified. That prediction turned out to be correct, and it is worth noting that
it was written down *before* the evidence arrived.

## 2. Experimental progression

| Experiment | Question | What was found |
|---|---|---|
| **EXP-0002** | Does fault distinguishability vary with flight condition? | Ambiguity exists deterministically; a stable 5-member indistinguishable group at every valid condition; cross-condition rank correlation monotone in operating-point separation (0.984 → 0.658). But only **1 verdict flip in 153 pairs** |
| **EXP-0010** | Does it survive measurement noise? | **P_iso = 1.000** at the reference sensor spec — *zero* ambiguous pairs. Ambiguity needs 10–19× the reference noise. The binding constraint is observation **time** (~5 s), not noise |
| **EXP-0011** | Does unknown fault magnitude create it? | Unknown magnitude costs ≤3.3 points, and **0.0001** at full observation. A prior *excluding* the truth costs 6.5–13.3 points and uniquely **worsens with more data** |
| **EXP-0012** | What if the true fault is absent from the library? | Confidently wrong with the residual silent in **5.8%** of cells (16.7% at full window). A χ² residual catches 47–83% — exactly where a closed-form threshold predicts, **1502/1512 cells (99.3%)** |

A methodological habit ran through all four: **derive a closed-form prediction, register
it, then test it unrefitted.** Agreement was r = 0.979, r = 0.9993, r = 0.973, and 99.3%.
That habit is why the eventual negative verdict is credible — the apparatus demonstrably
predicted its own results.

## 3. Unexpected and negative results

- **The motivating ambiguity was simply absent** at realistic noise. Not weak: 1.000 where
  the premise predicted degradation.
- **EXP-0010 falsified EXP-0002's own threshold**, showing it conservative by exactly
  √(KN) ≈ 153. The project's second experiment invalidated its first experiment's headline
  interpretation.
- **EXP-0011's most important finding arrived by accident.** Case B was designed to test
  bounded knowledge and instead tested *prior misspecification*, because its truths were
  drawn from the full grid while its prior was not. The project's most significant pivot
  originated in a specification defect — which was reported rather than quietly reframed.
- **EXP-0012 found a real failure mode**, and it was not the one AURA was built around.

## 4. Methodological corrections

Each of these was recorded at the time, and each now has an engineering counterpart.

| Incident | Consequence | Now enforced by |
|---|---|---|
| **FAIL-0001** — flight condition FC-4 departed controlled flight (α reached 31.5°) while producing the *most favourable-looking* matrix in the study | Condition excluded, experiment re-run, validity gate added to the pipeline | `model_validity_envelope` gate; required `validity_envelope` field; 3 regression tests; `DEMO-0002` |
| A silent patch failure on a whitespace mismatch produced **nine duplicate nominal templates** | First run discarded; all later patches assertion-checked | `integrity.assert_distinct`, `integrity.assert_patch_applied` |
| A determinism label hard-coded "72 runs" while 90 were checked | Label-only defect, but undetectable by a reader | `integrity.assert_reported_n`; `data_completeness` gate |
| `dt = 0.004` does not divide a 100 Hz sample interval | Corrected during pilot verification | `integrity.assert_divides`; `numerical_validity` gate |
| EXP-0011 Case A could select a hypothesis Cases B/C could not — the central comparison was between differently-shaped admissible sets | Experiment re-run | `integrity.assert_symmetric_sets`; `aura.compare` blocking differences |
| A discrete grid overstated near-intersection separation by up to 19.9× | Primary measure changed to the continuous manifold minimum | Recorded as a deviation; `deviations` is a required report section |
| MIT licence added by default, violating the repository policy | Removed; ADR-0006; unpublished commit amended | Policy check in the release audit |
| Personal email in git commit identity | Amended to a GitHub noreply address, objects pruned | Release audit item 3 |

**`INTERPRETATION`** The pattern worth noticing: in every case the defect was found by a
*check*, not by intuition — and in two of the three pilot-stage cases (EXP-0012) the bug
turned out to be **in the check, not the design**. That is an argument for making checks
first-class, testable artefacts rather than ad-hoc script fragments, which is what the
gate architecture does.

## 5. The novelty audit

Phase 0 declared **TV-N1** — a systematic literature search — a *blocking gate on any
novelty claim*. **Four experiments ran past it.**

The cumulative review identified this as the project's single most consequential process
failure and recommended closing the gate before any further experiment. The audit was then
performed adversarially: searching not for support, but for evidence that would make AURA
unnecessary.

## 6. What the literature said

| AURA finding | Prior art |
|---|---|
| Confidently wrong when the true fault is outside the hypothesis set | **Berk (1966)** — under misspecification the posterior concentrates on the KL-nearest member of the model class. Documented for aircraft MMAE on **real flight data** by Lu et al. (2015) |
| A χ² residual catches most mismatch | The classical model-based FDI consistency test; **Massoumnia, Verghese & Willsky (1989)** characterised undetectable faults geometrically |
| A closed-form detectability threshold enumerates blind spots | The classical *minimum detectable fault* — **Xu (2023, IEEE TAC)** is titled *Minimal Detectable and Isolable Faults of Active Fault Diagnosis* |
| Quantitative, noise-aware distinguishability | **Eriksson, Frisk & Krysander (2013)** — the same construct as AURA's deflection coefficient, thirteen years earlier |
| Near-manifold unknowns are the dangerous ones | The expected, measured result of open-set recognition |
| Near-manifold failure is excitation-limited; excitation could fix it | **Scott et al. (2014)** compute *guaranteed* separating inputs; **Kong et al. (2025)** prove optimal controls guarantee separation, in a Bayesian framework that already accounts for unmodelled faults |

The verdict was **`NOVELTY GATE: FAIL`**. Of thirteen candidate claims, twelve were N0/N1
and one was N2; none reached N3 or N4.

The sharpest argument came from AURA's own data: **a closed-form classical threshold
predicted its blind spots in 99.3% of cells.** A phenomenon that a textbook expression
predicts that well is not an open question. The project's strongest result was the
strongest evidence against its own novelty.

## 7. Cancelling EXP-0013

EXP-0013 was to ask whether additional excitation could resolve near-manifold ambiguity.
The cumulative review had called this the strongest remaining direction, supported by a
genuine measurement: UF-003's detectability ratio *peaks* at 0.80 exactly when the
excitation doublet ends and then *declines* to 0.74.

The literature answered it with theorems. Scott et al. (2014) compute the set of inputs
guaranteed to separate fault scenarios and handle the case where that set is empty;
Raimondo et al. (2016) extend it to the closed loop AURA operates in; Kong et al. (2025)
Lemma 1 proves optimal controls over a non-degenerate admissible set guarantee positive
separation.

**`EXP-0013: CANCEL`** — cancelled rather than deferred or redesigned. A narrower question
would not have helped: the answer already exists, in stronger form than a simulation on an
unvalidated airframe could produce.

## 8. Why the project stopped searching for a more convenient failure mode

This is the part worth being explicit about.

After each null result, a weaker assumption was relaxed and the search continued: noise →
magnitude → taxonomy. The documented fallback, had EXP-0012 also come out negative, was to
relax the *next* assumption (model/template error). The cumulative review asked the
required bias question — *would this direction still have been selected if EXP-0012 had
produced a negative result?* — and answered **almost certainly not**.

That is the signature of a programme searching for a justifying problem rather than
testing a hypothesis. Each experiment was individually falsifiable; the *programme* was
not, because the intended solution never changed while the target problem did.

Stopping was therefore not a judgement that the remaining questions were uninteresting. It
was the recognition that continuing would mean selecting the next question by whether it
kept the project alive. **A research programme that cannot be ended by evidence is not a
research programme.**

## 9. How the experience shaped AURA's architecture

Almost every design decision in the framework traces to something above.

| Framework feature | Origin |
|---|---|
| `validity_envelope` is a **required** field; the gate marks excursions `INVALID` | FAIL-0001 — the invalid condition produced the best-looking numbers |
| A gate that cannot be evaluated **raises** and never returns PASS | The same: absence of a check must never read as a passed check |
| A rejected run's report contains an explicitly **empty** "what the evidence supports" section rather than omitting it | So that emptiness is visible rather than inferred |
| Report generator refuses researcher-supplied measured evidence classes | Recurring risk of laundering assertion into measurement |
| Measured and inferred content are placed in physically separate sections | Evidence classification, formalised |
| N is **derived** from a declared precision target | "Run N because the researcher typed N" |
| Failed Monte Carlo trials are **recorded, never dropped** | Dropping failures biases the estimate |
| Zero surviving samples **raises** rather than returning an estimate | Absence of evidence is not a weak result |
| Status transitions are enumerated and require a **reason** | Silent methodological change |
| Failure records are append-oriented; `RESOLVED` requires recorded verification | "An unverified correction is a claim, not a fix" |
| `aura compare` blocks on differing model version, datasets or controlled variables | EXP-0011's asymmetric admissible sets |
| Specification is content-hashed, excluding status and path | Detect a changed pre-registration; ignore lifecycle noise |
| A **deliberately failing** demonstration ships with the framework | A framework that only demonstrates its successes demonstrates nothing |
| TV-N1 recorded as *realised, not mitigated* | The gate that was run past four times |

Two bugs were found **in the framework itself** during this conversion, by its own tests
and demonstrations, and both are recorded rather than quietly fixed:

- the automatic failure-id allocator would have re-issued `FAIL-0001`, overwriting the
  historical FC-4 record's identifier, because it scanned only its own YAML format;
- a run that crashed during execution reported `conclusion_emitted: true`, because the
  status was `FAILED` while its preflight gates had all passed.

Both now have regression tests.

## 10. What this case study does and does not show

**`OBSERVATION`** It shows a complete research cycle — *hypothesis → experiment →
falsification → audit → termination* — executed with pre-registration, self-correction,
and an explicit stop.

**`LIMITATION`** It does **not** show that the underlying aerospace question is
uninteresting; it shows that *this* investigation of it was not novel and that its premise
was unsupported in *this* configuration.

**`LIMITATION`** The literature audit was narrower than the Phase 0 protocol specified: no
institutional database access, several sources assessed from verbatim abstracts plus
verified metadata rather than full text. A deeper search could only deepen a FAIL, but the
limitation is real and is recorded in the audit itself.

**`INTERPRETATION`** The transferable claim is narrow and, I think, defensible: research
infrastructure that makes assumptions, failures, uncertainty and provenance explicit will
sometimes tell you to stop — and a project that can act on that is worth more than one
whose apparatus can only confirm.
