# AURA — Phase 0 Research Handoff Report

**Self-contained. No attachments required. Intended for independent critical review by another AI
system or human reviewer.**

**Date:** 2026-09-08 · **Phase:** 0 (complete) · **Experiments run:** 0 · **Results:** none

---

## TASK

Execute Phase 0 of AURA (Autonomous Uncertainty & Reliability Architecture): establish the
scientific and computational foundation for a research programme on uncertainty-aware autonomous
health management for uncrewed aircraft, before any substantive implementation — and determine
whether the project deserves to be built at all.

## OBJECTIVE

Determine what scientific problem to investigate, whether it is novel, what would test it, what
would falsify it, what infrastructure is needed, what should explicitly not be built, and whether
to proceed.

## WORK PERFORMED

- 26 literature searches across aircraft health management, state estimation, fault diagnosis,
  machine learning, uncertainty quantification, distribution shift/OOD, and assured autonomy.
- 4 full-text retrievals attempted; 3 succeeded, 1 failed (recorded).
- Built a 70-source literature index with a stratified `verification` field.
- Built an 8-row research gap matrix with an explicit "what is not a gap" section.
- Developed and scored 6 candidate research directions; selected a 7th synthesised from three of them.
- Surveyed 7 aircraft modelling approaches and 6 candidate datasets.
- Defined the uncertainty framework, distribution-shift framework, sensor suite, fault taxonomy,
  baselines, metrics, cost model, and staged experiment plan.
- Performed the mandatory validity attack: 23 threats catalogued, 3 unmitigated.
- Built repository, infrastructure documents, JSON schemas, experiment registry, ADRs.

## KEY FINDINGS

1. **The original research question was not testable.** It contained four separable programmes, no
   comparison, and no falsification condition.
2. **The UQ-under-distribution-shift literature is mature but concentrated in rotating machinery.**
   Aircraft fault diagnosis has the physics and the probabilistic machinery, and has not connected
   either to modern uncertainty evaluation.
3. **A directly adversarial prior result exists.** Gaus, Charaja & Haeufle (arXiv:2605.18045, 2026)
   compared seven uncertainty estimators under threshold-gated deferral: act/defer agreement > 97.8%,
   the threshold dominated the estimator, and semantic OOD detection was near chance (AUROC 0.35–0.49).
4. **The closest prior work states — and declines to measure — the most promising quantity.**
   Mohammadi, Krysander, Jung & Frisk (arXiv:2509.18810, 2025) note that epistemic OOD gating can
   *suppress* fault-induced anomalies when an operating-point shift coincides with a fault.
5. **Structural diagnosability analysis can supply analytic ground truth for uncertainty.** No
   retrieved source scores a learned uncertainty estimate against structural isolability.
6. **No open dataset combines fixed-wing flight dynamics, sensor-fault ground truth and a controlled
   shift axis.**

---

## FACTS (externally verifiable)

- Post-hoc calibration does not survive dataset shift; ensembles degrade most gracefully
  (Ovadia et al., NeurIPS 2019, arXiv:1906.02530).
- Calibration of deep fault-diagnostic models degrades monotonically with shift; good ID calibration
  does not imply good shifted calibration (Xiao et al., *Computers in Industry*, 2025).
- ECE is not a proper scoring rule and can be driven to zero by an uninformative model
  (Nixon et al. arXiv:1904.01685; Ferrer arXiv:2408.02841).
- Structural analysis yields isolability from equation structure without exact parameters; isolability
  is mode-dependent (*Applied Sciences* 13(22):12241, 2023; OASIcs.DX.2024.28).
- MMAE / Kalman-filter banks form fault posteriors from residual likelihoods and exhibit posterior
  lock-in (NASA NTRS 20030067984; JGCD 10.2514/1.G000587).
- ALFA contains 47 fixed-wing flights with labelled engine and control-surface faults; ~66 min
  nominal, ~13 min post-fault (IJRR 40(2-3), DOI 10.1177/0278364920966642).
- The academic open F-16 model derives from NASA TP-1538 (Nguyen et al., 1979).
- ASTM F3269-21 standardises run-time assurance for aircraft systems containing complex functions.

