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
| A-SIM-01 | The AeroBenchVVPython F-16 model is a *representative nonlinear high-performance aircraft*, **not** a validated model of a real F-16 | `OPEN` (accepted, not testable) | No claim about real F-16 behaviour is licensed. All findings scoped to "a nonlinear 6-DOF model" | Must appear in every report |
| A-SIM-02 | Rigid-body 6-DOF dynamics are sufficient; aeroelastic effects are irrelevant to RQ-1 | `OPEN` | Residual structure would differ at high dynamic pressure | Accepted; stated as a limitation |
| A-SIM-03 | The aero lookup tables are valid over the flight envelope used | `TO-VERIFY` | Simulation could operate in an unvalidated region, making "shift" an artefact of extrapolation rather than physics | A-5: bound the envelope to the documented region |
| A-SIM-04 | Atmospheric disturbance can be represented by a simple gust/turbulence model without changing the conclusions | `OPEN` | Conclusions may not transfer to realistic turbulence | Sensitivity run in EXP-0009 |
| A-SIM-05 | Actuator dynamics can be represented by first-order lags with rate/position limits | `OPEN` | F6 (effectiveness loss) signature could differ | Accepted |
| A-SIM-06 | Fixed-step integration at the chosen step size is numerically adequate | `TO-VERIFY` | Numerical error could masquerade as a residual | EXP-0001: step-size convergence check |

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
| A-FLT-03 | Elevator effectiveness loss (F6) and pitch-rate scale error (F2 on $q$) form a *flight-condition-dependent* ambiguity pair | `TO-VERIFY` — **critical** | If not, H2 has no mode-dependent ground truth | **EXP-0002 is a hard gate** |
| A-FLT-04 | Faults are safety-relevant in proportion to magnitude, as encoded in the cost model | `OPEN` | Cost model would misrank outcomes | Sensitivity over $\rho$ |

## Uncertainty and method

| ID | Assumption | Status | Consequence if wrong | Action |
|---|---|---|---|---|
| A-UNC-01 | Aleatoric noise levels are known | `OPEN` (deliberate) | See A-SEN-04 | Intentional |
| A-UNC-02 | Ensemble disagreement is a usable proxy for epistemic uncertainty | `OPEN` | $N$ would be poorly grounded | LIT-0005/0009 support; H2 tests it empirically |
| A-UNC-03 | Structural isolability is a valid *lower bound* reference for evidential ambiguity | `OPEN` | H2's ground truth would be invalid | Structural analysis gives necessary-not-sufficient conditions — so it bounds, not determines, ambiguity. Stated explicitly |
| A-UNC-04 | Calibration on the validation split transfers to in-distribution test data | `OPEN` | ID calibration numbers would be optimistic | Standard practice; ID/OOD reported separately |

## Data and infrastructure

| ID | Assumption | Status | Consequence if wrong | Action |
|---|---|---|---|---|
| A-INF-01 | `float32` storage is sufficient; precision loss is far below sensor noise | `OPEN` | Numerical artefacts in residuals | Verified in EXP-0001 by comparing float64 and float32 residuals |
| A-INF-02 | ~2 s wall-clock per 30 s simulated run | `TO-VERIFY` | Full experiment infeasible; must re-scope | **EXP-0001** |
| A-INF-03 | ~3× compression on flight-dynamics time series | `TO-VERIFY` | Storage forecast wrong by up to ~3× | **EXP-0001** |
| A-INF-04 | Total project storage stays under ~100 GB, so Git LFS / cloud storage are unnecessary | `TO-VERIFY` | Infrastructure change needed mid-project | Re-forecast after EXP-0005 |
| A-INF-05 | Simulation is deterministic given a fixed seed and environment | `TO-VERIFY` | Reproducibility claims void | **EXP-0001** bitwise check |

## Licensing and access

| ID | Assumption | Status | Action |
|---|---|---|---|
| A-LIC-01 | AeroBenchVVPython is licensed for research use and redistribution of derived data | `TO-VERIFY` — **blocking** | A-1 |
| A-LIC-02 | Fault Diagnosis Toolbox (LIT-0002) is licensed for research use | `TO-VERIFY` | Check before adoption |
| A-LIC-03 | ALFA is licensed for research use with attribution | `TO-VERIFY` | A-6 |

## Literature

| ID | Assumption | Status | Action |
|---|---|---|---|
| A-LIT-01 | The gap identified in `GAP_MATRIX.md` is real | `TO-VERIFY` — **blocking any novelty claim** | Systematic search (TV-N1) |
| A-LIT-02 | Metadata marked `SEARCH_METADATA` / `TITLE_URL_ONLY` in the literature index is approximately correct | `OPEN` | Verify before citing any such entry |
| A-LIT-03 | LIT-0014 and LIT-0026 (marked `PRIOR_KNOWLEDGE`) exist as described | `TO-VERIFY` | Confirm against a database |
