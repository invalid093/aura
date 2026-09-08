# ADR-0008 — "Structural isolability" was the wrong term; EXP-0002 measures response-based distinguishability

**Date:** 2026-09-08 · **Status:** Accepted
**Amends:** `docs/hypotheses.md` (H2), `docs/assumptions.md` (A-UNC-03, A-FLT-03),
`reports/phase0/EXPERIMENTAL_DESIGN_PRELIMINARY.md` (§9 gate EXP-0002)

## Context

Phase 0 specified EXP-0002 as computing "the structural isolability matrix at ≥3 flight conditions",
with the pre-declared pass condition that the matrix must **differ across flight conditions**.

Setting up the experiment exposed a definitional error in that specification.

## The error

**FACT.** Structural isolability, in the sense of Frisk and Krysander (LIT-0001, LIT-0002, LIT-0003),
is computed from a model's **incidence structure** — which variables and faults appear in which
equations. It is a combinatorial property of the equation set.

**Therefore it cannot depend on flight condition.** The equations of a 6-DOF aircraft have the same
incidence structure at 25 m/s and at 250 m/s: the same variables appear in the same equations. Only
the *numerical values* change.

**INTERPRETATION.** The Phase 0 gate as literally written was **unfalsifiable in the wrong
direction**: a correctly-executed structural analysis would return an identical matrix at every
flight condition, EXP-0002 would "FAIL", and the AURA design would have been abandoned on the basis
of a definitional artefact rather than a fact about aircraft.

This is a genuine error in the Phase 0 specification, found before it did damage. It is recorded
here rather than quietly corrected.

## The correction

EXP-0002 measures **response-based fault distinguishability** (also called quantitative
diagnosability or fault discernibility): whether two faults produce measurably different measured
output trajectories under identical conditions and excitation.

This quantity **is** flight-condition-dependent, through well-understood physics — dynamic pressure
scales aerodynamic forces and control effectiveness; trim angle of attack changes the operating
point on nonlinear aerodynamic curves; closed-loop dynamics change with both. It is the quantity
the AURA design actually needs.

| | Structural isolability | Response-based distinguishability |
|---|---|---|
| Computed from | Equation incidence structure | Simulated output trajectories |
| Depends on parameter values | No | Yes |
| Depends on flight condition | **No** | **Yes** |
| Depends on excitation | No | **Yes** |
| Depends on fault magnitude | No | Yes |
| Gives | Necessary conditions | Achievable separation at a stated operating point |

The two are complementary, and the relationship is one-directional and worth stating: **structural
isolability is a necessary condition.** Faults that are structurally indistinguishable can never be
separated by any method. Faults that are structurally isolable may still be practically
indistinguishable at a given condition, magnitude and noise level. Response-based distinguishability
measures the second, tighter, condition.

## Consequences for the hypotheses

- **H2's ground truth changes.** The reference for the evidential-ambiguity component $A$ is
  response-based distinguishability at the current flight condition — **not** the structural
  isolability matrix. Structural isolability is retained as an outer bound.
- **A-UNC-03 is amended.** It previously read that structural isolability is a valid lower bound on
  ambiguity. That remains true but is too weak to serve as H2's reference on its own.
- **A-FLT-03 is unchanged in substance** — it claims the F2/F6 ambiguity pair is
  flight-condition-dependent, which is a response-based claim and is exactly what EXP-0002 tests.
- **The pre-declared PASS/FAIL criteria are unchanged.** Not diagonal, not dense, meaningful
  ambiguity, differs across conditions. Only the quantity being thresholded is corrected. The
  criteria were fixed before results and are not being relaxed.

## Alternatives considered

- **Run the structural analysis as literally specified.** Rejected: it would produce a guaranteed
  FAIL for a definitional reason, which would be a misleading result, not a scientific one.
- **Quietly redefine the gate.** Rejected: `CLAUDE.md` prohibits silently changing experimental
  criteria, and the correction is scientifically interesting in its own right.
- **Do both.** A structural analysis is worth running later as an outer bound. It is not run in
  EXP-0002 because it cannot answer EXP-0002's question, and the model's incidence structure is
  simple enough that its result is largely foreseeable.

## Consequence for terminology

Reports use **"response-based distinguishability"** or **"fault distinguishability"**. Where
"structural isolability" appears in Phase 0 documents referring to this gate, it should be read as
the corrected term. `CLAUDE.md`'s terminology rules are extended accordingly.

## Revisit if

A structural analysis is later run as an outer bound and disagrees with the response-based result —
i.e. a pair found distinguishable by simulation is structurally non-isolable. That would indicate
an implementation error in one of the two, and would be important.
