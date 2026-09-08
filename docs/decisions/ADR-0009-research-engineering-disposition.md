# ADR-0009 — AURA research-engineering disposition

**Status:** Accepted · **Date:** 2026-09-08 · **Decision-maker:** researcher
**Supersedes:** the scientific scope defined in ADR-0002 (research question) as the
project's *primary* purpose. ADR-0002 is **not** withdrawn: it remains the record of what
was asked and is required to make sense of EXP-0002 → EXP-0012.

> Filed in `docs/decisions/` alongside ADR-0001…ADR-0008 rather than in a new `docs/adr/`
> directory, so that the decision record remains a single sequence.

---

## Context

### Original purpose

AURA was established to investigate **RQ-1**: whether representing *evidential ambiguity*
separately from *competence loss* produces better act / abstain / escalate decisions than
a single scalar confidence, in uncertainty-aware fault diagnosis for uncrewed aircraft.
The intended destination was a decision layer with machine-learning baselines.

### Evidence leading to termination

Four pre-registered experiments were run. Each reported its own falsification.

| Experiment | Result bearing on the premise |
|---|---|
| EXP-0002 | Deterministic ambiguity exists, but condition dependence is weak — **1 verdict flip in 153 pairs**. FAIL-0001: one flight condition departed controlled flight and was excluded |
| EXP-0010 | At the reference sensor specification **P_iso = 1.000** — no practical ambiguity. Ambiguity requires 10–19× the reference noise. EXP-0002's threshold was conservative by exactly √(KN) ≈ 153 |
| EXP-0011 | Unknown fault magnitude costs **0.0001** at full observation. A prior *excluding* the truth costs 6.5–13.3 points and worsens with data |
| EXP-0012 | With the true fault absent from the library, 5.8% of cells are confidently wrong with the residual silent; a χ² residual catches 47–83%, exactly where a closed-form threshold predicts (**1502/1512, 99.3%**) |

The **cumulative review** (EXP-0002 → EXP-0012) found the original premise
**unsupported**, and judged the programme **substantially goalpost-shifting**: the target
problem changed repeatedly while the intended solution never did. It also corrected two of
the project's own published claims.

### Novelty audit

**TV-N1**, declared at Phase 0 as a *blocking gate on any novelty claim*, was finally
performed and returned **`NOVELTY GATE: FAIL`**. Every substantive finding has established
prior art: Berk (1966) for posterior concentration under misspecification; Massoumnia,
Verghese & Willsky (1989) for design-time characterisation of undetectable faults;
Eriksson, Frisk & Krysander (2013) for quantitative noise-aware distinguishability;
Lundgren & Jung (2022) for open-set fault classification with fault-size effects; Scott et
al. (2014) and Kong et al. (2025) for excitation-limited diagnosability and active input
design. EXP-0013 was **cancelled**; the ML phase remains **not justified**.

## Alternatives considered

1. **Continue the scientific branch with a narrower question.** *Rejected.* The audit
   found no gap at N3 or above. Continuing would mean inventing a gap to justify time
   already invested — the precise behaviour the cumulative review identified and the
   novelty audit was commissioned to prevent.
2. **Proceed to the ML phase as originally planned.** *Rejected.* Established non-learning
   methods exist for every function ML was to serve, and the residue is bounded by an
   information-theoretic limit that learning does not lift. Proceeding would be
   motivated-by-plan rather than motivated-by-evidence.
3. **Archive the project entirely.** *Rejected, but seriously considered.* The scientific
   record is genuinely closed. However the infrastructure built to reach that conclusion —
   and the discipline that produced two self-corrections and an honest FAIL — is reusable
   and independently valuable.
4. **Rebuild the framework from scratch as a generic tool.** *Rejected.* The existing
   components are sound and their design is grounded in specific observed failures.
   Rebuilding would discard exactly the evidence that justifies the design.

## Decision

**AURA is redefined as a research-engineering project:**

> a reproducible and auditable computational research framework for designing, executing,
> validating, analysing and documenting aerospace engineering experiments.

The portfolio contribution is the **research infrastructure and engineering methodology**,
not a fault-diagnosis algorithm.

## New scope

**In scope:** experiment specification and pre-registration; specification validation;
reproducible execution with provenance; deterministic seed control; a reusable Monte Carlo
engine; statistical sufficiency and convergence; automated validity gates; failure
registry; evidence classification; evidence packaging; report and handoff generation;
experiment comparison; retention policy; regression tests derived from real research
failures; a CLI.

**Out of scope (explicit non-goals):** a production aircraft health-management system; a
novel FDI algorithm; an ML platform; a flight-control system; a safety-certification
framework; any claim of real-aircraft or operational applicability.

## Consequences

**Positive.** The failed research branch becomes the framework's most informative test
case: FAIL-0001 is now the `model_validity_envelope` gate plus three regression tests; the
duplicate-template incident is `assert_distinct`; the mismatched-N label is
`assert_reported_n`; the non-dividing timestep is part of `numerical_validity`; the
asymmetric admissible sets of EXP-0011 are `assert_symmetric_sets` and the comparison
module. Past research failures became permanent engineering tests.

**Negative.** AURA no longer has a scientific claim. The portfolio must be presented as an
engineering contribution, and any presentation implying novel aerospace science would be
false. The specific prohibited claims are listed in the portfolio handoff.

**Neutral.** The historical research record (EXP-0002 → EXP-0012, the cumulative review,
the TV-N1 audit, FAIL-0001, all ADRs) is **preserved unedited**. It is not rewritten to
make the portfolio project appear successful; the sequence *hypothesis → experiment →
falsification → audit → termination* is itself the evidence for the methodology.

## Completion criteria

The twelve criteria in
[`docs/RESEARCH_ENGINEERING_MISSION.md`](../RESEARCH_ENGINEERING_MISSION.md#completion-criteria),
demonstrated by both a passing experiment (`DEMO-0001`) and a deliberately rejected one
(`DEMO-0002`), with a regression suite that runs on Python and numpy alone.

## Compliance

This ADR exists because the project's operating instructions forbid changing the research
question, the scope, or the scientific interpretation of a result silently. The identity
change recorded here was requested by the researcher and is documented publicly rather
than applied quietly.