## CALCULATIONS

Storage forecast, assumptions stated:
30 s runs at 100 Hz → 3,000 samples; ~48 channels; float32 → **576 kB/run uncompressed**;
assumed 3× compression → **~190 kB/run**.
Pilot 200 → 57 MB · Medium 5,000 → 1.4 GB · Full 50,000 → 14 GB · Frozen test 10,000 → 2.9 GB ·
**project total ≈ 28 GB** (with 1.5× repeats).
Runtime: assumed 2 s/run → 50,000 runs ≈ **28 core-hours** ≈ 3.5 h on 8 cores.
→ Conclusion: local disk only; no Git LFS, no cloud, no database.
**Both the compression ratio and the per-run runtime are assumptions, not measurements.**

## OBSERVATIONS (from Phase 0 activity, not experiments)

- Two explicit novelty probes returned no direct match: (a) validating learned epistemic uncertainty
  against structural-diagnosability ground truth; (b) uncertainty-aware fault diagnosis evaluated
  across flight conditions on aircraft flight dynamics.
- No retrieved source applies selective classification / abstention to aircraft fault diagnosis.
- Recent ML aircraft-FDI papers report accuracy only, in-distribution, with forced single-class output.
- Only 3 of 70 indexed sources were read in full.

## INTERPRETATIONS (our reading, contestable)

- The absence of matches in the novelty probes is **weak** evidence of a gap. A non-systematic search
  cannot establish absence.
- Structural isolability *bounds* evidential ambiguity rather than determining it — structural
  conditions are necessary, not sufficient.
- The estimator-equivalence result may not transfer because all seven estimators in that study read
  the same evidence (one softmax head), making them near-monotone transformations of one another.
  **This is an argument, not a result.**
- The only defensible novelty available is in the *evaluation and decomposition* of uncertainty, not
  in the method producing it.

## HYPOTHESES (pre-registered, untested)

| ID | Claim | Primary metric | Falsified if |
|----|-------|----------------|--------------|
| H1 | Two-component $(A,N)$ policy beats the best scalar gate | Expected decision cost at matched coverage | CI on paired difference contains zero, **or** >95% decision agreement |
| H2 | $A$ and $N$ are empirically separable (**gate on interpreting H1**) | $\rho(A,N)$; association with ground truth | $\lvert\rho\rvert \ge 0.6$ |
| H3 | Novelty gating suppresses real faults as shift grows | MDR gap vs shift magnitude | Flat/non-monotonic; no crossover |
| H4 | MMAE posterior is overconfident and degrades fast under shift | NLL / Brier | MMAE competitive under shift |
| H5 | Ambiguity sets achieve valid coverage | Set coverage and size | Under-coverage beyond prediction |

**Prior belief, stated honestly: H1 is more likely to be falsified than supported. H3 is the most
likely to yield a clean result, and is method-independent.**

## ASSUMPTIONS (register: `docs/assumptions.md`)

Most consequential:
- **A-SIM-01** — the model is a representative nonlinear high-performance aircraft, not a validated
  F-16. No claim about real aircraft is licensed.
- **A-SEN-01** — excluding GPS is legitimate. *The most questionable choice in the design.* A
  GPS-included sensitivity run is mandatory and declared in advance.
- **A-FLT-03** — elevator effectiveness loss and pitch-rate scale error form a
  *flight-condition-dependent* ambiguity pair. **Untested; the whole design rests on it.**
- **A-UNC-03** — structural isolability is a valid *lower bound* on ambiguity.
- **A-INF-02 / A-INF-03** — 2 s/run runtime, 3× compression. Both unmeasured.
- **A-LIT-01** — the identified gap is real. Unverified.

## DECISIONS

| ADR | Decision | Status |
|---|---|---|
| 0001 | Repository structure; no CI/containers/tracking service at this scale | Accepted |
| 0002 | Adopt RD-G; original question replaced as untestable | Accepted, provisional on TV-N1 |
| 0003 | AeroBenchVVPython F-16 primary; GTM rejected on MATLAB dependency; small-UAS fallback | Accepted, blocked on licence |
| 0004 | Local storage only; no Git LFS, no cloud | Accepted |
| 0005 | Sensor suite excludes GPS, with a mandatory sensitivity run | Accepted with reservation |

