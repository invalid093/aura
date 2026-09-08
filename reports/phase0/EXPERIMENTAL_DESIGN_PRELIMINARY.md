# Preliminary Experimental Design — Phase 0

**Date:** 2026-09-08
**Status:** PRELIMINARY. Gated on EXP-0001 (runtime) and EXP-0002 (structural isolability).
**Tests:** H1–H5 in `docs/hypotheses.md`.

---

## 1. Sensor suite

The brief warns that more sensors do not produce better research. The binding constraint here is
the opposite of the usual one: **the sensor suite must be small enough that some fault pairs are
genuinely indistinguishable**, because H2 requires a non-trivial ambiguity structure. A fully
redundant suite would make every fault isolable and destroy the experiment.

### Proposed minimum suite

| Ch | Measurement | Symbol | Rate | Justification |
|----|-------------|--------|------|---------------|
| 1–3 | Body angular rates | $p, q, r$ | 100 Hz | Directly observable; primary residual source for actuator faults |
| 4–6 | Body specific forces | $a_x, a_y, a_z$ | 100 Hz | Couples to aerodynamic forces; shares information with air data → creates ambiguity |
| 7 | True airspeed | $V_t$ | 50 Hz | Air data; the classic fault-prone channel (LIT-0034) |
| 8 | Angle of attack | $\alpha$ | 50 Hz | Air data; vane faults are physically documented |
| 9 | Sideslip | $\beta$ | 50 Hz | Air data; needed for lateral fault separation |
| 10 | Barometric altitude | $h$ | 20 Hz | Slow channel; independent of air data pressure path only partially → deliberate coupling |
| 11–13 | Attitude | $\phi, \theta, \psi$ | 100 Hz | Available from an inertial solution; needed for kinematic redundancy relations |

**Deliberately excluded, with reasons:**

| Excluded | Reason |
|---|---|
| GPS position/velocity | Would supply near-complete redundancy for air-data faults, collapsing the ambiguity structure that H2 depends on. **Excluding it is a design decision, not an oversight** — it is recorded as A-SEN-01 in `docs/assumptions.md` and is the single most questionable choice in the design |
| Magnetometer | Adds heading redundancy only; no bearing on RQ-1 |
| Engine/system measurements | Engine faults are out of scope |
| Redundant (triplex) sensor sets | Hardware redundancy makes sensor-fault isolation a voting problem, not an inference problem |

**Sensitivity analysis (required, not optional):** rerun the primary comparison with GPS *included*.
If AURA's advantage disappears when redundancy is added, the finding is "the decomposition matters
only in under-determined sensor suites" — which is a legitimate, more precisely scoped result. This
sensitivity run is part of the design, not a response to a bad outcome.

**Gate:** the final suite is confirmed by EXP-0002. If the structural isolability matrix at the
chosen suite is fully diagonal (everything isolable) or fully dense (nothing isolable), the suite
must be adjusted **before** any data generation.

---

## 2. Fault taxonomy

Kept deliberately small. Each entry must earn its place by contributing either to the ambiguity
structure or to the shift axis.

### Sensor faults (primary)

| ID | Type | Model | Class |
|----|------|-------|-------|
| F1 | Constant bias | $y = y_{\text{true}} + b$ | Abrupt |
| F2 | Scale-factor error | $y = k \, y_{\text{true}}$ | Abrupt |
| F3 | Drift | $y = y_{\text{true}} + \dot{b}(t - t_0)$ | Gradual |
| F4 | Stuck / frozen | $y = y(t_0)$ | Abrupt |
| F5 | Increased noise | $y = y_{\text{true}} + \mathcal{N}(0, \kappa\sigma^2)$ | Gradual |

Applied to a **restricted channel set** — $\{q, a_z, V_t, \alpha\}$ — chosen because EXP-0002 must
confirm these produce a non-trivial ambiguity structure in the pitch axis.

### Actuator fault (one only)

| ID | Type | Model | Purpose |
|----|------|-------|---------|
| F6 | Elevator effectiveness loss | $\delta_{e,\text{eff}} = \lambda \delta_e$, $\lambda \in (0,1)$ | **Exists specifically to create a physically-motivated ambiguity pair with F2 on $q$.** A partial loss of elevator effectiveness and a pitch-rate gyro scale error can produce similar residual signatures in some flight conditions and not others — which is exactly the mode-dependent ambiguity H2 requires |

