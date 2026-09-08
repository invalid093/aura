# Literature Review — Phase 0

**Date:** 2026-09-08
**Sources:** 70 (`research/literature/literature_index.csv`)
**Depth:** 3 read in full; 53 at abstract level; 12 at title level; 2 from prior knowledge.
**Coverage caveat:** non-systematic search. See `research/reconnaissance/SEARCH_LOG.md` §2.

---

## 1. The shape of the field

Four literatures bear on AURA. They are mature individually and only loosely connected to one
another. The connections that *are* missing are where the research opportunity lies.

```
   Aircraft FDI            Structural diagnosability
   (mature, deterministic) (mature, design-time)
          │                          │
          │        ← weakly connected →
          │                          │
   Deep UQ / calibration      Uncertainty-gated autonomy
   (mature, wrong domain)     (mature, negative results)
```

---

## 2. Aircraft fault detection and isolation

**FACT.** Model-based FDI on aircraft is a mature discipline. Analytical redundancy for air data
systems is physically grounded — pitot blockage, static-port obstruction, and AoA vane sticking are
modelled from real failure physics and are the documented cause of transport-category accidents
(LIT-0034, LIT-0033). Geometric decoupling (LIT-0036) and integrity monitoring adapted from GNSS
RAIM (LIT-0035) both give structured, statistically-motivated detection.

**FACT.** Multiple-model adaptive estimation — a bank of Kalman filters, one per fault hypothesis,
with the posterior formed from residual likelihoods — is the classical probabilistic diagnoser
(LIT-0043, LIT-0045, LIT-0044). It has a known failure mode: posterior lock-in, where one filter's
weight collapses to unity and the diagnosis becomes unrecoverable.

**OBSERVATION.** That failure mode is treated in the literature as an *estimation* problem to be
patched (selective reinitialisation, LIT-0044) rather than as what it also is: **a calibration
failure**. No retrieved source evaluates an MMAE fault posterior with proper scoring rules.

**OBSERVATION.** The recent ML branch of aircraft FDI (LIT-0039, LIT-0040, LIT-0041, LIT-0042)
reports classification accuracy, in-distribution, with a forced single-class output. Uncertainty
is absent, abstention is absent, and there is no shift protocol.

**INTERPRETATION.** The aircraft FDI literature has the *physics* and the *probabilistic
machinery*, and has not connected either to modern uncertainty evaluation. Gap G1 and G3.

---

## 3. Structural diagnosability

**FACT.** Structural analysis determines detectability and isolability from a model's equation
structure alone, without exact parameters (LIT-0001, LIT-0067). It yields isolability matrices,
minimal over-determined (MSO) equation sets, residual generator candidates, and sensor placement
guidance. Open tooling exists in Python (LIT-0002, `FETCH_VERIFIED`).

**FACT.** Isolability is **mode-dependent** — diagnostic test selection differs across operating
modes (LIT-0068). Ambiguity groups (sets of faults sharing a signature) are an established concept
in aerospace practice, and ambiguity grows as available measurements shrink.

**OBSERVATION.** Structural analysis is used almost exclusively at *design time*: choose sensors,
choose residuals, prove isolability. It is not used at run time, and — critically for AURA — it is
not used as **ground truth against which a learned uncertainty estimate is scored**.

**INTERPRETATION.** This is the most distinctive asset available to AURA. Uncertainty
quantification research is normally handicapped by having no reference for what the "correct"
uncertainty is; here, structural isolability supplies a *lower bound* on ambiguity that is
computable, mode-dependent, and independent of any learned model. Gap G4.

**Caveat (A-UNC-03).** Structural conditions are necessary, not sufficient. Structurally isolable
faults may still be practically indistinguishable at realistic noise levels. Structural isolability
therefore *bounds* ambiguity; it does not determine it. AURA must state this rather than treat the
matrix as truth.

---

## 4. Uncertainty quantification under distribution shift

**FACT.** The canonical result (LIT-0009, Ovadia et al. 2019) is that post-hoc calibration does not
survive dataset shift, and that methods marginalising over models — ensembles — degrade most
gracefully.

**FACT.** This has been replicated in fault diagnosis. LIT-0005 finds that calibration degrades
monotonically with shift, that good in-distribution calibration does **not** imply good shifted
calibration, and that deep ensembles are the most robust option. LIT-0006 and LIT-0007 add OOD
detection and Bayesian treatment, decomposing aleatoric, epistemic and distributional uncertainty.