## FILES CREATED

`README.md`, `CLAUDE.md`, `FINDINGS.md`, `LICENSE`, `.gitignore`
`docs/`: project_charter, research_question, hypotheses, assumptions, scope, methodology, decisions/ (5 ADRs + README)
`research/`: reconnaissance/SEARCH_LOG, literature/literature_index.csv (70 sources) + README, gaps/GAP_MATRIX, hypotheses/CANDIDATE_RESEARCH_QUESTIONS
`infrastructure/`: data_management, experiment_management, reproducibility, reporting, schemas/ (3 JSON schemas + README)
`experiments/`: REGISTRY, TEST_SET_ACCESS_LOG, failures/README
`reports/phase0/`: PHASE0_RESEARCH_REPORT, RESEARCH_DIRECTION_COMPARISON, EXPERIMENTAL_DESIGN_PRELIMINARY, AIRCRAFT_MODEL_SURVEY, DATASET_SURVEY, LITERATURE_REVIEW, THREATS_TO_VALIDITY
`data/`: README, manifests/EXTERNAL_SOURCES
`handoffs/`: this file

## FILES MODIFIED

None (new repository).

## EXPERIMENTS

**None run.** Nine registered with status `PLANNED`. EXP-0001 (instrumentation) and **EXP-0002
(structural isolability)** are hard gates; EXP-0002 can invalidate the entire design and is
scheduled before any learning code is written.

## RESULTS

**None.** Nothing in this repository is a validated finding.

## FAILURES

One Phase 0 process failure, no experiment involved: full-text retrieval of the DX-2024 air data
sensor diagnosis survey (LIT-0033) failed — the PDF returned as unparsed binary. It is first in the
Phase 1 reading queue.

## LIMITATIONS

1. **TV-N1 — novelty unverified.** Non-systematic, search-engine-mediated, paywall-biased, no
   citation-graph traversal, English only, skewed 2019–2026. Foundational FDI literature
   (Willsky, Frank, Patton, Gertler, Isermann, Blanke) is under-represented despite AURA's baselines
   descending from it.
2. **Only 3 of 70 sources read in full.** 53 characterised at abstract level, 12 at title level, 2
   from unverified prior knowledge. Rows marked `(authors not verified)` are deliberate — inventing
   a plausible author list would be worse.
3. **TV-D1 — residual simulation bias.** Even the strongest OOD axis remains within one aerodynamic
   data lineage. Whether real sensor faults resemble the injected models is **not verifiable within
   scope**.
4. **TV-D9 — single airframe, single sensor suite, seven fault modes.**
5. **Runtime, compression and determinism are all unmeasured assumptions.**
6. **TV-N2 — the closest prior group is better placed to close the same gap.**

## OPEN QUESTIONS

1. Does structural isolability actually vary with flight condition for this model, suite and fault
   set? **If not, the design fails.** (EXP-0002)
2. Does a systematic search close gaps G4 or G6?
3. Are the AeroBenchVVPython, Fault Diagnosis Toolbox and ALFA licences suitable?
4. Does UAV-SEAD already benchmark uncertainty on state-estimation anomalies?
5. Should evidential ambiguity be defined over fault modes, or fault modes plus magnitude?
6. Is the cost model defensible, or should the decision layer be evaluated a different way entirely?

## RECOMMENDATION

**Proceed to Phase 1a only — four gates, in order:** systematic literature search; licence
verification; EXP-0001 (runtime, storage, determinism); **EXP-0002 (structural isolability)**.
Do not write learning code, generate bulk data, or implement baselines until all four pass.

The design's value does not depend on the primary hypothesis being supported — which is the property
that makes it worth starting. It does depend on EXP-0002, which is cheap.

## NEXT ACTION

Run **EXP-0002**: derive the structural model for the chosen aircraft, sensor suite and fault set,
and compute the isolability matrix at ≥3 flight conditions. Pass condition, declared in advance:
the matrix must be **neither fully diagonal nor fully dense**, and must **differ across flight
conditions**.

