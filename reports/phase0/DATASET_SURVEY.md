# Dataset Survey — Phase 0

**Date:** 2026-09-08
**Question:** What public data exists, what can it actually support, and what must AURA generate?

---

## 1. Why this survey matters more than usual

AURA's primary experiment is simulation-based. The brief (§20) is explicit that simulation bakes
assumptions into results. The role of public data here is therefore **not** to be the main
experimental substrate — it is to provide an **external validity check** that the simulation-based
conclusion is not an artefact of the simulator.

That reframes the selection criterion. The question is not "which dataset is biggest?" but
**"which dataset can falsify a simulation-derived conclusion?"**

---

## 2. Candidate datasets

### D1 — ALFA (LIT-0027)

| Property | Value |
|---|---|
| Content | 47 autonomous fixed-wing flights: 23 sudden full engine failures, 24 across 7 control-surface fault types |
| Duration | ~66 min nominal, ~13 min post-fault (processed); more raw |
| Ground truth | **Fault time and type labelled** |
| Platform | Fixed-wing UAV |
| Access | Open (CMU AirLab / GitHub) |
| Licence | **Must be verified (open action A-6)** |

**What it can support:** a genuine reality check on detection latency and false-alarm behaviour for
*actuator/engine* faults on a real airframe, at real noise levels, with real wind.

**What it cannot support:**
- **No sensor faults.** AURA's primary fault taxonomy is sensor-centric; ALFA is actuator-centric.
- **No controlled shift axis.** Flight conditions vary but not in a designed, measurable way.
- **Small post-fault sample.** 13 minutes of post-fault flight cannot support calibration
  estimation, which needs many independent fault events.

**Verdict: adopt as the external validity check, with an honest statement of what it cannot test.**
It answers "does the detector work on real data at all?" — not "is the uncertainty calibrated?"

---

### D2 — NASA DASHlink sample flight data / curated 4-class anomaly set (LIT-0028)

~99,000 flights, 160 s final-approach windows, 3 anomaly classes + nominal.

**Fatal limitation for AURA:** the labels are **operational anomalies** (unusual flight-crew or
trajectory behaviour), not component faults. There is no fault ground truth, so isolation
performance and ambiguity structure are undefined.
**Verdict: not usable for RQ-1.** Potentially relevant only to a pure anomaly-detection variant.
Access terms must be checked before any use.

---

### D3 — NGAFID maintenance dataset (LIT-0029)

28,000+ flights, 23 channels at 1 Hz, 36 unscheduled maintenance categories, Cessna 172 fleet.

**Limitations:** labels are *maintenance events*, so fault onset time is unknown and label noise is
high; 1 Hz is too slow for flight-dynamics residual generation; general-aviation piston aircraft.
**Verdict: not usable for RQ-1.** Excellent for a degradation/prognostics project, which AURA is not.

---

### D4 — BASiC — ArduCopter sensor failures (LIT-0030)

The only surveyed dataset that is genuinely **sensor-fault** focused.
**Limitation:** multirotor, and simulation-dominant — so it does not provide the "real data"
property that motivates using an external dataset at all.
**Verdict: reference for fault-model realism (what sensor faults look like in logs); not an
evaluation set.**

---

### D5 — UAV-SEAD (LIT-0031)

State-estimation anomaly dataset for UAVs — conceptually the closest to AURA's framing.
**Status: `TITLE_URL_ONLY`. Unverified.**
**Verdict: must be checked early in Phase 1 (open action A-7).** If it contains labelled
state-estimation anomalies with flight-condition metadata, it could materially strengthen AURA's
external validity — or, if it already includes uncertainty benchmarking, weaken AURA's novelty.
Either outcome is worth knowing quickly.

---

### D6 — AURA-generated simulation data (primary)

Generated from the C1 F-16 model (`AIRCRAFT_MODEL_SURVEY.md`).

**Why generation is unavoidable:** RQ-1 requires (i) a *controlled, measurable* distribution-shift
axis, (ii) exact fault ground truth including onset time and magnitude, and (iii) the ability to
place faults and shifts in *deliberate combination* (H3). No public dataset provides any one of
these, let alone all three. This is a statement about what the question requires, not a preference
for simulation.

---

## 3. Summary

| Dataset | Real? | Sensor faults? | Fault ground truth? | Controlled shift? | Role in AURA |
|---|---|---|---|---|---|
| D1 ALFA | ✔ | ✘ | ✔ | ✘ | **External validity check** |
| D2 DASHlink | ✔ | ✘ | ✘ | ✘ | Not used |
| D3 NGAFID | ✔ | ✘ | ~ (noisy) | ✘ | Not used |
| D4 BASiC | ~ | ✔ | ✔ | ✘ | Fault-realism reference |
| D5 UAV-SEAD | ? | ? | ? | ? | **Verify first (A-7)** |
| D6 AURA sim | ✘ | ✔ | ✔ | ✔ | **Primary substrate** |

---

## 4. Consequence for validity — stated plainly

AURA's primary results will be **simulation results**. The honest scope of any conclusion is:

> *"In a nonlinear 6-DOF flight-dynamics simulation with injected sensor and actuator faults, ..."*

Mitigations adopted (per §20 of the brief), in decreasing order of strength:

1. **Independent-implementation testing.** Evaluate the frozen test set against an *independently
   implemented* model (C2 or C3), not just perturbed parameters of the training model. This is the
   only mitigation that tests against *unmodelled structure* rather than *mis-specified parameters*.
2. **Alternate aerodynamic representation.** Table-lookup (development) vs global polynomial
   (LIT-0024) (test) is a principled, literature-grounded model-mismatch axis.
3. **Parameter and noise randomisation** across all runs.
4. **Real-data check on ALFA** for the detection sub-problem.

**LIMITATION that cannot be mitigated:** none of these test whether *real* aircraft sensor faults
look like the injected fault models. That is a fundamental limit of the approach and must be stated
in every report. It is not solvable within AURA's scope.

---

## 5. Open actions

| ID | Action |
|----|--------|
| A-6 | Verify ALFA licence and citation requirements before any use |
| A-7 | Verify UAV-SEAD (LIT-0031) content and whether it already benchmarks uncertainty |
| A-8 | Check DASHlink access/redistribution terms (even though unused, to close the question) |
| A-9 | Record licence + attribution for every external artefact in `data/manifests/EXTERNAL_SOURCES.md` |
