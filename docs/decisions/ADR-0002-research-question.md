# ADR-0002 — Research question selection

**Date:** 2026-09-08 · **Status:** Accepted, provisional on TV-N1

## Context

The original framing — *How can an autonomous high-performance aircraft detect, isolate and respond
to sensor and system degradation when human intervention is delayed or unavailable?* — contains at
least four separable research programmes (detection, isolation, response selection, human-interaction
timing), specifies no comparison, and has no falsification condition. It is an engineering prompt,
not a hypothesis.

Six candidate directions (RD-A … RD-F) were developed and scored in
`reports/phase0/RESEARCH_DIRECTION_COMPARISON.md`.

## Decision

Adopt **RD-G**: separate representation of *evidential ambiguity* ($A$) and *competence loss* ($N$),
tested by whether it changes act / abstain / escalate decisions under combined regime-and-fault
shift.

Reasons, in order of weight:

1. **There is ground truth for the uncertainty itself.** Structural isolability, computed per flight
   condition, provides an analytic reference for what the ambiguity component *should* say. UQ
   research rarely has this.
2. **There is a specific, pre-registered way to fail.** The LIT-0012 equivalence result predicts
   that estimator choice will not change decisions. That prediction is adopted as the falsification
   condition rather than argued away.
3. **It measures a quantity the closest prior work explicitly declined to measure** — LIT-0004's
   stated limitation about shift/fault confounding, formalised as H3.

## Alternatives considered

| Rejected | Reason |
|---|---|
| RD-A — UQ under shift | Replication of LIT-0004/0005 with an aircraft attached |
| RD-B — hybrid physics/ML | A design choice for AURA, not a research question; expected answer known |
| RD-C — diagnosability limits | A computation, not an experiment. Retained as the ground-truth enabler |
| RD-D — abstention | Thin alone; LIT-0004 already abstains under high epistemic uncertainty |
| RD-E — degraded-mode selection | Direct adversarial prior (LIT-0012) with no stated reason aerospace would differ |
| RD-F — self-aware health management | Not falsifiable as phrased. Retained as motivation only |

All six remain in `research/hypotheses/` and may be revisited if RD-G is invalidated.

## Consequences

- Fault-tolerant control, prognostics, planning and human-subject work fall out of scope
  (`docs/scope.md`).
- The design depends on structural isolability varying with flight condition. **EXP-0002 tests this
  directly and can invalidate this decision at near-zero cost.**
- On current evidence the most likely outcome is **H1 falsified and H3 supported**. That combination
  is planned for as a publishable result, not treated as failure.

## Revisit if

- A systematic literature search closes gap G4 or G6 (TV-N1).
- EXP-0002 shows flight-condition-invariant isolability.
- H2 and H3 are both falsified.