### Nominal

| ID | Description |
|----|-------------|
| F0 | No fault |

**Total: 7 fault modes** (F0 plus F1–F6, with F1–F5 instantiated on a small channel set).

**Explicitly NOT modelled:** intermittent faults, communication interruption, data corruption,
simultaneous multi-faults beyond a single designated pair, icing, structural damage.
Each was considered and cut because none is needed to answer RQ-1. Simultaneous faults would
enlarge the hypothesis space combinatorially and confound H2's ground truth.

**Faults are injected at the measurement/actuation interface, not into the plant dynamics** — with
the exception of F6, which necessarily acts on the plant. This distinction is recorded because it
determines what the structural model must contain.

---

## 3. Uncertainty framework

Binding definitions. "Confidence" is **not** used as a synonym for any of these.

| Symbol | Name | Meaning in AURA | Source | Used for |
|---|---|---|---|---|
| $\Sigma_x$ | State-estimation uncertainty | Covariance of the estimated aircraft state | Estimator (EKF/UKF) | Input to residual normalisation |
| $A$ | **Evidential ambiguity** | Spread of posterior mass across fault hypotheses that explain the evidence equally well | Residual likelihood over the hypothesis set | Abstain-with-set decision |
| $N$ | **Competence loss** | Distance of the current operating point from development conditions | Distance-aware representation over flight-condition features | Escalate decision |
| — | Aleatoric | Irreducible sensor/process noise | Known noise model | Kept fixed; a control variable |
| — | Epistemic | Reducible-by-data uncertainty | Ensemble disagreement | Realised concretely as $N$ |

**How uncertainty is generated, propagated, calibrated, evaluated, and used:**

1. **Generated** — $A$ from the normalised residual likelihood across hypotheses; $N$ from
   ensemble disagreement plus a distance-aware term over flight-condition features (LIT-0050).
2. **Propagated** — state covariance normalises residuals; residual likelihoods form the fault
   posterior; the posterior's entropy/margin gives $A$.
3. **Calibrated** — on the **validation** split only. Never on test.
4. **Evaluated** — primarily by **proper scoring rules** (NLL, Brier) and **expected decision
   cost**. ECE is reported as a secondary, clearly-labelled diagnostic only, because it is not a
   proper scoring rule and can be trivially satisfied by an uninformative model (LIT-0010, LIT-0011).
5. **Used** — through the decision policy in §6.

**ASSUMPTION (A-UNC-01):** aleatoric noise levels are known to the estimator. This is generous to
the model-based baselines and is deliberate — AURA must not win by being handed a noise advantage.

---

## 4. Distribution-shift / OOD framework

"Unseen" must be defined operationally or the OOD claim is unfalsifiable.

| Axis | Development | Test | Shift magnitude $s$ |
|---|---|---|---|
| **S1 Flight regime** | Trim conditions inside a defined box in $(V_t, h, n_z)$ | Conditions outside the box | Normalised distance from the box boundary |
| **S2 Parameter** | Nominal mass, inertia, CG | Perturbed within a stated range | Relative perturbation magnitude |
| **S3 Sensor** | Development noise/bias characteristics | Different noise level and spectrum | Ratio to development $\sigma$ |
| **S4 Model structure** | Aero **lookup tables** | Aero **global polynomial** (LIT-0024), or an independent implementation (C2/C3) | Categorical (structural) |
| **S5 Fault** | Fault magnitudes in a development range | Magnitudes outside it; and F6 held out entirely from one training condition | Magnitude ratio |
| **S6 Combined** | — | S1 + S5 simultaneously | Joint |

**S6 is the scientifically important one.** It is the setting in which LIT-0004's stated limitation
lives, and it is where H3 is tested. S1–S5 exist mainly to make S6 interpretable.

**S4 is the strongest OOD axis** because it introduces *unmodelled structure* rather than
mis-specified parameters. Parameter randomisation alone is a weak OOD test — a criticism AURA must
apply to itself, not only to others.

---

## 5. Variables

