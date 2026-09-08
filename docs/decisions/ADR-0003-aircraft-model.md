# ADR-0003 — Aircraft model selection

**Date:** 2026-09-08 · **Status:** Accepted, blocked on open action A-1 (licence verification)

## Context

Seven modelling approaches were surveyed (`reports/phase0/AIRCRAFT_MODEL_SURVEY.md`). RQ-1 requires
nonlinear 6-DOF dynamics, a wide documented envelope, exact ground truth, **analysable equations**,
and low per-run cost. The governing constraint turned out to be equation availability, not fidelity.

## Decision

**Primary: AeroBenchVVPython** — the Python F-16 model built on NASA TP-1538 aerodynamics
(LIT-0020, LIT-0021, LIT-0022).

Supporting roles:
- An LTI model at trim points for implementation and metric verification (EXP-0004).
- F16Model.jl or JSBSim as independent-implementation test environments for simulation-bias
  mitigation.
- A small fixed-wing UAS model (Aerosonde-class) as the fallback primary.

## Alternatives considered

- **NASA GTM / AirSTAR.** Scientifically the best heritage of any candidate — purpose-built for
  in-flight failure emulation and backed by dynamically-scaled flight test. Rejected *only* because
  it requires MATLAB/Simulink, which conflicts with the open-reproducibility goal. If MATLAB access
  exists, this is the strongest alternative and this ADR should be reopened.
- **Small UAS (Aerosonde-class).** Better for structural analysis, since its aerodynamics are
  closed-form rather than tabulated. Rejected as primary because its narrow envelope weakens the
  physical meaning of regime shift — the property RQ-1 depends on most. Retained as fallback.
- **JSBSim.** More capable than needed, and its capability lies in dimensions RQ-1 does not use.
  Extracting a clean equation set from XML-configured aero and engine models is substantial work
  with no research payoff.
- **PX4 / ArduPilot SITL, X-Plane.** Rejected on equation transparency and per-run cost.

## Consequences

- **A-SIM-01 binds:** this is a *representative* nonlinear high-performance aircraft built from 1979
  wind-tunnel data, **not** a validated model of a real F-16. No result licenses any claim about a
  real aircraft. This must appear in every report.
- The model is not chosen because it is an F-16. Had the small-UAS model had a wider envelope it
  would have won on analysability. This is recorded to guard against TV-F1 (recognisability
  substituting for justification).

## Revisit if

- A-1 finds the licence unsuitable for research use or derived-data redistribution.
- EXP-0002 shows the equation set cannot be structurally analysed → switch to the small-UAS fallback.
- EXP-0001 shows per-run runtime makes the full experiment infeasible on one machine.
