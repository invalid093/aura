# Aircraft Model Survey — Phase 0

**Date:** 2026-09-08
**Question this survey must answer:** What is the **minimum** model fidelity required by RQ-1?
**Decision record:** `docs/decisions/ADR-0003-aircraft-model.md`

---

## 1. What the research question actually requires

RQ-1 needs a simulation environment with five properties. Anything beyond these is cost, not value.

| # | Requirement | Why RQ-1 needs it |
|---|-------------|-------------------|
| R1 | **Nonlinear, coupled 6-DOF dynamics** | Residual structure must genuinely change with flight condition. In an LTI model, "flight-regime shift" is not a physical phenomenon — it is a parameter change I imposed. H2's ground truth would be circular. |
| R2 | **A wide, documented flight envelope** | The shift axis (airspeed / altitude / load factor / angle of attack) must span a range over which the dynamics *actually* differ. A model valid only near one trim point cannot support a shift study. |
| R3 | **Exact ground truth for state and fault** | Non-negotiable. Diagnosis performance and uncertainty calibration cannot be scored without it. |
| R4 | **An analysable equation structure** | Structural isolability (H2's ground truth) requires a declarable set of equations relating states, inputs, measurements and faults. A black-box binary simulator cannot supply this. |
| R5 | **Cheap enough for Monte Carlo** | Tens of thousands of runs. A model requiring seconds-to-minutes per second of simulated time is disqualifying. |

**Explicitly NOT required:** aeroelasticity, engine thermodynamics, actuator hardware modelling,
atmospheric turbulence spectra beyond a simple gust model, visual/graphical output, real-time
operation, certified aerodynamic accuracy.

**INTERPRETATION:** the governing constraint is R4, not fidelity. AURA needs a model whose
*equations* are available, not a model whose *predictions* are accurate.

---

## 2. Candidates evaluated

Seven options were assessed (the brief required at least five).

### C1 — AeroBenchVVPython (F-16, Nguyen/Stevens–Lewis aerodynamics)

Sources: LIT-0020 (NASA TP-1538), LIT-0021 (Heidlauf et al. 2018), LIT-0022 (Bak, Python port),
LIT-0026 (Stevens & Lewis).

| Aspect | Assessment |
|---|---|
| Documentation | Strong. Aero data traceable to a public NASA report; equations published in a standard textbook |
| Governing equations | Explicit 6-DOF; 13 states (Vt, α, β, φ, θ, ψ, P, Q, R, pn, pe, alt, pow) |
| Aero fidelity | Wind-tunnel lookup tables incl. high-α / post-stall |
| Control inputs | Throttle, elevator, aileron, rudder + a low-level LQR-style controller and autopilots |
| Envelope | Wide; explicitly includes high-angle-of-attack regimes |
| Accessibility | Open source, Python-native |
| Validation evidence | Used as an ARCH verification benchmark — i.e. others rely on its behaviour |
| Implementation difficulty | Low. Already runnable |
| Licensing | **UNVERIFIED — must be confirmed before adoption (open action A-1)** |
| Computational cost | Low (ODE integration over tables) — **must be measured (EXP-0001)** |
| Fault-diagnosis suitability | Good: clean measurement model, easy fault injection at sensor/actuator interfaces |
| Uncertainty-research suitability | Good: parameters and aero tables are perturbable in a physically-meaningful way |

### C2 — F16Model.jl / F16-Model-Matlab (ISR Lab) — LIT-0023

Same underlying aerodynamics as C1, different implementation, with trim and linearisation
utilities. Julia/MATLAB rather than Python.
**Verdict:** not the primary platform (language mismatch), but **valuable as an independent
cross-implementation check** — differences between two implementations of the "same" model are a
legitimate, honest source of model mismatch.

### C3 — JSBSim — LIT-0025

| Aspect | Assessment |
|---|---|
| Documentation | Strong; mature project |
| Governing equations | 6-DOF; but expressed through an XML configuration system |
| Aero fidelity | Varies enormously by aircraft configuration |
| Accessibility | Open source; Python wheels |
| Suitability for R4 | **Weak.** Extracting a clean equation set for structural analysis from XML-configured aero tables plus engine models is substantial work with no research payoff |
| Cost | Higher than C1 |

**Verdict:** more capable than needed, and its capability is concentrated in dimensions RQ-1 does
not use. Retained as a *possible independent test environment* for simulation-bias mitigation.

### C4 — NASA GTM / AirSTAR — LIT-0032

| Aspect | Assessment |
|---|---|
| Heritage | Excellent — purpose-built for upset and in-flight failure emulation |
| Validation | Backed by real dynamically-scaled flight test |
| Accessibility | Open, but **MATLAB/Simulink** |
| Cost | Toolbox licensing conflicts with the open-reproducibility goal |

**Verdict:** scientifically the most attractive heritage of any candidate, disqualified on
reproducibility grounds. If MATLAB access exists, this is the strongest alternative to C1.

### C5 — Small fixed-wing UAS model (Aerosonde-class, Beard & McLain lineage)

*Marked `PRIOR_KNOWLEDGE` — the textbook and its open course code must be verified (open action A-2).*

| Aspect | Assessment |
|---|---|
| Documentation | Textbook-complete: full 6-DOF with explicit coefficient-form aerodynamics |
| Suitability for R4 | **Excellent** — the aero model is closed-form, so structural analysis is straightforward |
| Envelope | **Narrow.** A small UAS operates over a limited airspeed/altitude range |
| Suitability for R2 | **Weak** — a narrow envelope weakens the physical meaning of "regime shift" |
| Match to real data | Good — closest airframe class to ALFA (LIT-0027) |

**Verdict:** a serious contender, and a better structural-analysis subject than C1. Rejected as
primary only because R2 (envelope width) is the property RQ-1 most depends on. **Retained as the
fallback if C1's structural analysis proves intractable.**

### C6 — Linearised LTI models at trim points

Cheapest, fully analysable, exact ground truth. **Disqualified on R1:** in an LTI model the
distribution shift AURA studies would be an artefact of my own parameter choices rather than a
consequence of physics. H2's structural ground truth would then be circular.
**Retained** as a *sanity-check environment* for verifying estimator and metric implementations
before running the nonlinear experiments.

### C7 — PX4 / ArduPilot SITL, X-Plane

High realism of the *software stack*, poor transparency of the *equations*. Disqualified on R4 and R5.

---

## 3. Comparison

| Criterion | C1 F-16 (Py) | C2 F16 (Jl/ML) | C3 JSBSim | C4 GTM | C5 small UAS | C6 LTI | C7 SITL |
|---|---|---|---|---|---|---|---|
| R1 nonlinear 6-DOF | ✔ | ✔ | ✔ | ✔ | ✔ | ✘ | ✔ |
| R2 wide envelope | ✔✔ | ✔✔ | ✔ | ✔ | ✘ | ✘ | ✔ |
| R3 exact ground truth | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ~ |
| R4 analysable equations | ✔ | ✔ | ~ | ~ | ✔✔ | ✔✔ | ✘ |
| R5 cheap Monte Carlo | ✔ | ✔ | ~ | ~ | ✔✔ | ✔✔ | ✘ |
| Open / no proprietary tools | ✔ | ~ | ✔ | ✘ | ✔ | ✔ | ✔ |
| Python-native | ✔ | ✘ | ✔ | ✘ | ✔ | ✔ | ~ |
| **Overall** | **Selected** | Cross-check | Reserve | Blocked | Fallback | Verification | Rejected |

---

## 4. Decision

**Primary model: C1 — AeroBenchVVPython F-16 (Nguyen/Stevens–Lewis aerodynamics).**

Justification against the brief's standard — *"sufficiently realistic to create meaningful
diagnostic difficulty, but sufficiently controlled to provide interpretable ground truth"*:

- Nonlinear aero tables and cross-axis coupling make residual structure genuinely
  flight-condition-dependent, which is the physical basis of H2. (Difficulty.)
- Full state and injected fault are known exactly, and the equation set is publishable and
  analysable. (Interpretable ground truth.)
- It is not chosen because it is an F-16. It is chosen because it is the only openly available,
  Python-native, textbook-documented nonlinear model with an envelope wide enough for the shift
  axis to mean something. **If C5 had a wider envelope it would win on R4.**

**Supporting roles:**
- **C6 (LTI)** — implementation verification of estimators and metrics before nonlinear runs.
- **C2 / C3** — independent-implementation test environments for simulation-bias mitigation (§20 of the brief).
- **C5** — fallback primary if structural analysis of C1 proves intractable.
- **ALFA (LIT-0027)** — real-flight external validity check; see `DATASET_SURVEY.md`.

---

## 5. Open actions before implementation

| ID | Action | Blocking? |
|----|--------|-----------|
| A-1 | Verify AeroBenchVVPython licence and maintenance status; record in `docs/assumptions.md` | **Yes** |
| A-2 | Verify the C5 textbook/code availability and licence | No (fallback only) |
| A-3 | **EXP-0001:** measure wall-clock runtime and output size for one 30 s run | **Yes** |
| A-4 | **EXP-0002:** derive the equation set and compute the structural isolability matrix at ≥3 flight conditions. **If isolability is identical at all conditions, H2's ground truth does not exist and the design must change.** | **Yes — highest-priority gate** |
| A-5 | Confirm the model's high-α validity boundary and set envelope limits so simulations stay inside the documented region | Yes |

---

## 6. Recorded risk

**LIMITATION.** The C1 aerodynamic data is from 1979 wind-tunnel testing of an F-16 configuration.
It is a *representative* nonlinear fighter model, not a validated model of any flying aircraft. No
result from AURA may be stated as a claim about F-16 behaviour. All claims are about *a nonlinear
high-performance aircraft model*. This is stated in `docs/assumptions.md` as A-SIM-01 and must
appear in any publication.