**OBSERVATION.** Essentially all of this work is on **rotating machinery** — bearings, gearboxes,
turbines — with quasi-static features. There is no state estimator in the loop, no dynamics, and
"operating condition" is a load or speed setting rather than a physical flight regime.

**FACT (methodological).** ECE is not a proper scoring rule. It is binning-sensitive (LIT-0010) and
can be driven to zero by an uninformative model that discards all instance-specific information
(LIT-0011). Decision-theoretic expected cost and proper scoring rules are the defensible targets.

**INTERPRETATION.** The methodology exists and is well-validated — in the wrong domain. Gap G2.
This is why "apply UQ-under-shift to aircraft" (RD-A) is an application study rather than research.

---

## 5. The closest prior work

**LIT-0004 — Mohammadi, Krysander, Jung & Frisk (2025), `FETCH_VERIFIED`.**

This paper does most of what an "uncertainty-aware AURA" would do: ensemble probabilistic neural
networks, explicit aleatoric/epistemic separation, adaptive residual thresholds driven by predicted
variance, epistemic uncertainty used to flag out-of-distribution samples and **issue a warning
instead of a diagnosis** — i.e. abstention — all inside a consistency-based diagnosis framework.
Evaluated on a two-tank system, an SCR aftertreatment system, and a turbocharged engine test bench.

**This is the single most important entry in the index.** It is simultaneously:
- the strongest threat to AURA's novelty (TV-N2),
- the required baseline B4, and
- the source of AURA's most promising hypothesis.

Because among its stated limitations is this:

> OOD detection can suppress fault-induced anomalies, increasing missed detections when operating
> point shifts coincide with faults.

**OBSERVATION.** The authors state the failure mode and do not quantify it.

**INTERPRETATION.** That unquantified confound is a well-defined, measurable, previously-unmeasured
quantity — and it is exactly the situation an aircraft faces when it manoeuvres into an unfamiliar
regime *and* a sensor degrades. It became hypothesis H3. Gap G6.

Note that H3 is **method-independent**: it is a property of novelty gating in general, so its result
stands whether or not AURA's own method succeeds.

---

## 6. Abstention and set-valued prediction

**FACT.** Classification with a reject option has a Bayes-optimal solution under a fixed abstention
cost (LIT-0014, Chow 1970). Modern treatments give risk–coverage curves and jointly-trained
selectors (LIT-0013). Conformal prediction gives distribution-free finite-sample coverage for
prediction *sets* (LIT-0016), and has been applied to fault detection to reduce false alarms
(LIT-0017, LIT-0018) and in aerospace FDD (LIT-0019).

**FACT.** Conformal guarantees rest on exchangeability — which is violated precisely under the
distribution shift AURA studies.

**OBSERVATION (from the S-07 null search).** No retrieved source applies selective
classification / abstention to *aircraft* fault diagnosis. And nowhere is abstention decomposed
into *"the evidence is ambiguous"* versus *"I am out of my competence"* — despite these calling for
different responses.

**INTERPRETATION.** Gap G7. The set-valued output form is directly reusable; the decomposition is
not present.

---

## 7. Uncertainty-gated autonomy — and the adversarial prior

**FACT.** Run-time assurance is the certification-credible architecture for bounding functions that
cannot be verified conventionally. It is standardised (ASTM F3269, LIT-0052, LIT-0053) and has a
substantial technical literature (LIT-0054, LIT-0055, LIT-0056). Competence-aware autonomy provides
formal machinery for a system to decide when to request human assistance (LIT-0058), and
factorised self-confidence argues that a scalar confidence is insufficient (LIT-0059).

**FACT — and this is the result AURA must confront.** LIT-0012 (Gaus, Charaja & Haeufle, 2026,
`FETCH_VERIFIED`) compared seven uncertainty estimators under threshold-gated deferral. Findings:

1. Below a dataset-dependent **competence threshold**, uncertainty ranking is weak and unstable —
   deferral does not meaningfully reduce execution error.
2. Above it, **all seven estimators produce nearly indistinguishable act/defer decisions**
   (agreement > 97.8%; Spearman ρ ≈ 0.27–0.30 across methods).
