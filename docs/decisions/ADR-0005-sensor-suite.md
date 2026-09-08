# ADR-0005 — Sensor suite excludes GPS

**Date:** 2026-09-08 · **Status:** Accepted, with a mandatory sensitivity run

## Context

H2 requires a non-trivial ambiguity structure: some fault hypotheses must be genuinely
indistinguishable, and *which* ones must depend on flight condition. A fully redundant sensor suite
would make every fault isolable and leave H2 with nothing to measure.

## Decision

A 13-channel suite: body angular rates ($p,q,r$), body specific forces ($a_x,a_y,a_z$), air data
($V_t, \alpha, \beta$), barometric altitude, and attitude ($\phi,\theta,\psi$).
**GPS position/velocity and magnetometer are excluded.**

## Why this is uncomfortable, and recorded as such

Excluding a sensor because including it would weaken the effect under study is exactly the kind of
choice that produces a result which does not generalise. It is recorded as **A-SEN-01: the most
questionable choice in the design.**

The defence is that a navigation-degraded or GNSS-denied condition is a genuine operating case
rather than a contrivance. That defence is an argument, not evidence, and it is labelled as such.

## Consequence: a mandatory sensitivity run

**EXP-0009 repeats the primary comparison with GPS included.** This is declared now, before any
results exist, so that it cannot later be characterised as a response to an unwelcome outcome.

If AURA's advantage disappears when GPS is included, the honest finding is:

> *the decomposition matters only in under-determined sensor suites*

— a narrower but still legitimate result, and it will be reported as the headline rather than as a
footnote.

## Alternatives considered

- **Include GPS from the start.** Would likely collapse the air-data ambiguity structure, leaving
  H2 without a measurable effect. Retained instead as the sensitivity condition, which is strictly
  more informative than choosing one or the other.
- **Triplex redundant sensors.** Turns sensor-fault isolation into a voting problem — a different
  and largely solved research question.

## Revisit if

EXP-0002 shows the isolability structure at this suite is trivial (fully diagonal) or degenerate
(fully dense). The suite is then adjusted **before** any data generation, not after seeing results.
