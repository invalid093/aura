# AURA — Assumptions Register

**Date:** 2026-09-08
**Rule:** No assumption may live only inside code. If code depends on one, it cites the ID here.
An assumption that is later tested moves to `VALIDATED` or `REFUTED` — it is never silently deleted.

| Status | Meaning |
|---|---|
| `OPEN` | Assumed, untested |
| `TO-VERIFY` | Assumed, with a specific action scheduled |
| `VALIDATED` | Tested and held |
| `REFUTED` | Tested and failed — consequences must be traced |

---

## Simulation and model

| ID | Assumption | Status | Consequence if wrong | Action |
|---|---|---|---|---|
| A-SIM-01 | The aircraft model is a *representative nonlinear fixed-wing aircraft*, **not** a validated model of any real airframe. As of 2026-09-08 the model is **GFW-1**, self-implemented from published flight-dynamics equations with parameters stated in configuration (`ADR-0007`) | `OPEN` (accepted, not testable) | No claim about any real aircraft is licensed. All findings scoped to "a nonlinear 6-DOF fixed-wing model" | Must appear in every report |
| A-SIM-07 | GFW-1's parameter set is physically self-consistent and representative of a small fixed-wing UAS | `OPEN` — **new threat TV-D10**: the model is now self-implemented as well as single | EXP-0002's conclusion could be specific to a parameter set chosen by the same person who ran the experiment | Reproduce on an independently sourced airframe model before the result becomes load-bearing |
| A-SIM-02 | Rigid-body 6-DOF dynamics are sufficient; aeroelastic effects are irrelevant to RQ-1 | `OPEN` | Residual structure would differ at high dynamic pressure | Accepted; stated as a limitation |
| A-SIM-03 | **Superseded 2026-09-08.** GFW-1 uses closed-form coefficient aerodynamics with a sigmoid stall blend, not lookup tables, so there is no tabulated validity region. The equivalent risk — operating where the model is not meaningful — is now controlled by the **validity gate** (max α < 12°, bounded θ, V, h) | **`VALIDATED` as a mechanism (EXP-0002)** — the gate caught FC-4 | Without it, results come from a region where the model misbehaves | Gate runs on every condition in `run_exp0002.py` |
| A-SIM-04 | Atmospheric disturbance can be represented by a simple gust/turbulence model without changing the conclusions | `OPEN` | Conclusions may not transfer to realistic turbulence | Sensitivity run in EXP-0009 |
| A-SIM-05 | **Corrected to match the implementation 2026-09-08.** Actuators are **algebraic (no lag)**, with position limits only — not first-order lags as originally written. `aircraft/gfw1.py` cites this ID | `OPEN` | F6's signature and the high-frequency content of every fault response could differ with real actuator dynamics. Uniform across all faults, so pairwise *comparisons* are less affected than absolute responses | Add lag and re-check in a later experiment |
| A-SIM-06 | Fixed-step RK4 at the chosen step is numerically adequate | **`VALIDATED` (EXP-0002 S-A)** — pair counts identical and rank correlation ≥ 0.9992 across dt ∈ {0.005, 0.002, 0.001} s | Numerical error could masquerade as a fault signature | Done |

## Sensors

| ID | Assumption | Status | Consequence if wrong | Action |
|---|---|---|---|---|
| A-SEN-01 | **Excluding GPS is legitimate** — it reflects a plausible degraded/denied-navigation case and is necessary to preserve a non-trivial ambiguity structure | `OPEN` — **the most questionable choice in the design** | AURA's advantage might exist only in artificially under-determined sensor suites | Mandatory GPS-included sensitivity run (EXP-0009). Result reported either way |
| A-SEN-02 | Sensor noise is zero-mean Gaussian and white at the stated levels | `OPEN` | Real sensor noise is coloured; calibration results could be optimistic | Stated as a limitation |
| A-SEN-03 | Sensor sample rates are fixed and synchronous, with no dropouts outside injected faults | `OPEN` | Real systems have jitter and asynchrony | Out of scope |
| A-SEN-04 | The estimator knows the true aleatoric noise levels (A-UNC-01) | `OPEN` (deliberate) | Generous to model-based baselines — chosen so AURA cannot win by a noise-knowledge advantage | Intentional |

## Faults

