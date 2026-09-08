# Research Gap Matrix — Phase 0

**Date:** 2026-09-08
**Status:** Provisional. Based on a non-systematic search (see `research/reconnaissance/SEARCH_LOG.md`).

Every claim below is tagged with an evidence class per `docs/methodology.md`:
`FACT` / `OBSERVATION` / `INTERPRETATION` / `HYPOTHESIS` / `ASSUMPTION` / `LIMITATION`.

---

## 1. The gap matrix

| # | Area | State of the art | Limitation | Evidence | Opportunity |
|---|------|------------------|------------|----------|-------------|
| **G1** | Aircraft sensor fault diagnosis with ML | Deep models (CNN/LSTM/GNN/CNN-on-images) achieve high classification accuracy on aircraft sensor faults | Evaluated by **accuracy alone**, in-distribution, with a forced single-class answer. No calibration, no abstention, no shift protocol | LIT-0039, LIT-0040, LIT-0041, LIT-0042 (OBSERVATION) | Re-pose aircraft sensor diagnosis as a *decision-under-uncertainty* problem rather than a classification problem |
| **G2** | UQ under distribution shift | Mature and well-benchmarked: calibration degrades with shift; ID calibration does not transfer; deep ensembles most robust | Almost entirely **rotating machinery / static-feature** domains. No coupling to state estimation, no dynamics, no physically-meaningful shift axis | LIT-0005, LIT-0006, LIT-0007, LIT-0009, LIT-0049, LIT-0050 (OBSERVATION) | Replicate the shift-calibration protocol in a **flight-dynamics** setting where shift has physical meaning (airspeed, altitude, load factor) |
| **G3** | Model-based FDI on aircraft | Very mature: analytical redundancy, geometric decoupling, integrity monitoring, MMAE/KF banks. Produces *principled* fault posteriors | The posterior from a KF bank / MMAE is essentially **never evaluated as a calibrated probability**. Known failure mode (posterior lock-in) is treated as an estimation bug, not a miscalibration | LIT-0034, LIT-0035, LIT-0036, LIT-0043, LIT-0044, LIT-0045 (OBSERVATION) | Evaluate the classical MMAE posterior with modern calibration/proper-scoring tools. This is a cheap, high-value, possibly-negative result |
| **G4** | Structural diagnosability | Mature theory: isolability matrices, MSO sets, sensor placement, mode-dependent test selection | Used at **design time** to choose residuals/sensors. Not used at **run time**, and not used as ground truth for evaluating learned uncertainty | LIT-0001, LIT-0002, LIT-0003, LIT-0067, LIT-0068 (OBSERVATION) | Use structural isolability as an **analytic reference signal** for what an uncertainty estimate *should* say. This is unusual: UQ research rarely has ground truth for "correct" uncertainty |
| **G5** | Uncertainty-gated autonomy | Threshold-gated deferral is the standard architecture (RTA / simplex / competence-aware systems) | A strong recent **negative result**: across 7 estimators, act/defer decisions agree >97.8%; the *threshold* dominates, not the estimator. Semantic OOD detection near chance | LIT-0012 (FETCH_VERIFIED), LIT-0052, LIT-0054, LIT-0058, LIT-0059 (OBSERVATION) | Test whether that equivalence result **also holds** when the uncertainty is derived from physics-based residuals rather than a softmax head. If it holds, that is a valuable negative result for aerospace |
| **G6** | Shift/fault confounding | Uncertainty-aware diagnosis with an epistemic OOD gate reduces false alarms on industrial systems | The authors explicitly state that **OOD gating can suppress genuine fault signatures** when an operating-point shift coincides with a fault — and do not quantify it | LIT-0004 (FETCH_VERIFIED, stated limitation) | **Quantify the confounding curve.** Missed-detection rate vs shift magnitude under novelty gating. This is a directly measurable, previously-unmeasured quantity |
| **G7** | Abstention in diagnosis | Well-developed theory (Chow, risk–coverage, SelectiveNet, conformal prediction sets) | No retrieved application to aircraft fault diagnosis; and abstention is never separated into *"the evidence is genuinely ambiguous"* vs *"I am out of my competence"* | LIT-0013, LIT-0014, LIT-0016, LIT-0017 + S-07 null result (OBSERVATION) | Two-component abstention with **different correct responses**: ambiguity → return a fault *set* and continue; novelty → escalate |
| **G8** | Aerospace UQ datasets/benchmarks | ALFA (real, actuator faults), DASHlink/NGAFID (real, operational anomalies), BASiC (simulated sensor faults, multirotor) | No open benchmark couples (i) fixed-wing flight dynamics, (ii) sensor+actuator fault ground truth, (iii) a *controlled distribution-shift axis*, and (iv) uncertainty evaluation | LIT-0027 – LIT-0031 (OBSERVATION) | A reproducible open benchmark is itself a defensible contribution, independent of whether the primary hypothesis is supported |

---

## 2. What is *not* a gap (novelty hygiene)

Per §9 of the Phase 0 brief, the following do **not** constitute novelty and are explicitly
disclaimed as contributions:

- **A different aircraft.** Running an existing method on an F-16 instead of a gearbox is not a
  contribution unless the flight-dynamics setting changes the *conclusion*.
- **A different neural architecture.** A better classifier is not the research question.
- **Combining existing methods.** Ensembles + conformal + structural analysis is integration
  engineering unless the combination answers a question none of them answer alone.
- **"Uncertainty-aware X".** LIT-0004 already does uncertainty-aware, epistemic-gated,
  consistency-based diagnosis with abstention. AURA is *downstream* of that work, not ahead of it.
- **Higher fidelity simulation.** Fidelity is a cost. It buys nothing unless the research question
  requires it.

**INTERPRETATION:** The only defensible novelty available to AURA is in the **evaluation and
decomposition** of uncertainty, not in the method that produces it. Specifically: G4 (structural
ground truth for uncertainty), G6 (quantifying the shift/fault confound), and G5 (testing whether
the confidence-gating equivalence result survives contact with physics-derived evidence).

---

## 3. Threat to the whole gap analysis

**LIMITATION (recorded, not resolved):** LIT-0004 (Mohammadi, Krysander, Jung & Frisk 2025) is
close enough to AURA that it could plausibly be extended by its own authors to cover G6 before
AURA produces results. AURA's defensible position is therefore **not** "we invented
uncertainty-aware diagnosis" but "we measured a specific failure mode that the field has stated
but not quantified, in a domain where it matters, with an analytic ground truth the field does not
usually have."

If a Phase 1 systematic search finds that G4 or G6 is already closed, the correct response is to
say so in `docs/decisions/` and re-scope — not to proceed and claim novelty anyway.