3. **The threshold dominates**, not the estimator: restricting to the 10% most confident predictions
   cut error from 36.5% to 19.9%, while swapping entropy for margin changed outcomes by < 0.5%.
4. Uncertainty degrades gracefully under *covariate* shift, but **semantic OOD detection was near
   chance** (AUROC 0.35–0.49).

**INTERPRETATION.** This is a direct prediction that AURA's central hypothesis will fail. The stated
reason it might not transfer is that all seven of their estimators read the *same* evidence — a
softmax over one learned representation — making them near-monotone transformations of one another.
AURA's two components read structurally different evidence: residual likelihood structure versus
operating-point position.

That is an argument, not a result. It is adopted as H1's falsification condition rather than argued
away. Gap G5.

---

## 8. Models and data

**Aircraft models.** The open academic F-16 lineage traces to 1979 NASA wind-tunnel data
(LIT-0020), formalised in a standard textbook (LIT-0026), and implemented as a V&V benchmark
(LIT-0021) with a Python port (LIT-0022) and Julia/MATLAB variants (LIT-0023). An alternative
global-polynomial aerodynamic representation exists (LIT-0024), which is a principled
model-mismatch axis. JSBSim (LIT-0025) is more capable but less transparent. NASA's GTM/AirSTAR
(LIT-0032) has the best fault-research heritage but requires MATLAB.

**Data.** ALFA (LIT-0027) is the only open real fixed-wing dataset with labelled fault type and
onset time — but its faults are actuator and engine failures, not sensor faults, and post-fault
flight time totals about 13 minutes. DASHlink (LIT-0028) and NGAFID (LIT-0029) are large and real
but label *operational anomalies* and *maintenance events* respectively, neither of which supports
fault isolation. BASiC (LIT-0030) is sensor-fault focused but multirotor and simulation-dominant.
UAV-SEAD (LIT-0031) is unverified and must be checked early.

**OBSERVATION.** No open dataset combines fixed-wing flight dynamics, sensor-fault ground truth,
and a controlled distribution-shift axis. Gap G8 — which means AURA must generate its primary data,
and means the resulting benchmark has value independent of AURA's hypothesis.

---

## 9. What the literature establishes, and what it leaves open

### Established
1. Calibration degrades under distribution shift; in-distribution calibration does not transfer.
2. Deep ensembles are the most robust practical UQ method under shift.
3. ECE is an inadequate primary metric.
4. Structural analysis determines isolability from equation structure, and isolability is
   mode-dependent.
5. Classical MMAE produces a principled fault posterior with a known lock-in failure mode.
6. Threshold-gated deferral works; the threshold matters far more than the estimator (in the one
   domain where this has been tested carefully).
7. Aircraft sensor faults have well-documented physical models.

### Open
1. Whether UQ-under-shift results transfer to flight dynamics with a state estimator in the loop.
2. Whether classical MMAE posteriors are calibrated. **Nobody appears to have checked.**
3. **How much novelty gating suppresses genuine fault detection when shift and fault co-occur.**
   Stated as a limitation by LIT-0004; unmeasured.
4. Whether learned uncertainty agrees with analytically-derived indistinguishability.
5. Whether the estimator-equivalence result (LIT-0012) survives when estimators read structurally
   different evidence.
6. Whether abstention should be decomposed by *reason*, given that different reasons imply
   different correct responses.

Items 2–5 are AURA's targets. Item 3 is the one most likely to yield a clean result.

---

## 10. Honest assessment of this review

**LIMITATION.** Three of seventy sources were read in full. Fifty-three are characterised from
abstract-level evidence, which is enough to place a paper in the map but not enough to verify a
method claim. Twelve are title-level only. Two rest on unverified prior knowledge.

**LIMITATION.** Foundational FDI work (Willsky, Frank, Patton, Gertler, Isermann, Blanke) is
under-represented, despite AURA's baselines descending from it. This is a real coverage hole and is
first in the Phase 1 reading queue after LIT-0033.

**LIMITATION.** No citation-graph traversal was performed. A backward/forward sweep from LIT-0004
and LIT-0005 is the highest-value next action and could close gap G6 — in which case AURA re-scopes.

**The gap claims in this review are provisional and must not be published before a systematic
database search (TV-N1).**
