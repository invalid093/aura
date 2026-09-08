# ADR-0007 — AeroBenchVVPython is GPL-3.0; EXP-0002 uses a self-contained model

**Date:** 2026-09-08 · **Status:** Accepted for EXP-0002; **researcher decision required** for Phase 1b
**Resolves:** open action A-1, assumption A-LIC-01
**Amends:** `ADR-0003-aircraft-model.md`

## Context

ADR-0003 selected AeroBenchVVPython as the primary aircraft model, with licence verification (A-1)
recorded as **blocking**. ADR-0006 deferred AURA's own licensing precisely because the inbound
obligations of its dependencies were unverified.

A-1 is now resolved by direct query of the GitHub API:

```
stanleybak/AeroBenchVVPython  ->  license: GPL-3.0 (GNU General Public License v3.0)
                                  archived: false, last push 2026-03-11
```

**FACT.** The model is GPL-3.0, a strong copyleft licence.

## Why this matters

GPL-3.0 obligations attach to **distribution of derivative works**. Three distinct situations:

| Situation | GPL consequence |
|---|---|
| Run the software locally, publish only *results* (trajectories, matrices, figures) | No copyleft obligation. Program output is not a derivative work of the program |
| Vendor the code into this repository | AURA's distributed code must be GPL-3.0-compatible |
| Publish AURA code that imports it | Generally treated as a derivative work; same obligation |

AURA is a **public repository whose entire purpose is publishing reproducible research code**. The
second and third rows are therefore the operative ones. Adopting AeroBench would bind AURA's code
to GPL-3.0 permanently.

**That is a decision the researcher owns, not an implementation detail.** It is exactly the
commitment ADR-0006 declined to make on a default.

## Decision

**For EXP-0002: do not vendor, import, or depend on AeroBenchVVPython.**

EXP-0002 runs on a **self-contained nonlinear 6-DOF fixed-wing model implemented from published
flight-dynamics equations**, with every parameter stated explicitly in version-controlled
configuration. Designated `GFW-1` (generic fixed-wing, model 1).

This is not a downgrade for this experiment's purpose. ADR-0003 already recorded that a
closed-form-aerodynamics airframe **wins on requirement R4 (analysable equations)** and was rejected
as primary only on envelope width. EXP-0002 tests a mechanism — whether fault distinguishability
varies with operating point — that is generic to fixed-wing aircraft, not specific to any airframe.

## Alternatives considered

- **Adopt AeroBench and licence AURA under GPL-3.0.** Legitimate and possibly the right long-term
  answer. Not taken now because it is an irreversible outbound-licensing commitment belonging to
  the researcher, and EXP-0002 does not require it.
- **Run AeroBench locally, publish only results.** GPL-clean, but it makes the central result
  irreproducible from this repository alone, which contradicts the project's reproducibility
  standard.
- **NASA GTM.** Still blocked on MATLAB (ADR-0003).
- **Reimplement the F-16 from NASA TP-1538 tables.** The tables are several hundred tabulated
  values. They were not available to this session from an independently verifiable source, and
  **fabricating aerodynamic data would be scientific misconduct**. Not attempted.

## Consequences

- **A-SIM-01 is extended.** GFW-1 is a *generic, representative* fixed-wing aircraft. Its parameters
  are physically consistent and fully disclosed, but they are **not** those of any specific
  validated airframe. No AURA result licenses a claim about any real aircraft, including the class
  of aircraft GFW-1 resembles.
- **New limitation (TV-D10):** EXP-0002's conclusion rests on one self-implemented model. Before it
  becomes load-bearing for a published claim, it must be reproduced on an **independently sourced**
  airframe model. This is a stronger requirement than the original TV-D9 (single airframe), because
  the model is now also self-implemented.
- AURA's outbound licence remains undetermined (ADR-0006), and is now *less* constrained, not more.

## Researcher decision required before Phase 1b

Choose one:

1. **Accept GPL-3.0 for AURA** and adopt AeroBench as the primary model (restores ADR-0003).
2. **Keep AURA licence-unencumbered** and adopt an independently sourced permissively-licensed
   airframe, or a published closed-form parameter set with a verifiable citation.
3. **Keep GFW-1** as the primary model and accept TV-D10 as a permanent limitation.

**Option 3 is the weakest scientifically and should not be the default simply because it is the
current state.**

## Revisit when

Phase 1b begins, or sooner if the researcher makes the licensing decision.