---

# REVIEWER INSTRUCTIONS

**Your purpose is independent scientific criticism, not confirmation.** A review that agrees with
this document has probably not done its job. Please attack:

**Novelty** — Is the gap real, or an artefact of a shallow search? Search for prior work that
already validates learned uncertainty against structural diagnosability, or that quantifies
shift/fault confounding. If you find it, say so plainly.

**Framing** — Is the two-component decomposition ($A$ vs $N$) genuinely different from the standard
aleatoric/epistemic split, or a relabelling? H2 is supposed to test this — is that test adequate?

**Methodology** — Are the baselines credible and fairly specified? Is B4 (the closest prior work)
sufficient as the decisive comparator? Is the cost model defensible, or does the $\rho$-sweep merely
disguise arbitrariness?

**Experimental design** — Is the shift axis genuinely out-of-distribution, or interpolation inside a
box the authors drew? Is S4 (alternate aerodynamic representation) a real structural shift or a
cosmetic one?

**Statistical validity** — Is the equivalence test (TOST, δ = 2%) appropriately powered? Is the
multiple-comparisons treatment adequate given the factorial size?

**Hidden bias** — Is excluding GPS (A-SEN-01) defensible, or does it engineer the effect being
measured? Does the mandatory sensitivity run actually address this, or just document it?

**Simulation bias** — What conclusions could be artefacts of the F-16 model specifically? Is the
1979 aerodynamic data a problem for any claim made here?

**Data leakage / contamination** — Is scenario-level splitting sufficient? What leakage paths have
been missed? Is the label-shuffle control adequate?

**Uncertainty calibration** — Is expected decision cost the right primary metric? What would a
decision-theorist object to?

**Unsupported conclusions** — Identify any statement in this document that outruns its evidence,
especially any interpretation presented as fact.

**Scope** — Is the project too narrow to support its conclusions, or still too broad to finish?

---

## MACHINE-READABLE CONTEXT

```json
{
  "project": "AURA",
  "phase": 0,
  "date": "2026-09-08",
  "status": "complete_with_unresolved_items",
  "experiments_run": 0,
  "validated_results": 0,
  "research_question_id": "RQ-1",
  "research_question": "Does representing evidential ambiguity separately from competence loss produce better act/abstain/escalate decisions than a single scalar confidence, under combined flight-regime and fault shift?",
  "primary_hypothesis": "H1",
  "prior_belief_h1": "more likely falsified than supported",
  "adversarial_prior": "arXiv:2605.18045 (estimator equivalence >97.8% act/defer agreement)",
  "closest_prior_work": "arXiv:2509.18810 (uncertainty-aware consistency-based diagnosis)",
  "gap_source": "stated-but-unmeasured limitation of closest prior work (shift/fault confounding)",
  "literature_sources": 70,
  "sources_read_in_full": 3,
  "aircraft_model": "AeroBenchVVPython F-16 (NASA TP-1538 aerodynamics)",
  "sensor_channels": 13,
  "gps_excluded": true,
  "fault_modes": 7,
  "shift_axes": 6,
  "baselines": ["B0_chi2", "B1_MMAE", "B2_softmax", "B3_ensemble", "B4_ensemble_PNN_OOD", "B5_conformal"],
  "decisive_baseline": "B4",
  "primary_metric": "expected_decision_cost_at_matched_coverage",
  "cost_ratio_sweep": [5, 10, 30, 100],
  "storage_forecast_gb": 28,
  "git_lfs": false,
  "cloud_storage": false,
  "unmitigated_threats": ["TV-N1_novelty_unverified", "TV-D1_simulation_bias", "TV-D9_single_airframe"],
  "blocking_gates": ["systematic_literature_search", "licence_verification", "EXP-0001_runtime", "EXP-0002_structural_isolability"],
  "decisive_gate": "EXP-0002",
  "recommendation": "proceed_to_phase_1a_gates_only",
  "abandonment_criteria": ["H2_and_H3_both_falsified", "systematic_search_closes_G4_and_G6", "flight_condition_invariant_isolability"]
}
```