### Independent
| Variable | Levels |
|---|---|
| Fault mode | F0–F6 |
| Fault magnitude | 5 levels spanning below-detectable to obvious |
| Fault onset time | Uniform random within the run |
| Flight condition | Grid over $(V_t, h)$ + commanded manoeuvre |
| Shift axis / magnitude | S1–S6, ≥4 magnitudes each |
| Diagnostic method | B0–B5 + AURA (§7) |
| Random seed | ≥30 independent seeds per cell |

### Dependent (primary in **bold**)
- **Expected decision cost $\mathbb{E}[C]$ at matched coverage** (H1)
- **Act/abstain/escalate agreement rate with baselines** (H1 falsification, H5)
- **$\rho(A,N)$; association of each with its ground truth** (H2)
- **MDR vs shift magnitude, gated vs ungated** (H3)
- **NLL / Brier of the fault posterior** (H4)
- Detection latency; false-alarm rate; missed-detection rate; isolation accuracy *conditioned on
  structural isolability*; ambiguity-set coverage and size; AURC (risk–coverage)

### Controlled (fixed across all runs)
Integration scheme and step size; sensor sample rates; aleatoric noise model; controller gains and
autopilot configuration; run duration; training budget per method; calibration split size;
evaluation code path (one implementation, shared by all methods).

---

## 6. Decision policy and cost model

Three actions: **CONTINUE**, **DEGRADE**, **ESCALATE**.

The cost model is the weakest link in any decision-quality claim, because a single arbitrary cost
matrix can manufacture the desired result. AURA therefore **does not fix one cost matrix**. It uses
a parametric family and reports results as a function of the parameter.

| Outcome | Cost |
|---|---|
| CONTINUE, nominal | $0$ |
| DEGRADE, nominal (unnecessary) | $1$ |
| ESCALATE, nominal (false escalation) | $c_e$ |
| CONTINUE, fault present and safety-relevant | $c_u$ |
| DEGRADE, fault present, correct isolation | $2$ |
| DEGRADE, fault present, wrong isolation | $5$ |
| ESCALATE, fault present | $c_e$ |

The governing quantity is $\rho = c_u / c_e$ — how much worse an unsafe continuation is than a
false escalation. **All H1 results are reported as curves over $\rho \in \{5, 10, 30, 100\}$.**

A method that wins only at one value of $\rho$ has not won. This is stated now, before results
exist, so it cannot be relaxed later.

**Coverage matching:** all comparisons are made at equal autonomy coverage (equal fraction of runs
where the system acts without escalating). Comparing methods at different coverage is meaningless
(LIT-0012).

---

## 7. Baselines

AURA must beat credible baselines, tuned with equal effort, implemented against the same interface,
and scored by the same code.

| ID | Baseline | Why included |
|----|----------|--------------|
| B0 | Fixed-threshold residual detector ($\chi^2$ on normalised innovations) | The classical method the field actually uses |
| B1 | **MMAE / Kalman-filter bank** posterior (LIT-0043, LIT-0044) | The strongest *principled probabilistic* model-based diagnoser. Tests H4 |
| B2 | Deterministic NN classifier + softmax-confidence gate | Represents the dominant recent aircraft-FDI literature (LIT-0039–0042) |
| B3 | Deep ensemble + predictive-entropy gate | Current best-practice UQ; strongest under shift per LIT-0005, LIT-0009 |
| B4 | **Ensemble PNN + epistemic OOD gate** (LIT-0004 style) | **The closest prior work.** If AURA cannot beat B4, AURA has no contribution |
| B5 | Conformal prediction set over B3 | Distribution-free set-valued comparator for H5 |
| — | Chow's rule with an oracle posterior (LIT-0014) | Reference upper bound on abstention, not a competitor |
| **AURA** | Two-component $(A,N)$ policy | The method under test |

**B4 is the decisive baseline.** Any H1 result reported without B4 is not a result.

---

## 8. Development / validation / test discipline

```
DEVELOPMENT  →  VALIDATION  →  FROZEN TEST  →  FINAL EVALUATION
```

- Splits are by **scenario**, never by time window within a run. Windows from one run must never
  appear on both sides of a split (TV-L2 — the most likely source of data leakage here).
- The **frozen test set is generated once, hashed, and committed as a manifest before any method is
  trained.** Its checksum is recorded in `data/manifests/`.
- Test-set evaluation is performed **once per method version.** Every evaluation is logged in the
  experiment registry with a timestamp, whether or not the result was liked.
