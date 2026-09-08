# AURA — Scope

**Date:** 2026-09-08

The most useful section of this document is §2. Deciding what *not* to build is the main way a
solo computational research project stays finishable.

---

## 1. In scope

| Area | What is included |
|---|---|
| Aircraft model | One nonlinear 6-DOF model (AeroBenchVVPython F-16), used as a *representative* high-performance aircraft |
| Sensors | A fixed 13-channel suite: rate gyros, accelerometers, air data ($V_t, \alpha, \beta$), baro altitude, attitude |
| Faults | 7 modes: nominal, sensor bias, scale error, drift, stuck, increased noise, elevator effectiveness loss |
| Estimation | One nonlinear state estimator (EKF or UKF) shared by all methods |
| Diagnosis | Residual generation, fault posterior, ambiguity set |
| Uncertainty | Two components: evidential ambiguity $A$, competence loss $N$ |
| Decision | Three actions: continue / degrade / escalate, under a parametric cost model |
| Shift | Six axes S1–S6, with S6 (combined) as the primary |
| Baselines | B0–B5 including the closest prior work (B4) |
| Data | Simulation-generated primary data + ALFA as an external validity check |
| Infrastructure | Local, file-based, checksummed, reproducible; no cloud services |

---

## 2. Explicitly out of scope

Each entry states *why*, because "we didn't get to it" and "it isn't needed" are different claims.

### Not built because RQ-1 does not need it

| Excluded | Reason |
|---|---|
| **Fault-tolerant control / reconfiguration** | A separate discipline. AURA decides *what to do at the autonomy level*, not how to re-allocate control. Adding it would double scope and confound the decision metric with controller quality |
| **Prognostics / remaining useful life** | Different question, different literature, different data requirements |
| **Trajectory planning / mission replanning** | Downstream of the decision AURA studies |
| **Human-subject studies of operator response** | Would require ethics approval and participants; the cost model treats escalation as a cost, not a human process |
| **Multi-aircraft / fleet health management** | Orthogonal to RQ-1 |
| **Real-time / embedded implementation** | Computational cost is not a variable in RQ-1. Claiming onboard feasibility would need hardware we do not have |
| **Certification argumentation** | AURA relates to the RTA architecture (LIT-0052) conceptually. It does not produce a certification case |
| **Cyber-security / adversarial attacks on sensors** | A different threat model |
| **Icing, structural damage, engine faults** | Would enlarge the fault space without sharpening RQ-1 |
| **Intermittent and cascading faults** | Combinatorially enlarge the hypothesis space and confound H2's ground truth |
| **Higher-fidelity aerodynamics (CFD, aeroelastics)** | Fidelity is a cost. RQ-1 needs *analysable* equations, not accurate ones |
| **Reinforcement learning for the decision policy** | The decision space has 3 actions and an explicit cost model. A learned policy would add variance and confound the uncertainty question with policy-learning quality |
| **Large foundation / sequence models** | No evidence they would change the answer to RQ-1; large compute cost; poor interpretability of the resulting uncertainty |
| **A dashboard or web UI** | Provides no scientific information |

### Not built *yet* (deferred, with a condition)

| Deferred | Condition for revisiting |
|---|---|
| Second airframe (small UAS, C5) | Only after the primary result exists on C1, and only if generality is the limiting criticism |
| Conformal methods beyond B5 | Only if H5 shows the coverage question is central |
| Online adaptation (LIT-0070 style) | Only if H3 shows novelty gating is net-harmful — then adaptation becomes the natural alternative |
| Git LFS / cloud storage | Only if projected storage exceeds ~100 GB |
| Distributed compute | Only if EXP-0001 shows runtime makes the full experiment infeasible on one machine |

---

## 3. Scope boundaries that protect research integrity

- **Public, unclassified sources only.** No proprietary aircraft data, no operational or threat
  context, no export-controlled material. The F-16 model is a 1979 public NASA wind-tunnel dataset.
- **No claims about any real aircraft.** See A-SIM-01.
- **Defence relevance is not a research contribution** and does not enter the ranking of research
  directions (TV-F1).

---

## 4. What success looks like

Phase 1 succeeds if it produces a **defensible answer** to RQ-1 — in either direction — with:

- a reproducible open benchmark,
- an honest statement of what the simulation cannot establish,
- H3's confounding curve measured, and
- every falsified hypothesis reported as prominently as any supported one.

Phase 1 **fails** if it produces an impressive architecture with no falsifiable claim attached.