| ID | Assumption | Status | Consequence if wrong | Action |
|---|---|---|---|---|
| A-FLT-01 | The five sensor fault models (bias, scale, drift, stuck, noise) adequately represent real sensor failure modes | `OPEN` — **not verifiable within scope** | External validity of the whole study is limited | Fault models drawn from LIT-0034; stated as a core limitation |
| A-FLT-02 | Single faults only (except one designated ambiguity pair) | `OPEN` (scope decision) | Real systems experience cascades | Explicitly out of scope |
| A-FLT-03 | Elevator effectiveness loss (F6) and pitch-rate scale error (F2 on $q$) form a *flight-condition-dependent* ambiguity pair | **`REFUTED` in its specifics (EXP-0002, 2026-09-08)** — F6 and F2_q are **distinguishable at every valid condition**. The general claim survives: a flight-condition-dependent ambiguity pair does exist, but it is bias-vs-scale on airspeed (`F1_Vt`/`F2_Vt`), ambiguous only at 45 m/s | H2 retains a mode-dependent reference, but not the one predicted | Superseded by the EXP-0002 result; see `reports/technical/EXP-0002_STRUCTURAL_ISOLABILITY.md` §13 |
| A-FLT-05 | A bias fault and a scale fault on a *regulated* channel coincide at $V^{*}=b/(k-1)$ | **`VALIDATED` (EXP-0002)** — predicted in closed form before simulation, confirmed at Pearson r = 0.979 across four conditions | Gives the ambiguity component a *derivable* reference, not only a measured one | — |
| A-FLT-04 | Faults are safety-relevant in proportion to magnitude, as encoded in the cost model | `OPEN` | Cost model would misrank outcomes | Sensitivity over $\rho$ |

## Uncertainty and method

| ID | Assumption | Status | Consequence if wrong | Action |
|---|---|---|---|---|
| A-UNC-01 | Aleatoric noise levels are known | `OPEN` (deliberate) | See A-SEN-04 | Intentional |
| A-UNC-02 | Ensemble disagreement is a usable proxy for epistemic uncertainty | `OPEN` | $N$ would be poorly grounded | LIT-0005/0009 support; H2 tests it empirically |
| A-UNC-03 | **Amended 2026-09-08 (`ADR-0008`).** H2's reference is **response-based distinguishability at the current flight condition**, not structural isolability. Structural isolability remains a valid *outer bound* (necessary, not sufficient) but is flight-condition-invariant by construction and so cannot serve as the condition-dependent ground truth on its own | `OPEN` | H2's ground truth would be invalid | Response-based distinguishability measured in EXP-0002; structural analysis deferred as an outer-bound cross-check |
| A-UNC-04 | Calibration on the validation split transfers to in-distribution test data | `OPEN` | ID calibration numbers would be optimistic | Standard practice; ID/OOD reported separately |

## Data and infrastructure

| ID | Assumption | Status | Consequence if wrong | Action |
|---|---|---|---|---|
| A-INF-01 | `float32` storage is sufficient | **`NOT YET APPLICABLE`** — EXP-0002 computes and stores in float64 throughout. The float32 decision belongs to the large Monte Carlo runs, which have not been built | Numerical artefacts in residuals | Test when bulk generation begins |
| A-INF-02 | ~2 s wall-clock per 30 s simulated run | **`VALIDATED` (EXP-0002)** — measured 1.37 s per 20 s run at dt = 0.002 s, i.e. ≈ 2.1 s per 30 s equivalent | Full experiment infeasible; must re-scope | Done |
| A-INF-03 | ~3× compression on flight-dynamics time series | **`VALIDATED` (EXP-0002)** — 90 runs of 485 KiB float64 uncompressed stored as 17.7 MiB, ≈ 2.5× compression at float64. The float32 forecast in Phase 0 remains untested | Storage forecast wrong | Re-check at float32 |
| A-INF-04 | Total project storage stays under ~100 GB, so Git LFS / cloud storage are unnecessary | `TO-VERIFY` | Infrastructure change needed mid-project | Re-forecast after EXP-0005 |
| A-INF-05 | Simulation is deterministic given a fixed configuration and environment | **`VALIDATED` (EXP-0002 S-E)** — all 90 runs bitwise identical on replay. The pipeline contains no RNG at all | Reproducibility claims void | Done |

## Licensing and access

| ID | Assumption | Status | Action |
|---|---|---|---|
| A-LIC-01 | AeroBenchVVPython is licensed for research use and redistribution of derived data | **`REFUTED` in part (2026-09-08)** — it is **GPL-3.0**. Usable, but vendoring or importing it into distributed AURA code would bind AURA to GPL-3.0 | Resolved A-1. Model substituted for EXP-0002; **researcher decision required before Phase 1b** — `ADR-0007` |
| A-LIC-02 | Fault Diagnosis Toolbox (LIT-0002) is licensed for research use | `TO-VERIFY` | Check before adoption |
| A-LIC-03 | ALFA is licensed for research use with attribution | `TO-VERIFY` | A-6 |

## Literature

| ID | Assumption | Status | Action |
|---|---|---|---|
| A-LIT-01 | The gap identified in `GAP_MATRIX.md` is real | `TO-VERIFY` — **blocking any novelty claim** | Systematic search (TV-N1) |
| A-LIT-02 | Metadata marked `SEARCH_METADATA` / `TITLE_URL_ONLY` in the literature index is approximately correct | `OPEN` | Verify before citing any such entry |
| A-LIT-03 | LIT-0014 and LIT-0026 (marked `PRIOR_KNOWLEDGE`) exist as described | `TO-VERIFY` | Confirm against a database |