- OOD conditions (S1–S6 test levels) appear **only** in the frozen test set.
- Exploratory and confirmatory experiments are tagged distinctly in the registry.

---

## 9. Staged execution plan

Per §28 of the brief — each stage gates the next.

| Stage | Experiment | Purpose | Gate to proceed |
|---|---|---|---|
| 0 | EXP-0001 | One run: measure runtime, output size, verify determinism under fixed seed | Runtime and size within forecast; bitwise reproducibility |
| 1 | **EXP-0002** | Structural model + isolability matrix at ≥3 flight conditions | **Isolability must be non-trivial AND flight-condition-dependent. If not, H2 fails at design stage and the design changes.** |
| 2 | EXP-0003 | Fault injection verification: confirm each fault produces its expected residual signature | All 7 modes distinguishable from nominal at max magnitude |
| 3 | EXP-0004 | Metric implementation verification on the LTI model (C6) with analytically known answers | Metrics reproduce known values |
| 4 | EXP-0005 | Pilot: ~200 runs, B0/B1/AURA only | Diagnosis is neither trivial (>99%) nor impossible (<20%) |
| 5 | EXP-0006 | Medium: ~5,000 runs, all baselines, development + validation | Stable rankings across seeds |
| 6 | EXP-0007 | Full: frozen test set, all methods, all shift axes | — |
| 7 | EXP-0008 | ALFA external validity check (detection sub-problem only) | — |
| 8 | EXP-0009 | Sensitivity: GPS included; cost-model sweep; independent-implementation test | — |

**No learning code is written before Stage 1 passes.** EXP-0002 can invalidate the design, and it
costs almost nothing to run.

---

## 10. Storage and runtime forecast (CALCULATION)

Stated assumptions, so the arithmetic can be checked and corrected after EXP-0001.

**Per run:**
- Duration 30 s at 100 Hz → 3,000 samples
- Channels: 13 states + 4 controls + 13 measurements + ~13 residuals + ~5 diagnostic outputs ≈ 48
- Stored as `float32` (8 → 4 bytes; justified: sensor precision is far below float32 resolution)

$$3000 \times 48 \times 4 = 576\ \text{kB/run uncompressed}$$

Flight-dynamics signals are smooth and highly compressible; assuming a conservative **3×** ratio
with zstd-compressed columnar storage:

$$\approx 190\ \text{kB/run stored}$$

| Stage | Runs | Raw stored | With derived artefacts (+50%) |
|---|---|---|---|
| Pilot (EXP-0005) | 200 | 38 MB | 57 MB |
| Medium (EXP-0006) | 5,000 | 0.95 GB | 1.4 GB |
| Full dev+val (EXP-0007) | 50,000 | 9.5 GB | 14 GB |
| Frozen test | 10,000 | 1.9 GB | 2.9 GB |
| **Project total (incl. repeats, ~1.5×)** | — | — | **≈ 28 GB** |

**Runtime — ASSUMPTION requiring measurement in EXP-0001:** assume 2 s wall-clock per 30 s run,
single core.

$$50{,}000 \times 2\ \text{s} \approx 28\ \text{core-hours} \approx 3.5\ \text{h on 8 cores}$$

**Conclusions (decisions, not observations):**
- ~28 GB is a **local-disk problem**, not a cloud problem.
- **Git LFS is NOT adopted.** Bulk data stays out of Git; manifests with checksums go in Git.
  Revisit only if projected storage exceeds ~100 GB.
- No cloud object storage, no database, no distributed compute in Phase 1.
- Parallelisation via simple process-level parallelism over seeds. No vectorisation work until
  EXP-0001 shows it is needed.

**If EXP-0001 shows runtime >10 s/run, the full experiment must be re-scoped** (fewer seeds or
shorter runs), not run anyway.

---

## 11. Statistical treatment

- All stochastic results reported as distributions over ≥30 seeds, never single runs.
- Paired comparisons at the scenario level; bias-corrected bootstrap CIs (≥1000 resamples).
- **Equivalence testing, not just difference testing.** H1's falsification condition is an
  equivalence claim, which requires a TOST-style test with a pre-declared margin — following
  LIT-0012's methodology. The margin is declared here: **δ = 2% of baseline expected cost.**
- Multiple comparisons across 7 methods × 6 shift axes are corrected (Holm–Bonferroni) for any
  confirmatory claim.
