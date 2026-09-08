# TV-N1 — Evidence Matrix

**Date:** 2026-09-08 · Companion to [`TV-N1_LITERATURE_AUDIT.md`](TV-N1_LITERATURE_AUDIT.md).

Each row maps one AURA phenomenon to the prior literature. **Evidence strength** describes the
strength of the *prior-art claim*, not of AURA's result.

Inspection levels: `FULL` = full text read locally · `ABSTRACT` = abstract read verbatim ·
`METADATA` = bibliographic record verified via Crossref, content from abstract/secondary sources.

---

| # | AURA phenomenon | Prior literature | Already established? | Closest source | What remains different? | Evidence strength |
|---|---|---|---|---|---|---|
| 1 | **Residual-based detection of unknown/unmodelled faults** (EXP-0012 F5) | Model-based FDI residual generation + statistical consistency testing; GLR; unobservability-subspace characterisation of undetectable faults | **Yes — foundational** | Massoumnia, Verghese & Willsky 1989, *IEEE TAC* 34:316–321 (`METADATA`) | Nothing of substance. AURA applies a χ² consistency test, the standard instrument, under stronger assumptions (exactly-known templates) than the classical work requires | **Very strong** |
| 2 | **A known-hypothesis posterior cannot express hypothesis-space mismatch; softmax confidence rises anyway** (EXP-0012 FACT 1, F4) | Bayesian asymptotics under misspecification (M-open): the posterior concentrates on the KL-nearest member of the model class regardless of absolute fit | **Yes — a 1966 theorem** | Berk 1966, *Ann. Math. Statist.* 37:51–58, doi:10.1214/aoms/1177699597 (`METADATA`, `SECONDARY`) | AURA gives a finite-sample numerical demonstration in a flight-dynamics setting. The mechanism is the theorem | **Very strong** |
| 3 | **Same, in the aircraft FDI setting specifically** | MMAE/IMM fault diagnosis is known to degrade when the model set omits the true system | **Yes** | Lu, Van Eykeren, van Kampen, de Visser & Chu 2015, *Control Eng. Practice* 36:39–57, doi:10.1016/j.conengprac.2014.12.007 (`METADATA`) | Lu et al. use **real flight data**; AURA uses a self-implemented model (TV-D10). The comparison favours the prior work | **Strong** |
| 4 | **Nearest-manifold false confidence — unknown faults close to known ones are the dangerous ones** (F6) | Open-set recognition: rejection performance degrades monotonically with semantic proximity of unknown to known classes; closed-set methods assign unseen modes to known ones "with high confidence" | **Yes — the field's expected result** | Open-set recognition / PHM open-set fault-mode literature (`METADATA`); Lundgren & Jung 2022 on ambiguity from similar residuals (`ABSTRACT`) | AURA quantifies a rate for six faults it authored itself. The rate estimates nothing external | **Strong** |
| 5 | **Fault-library incompleteness as a real operational problem** | Stated design driver in aircraft air-data FDI: "some modes being discovered only after being observed in operation"; motivates semi-supervised anomaly detection | **Yes — in AURA's exact application domain** | Lima Lopes, Travé-Massuyès, Jauberthie & Alcalay 2024, DX 2024, doi:10.4230/OASIcs.DX.2024.3 (`FULL`) | Nothing. The review states the problem and names the field's preferred response | **Strong** |
| 6 | **Excitation-dependent diagnosability; some faults undiagnosable without exciting the system** (F7) | Active fault diagnosis: the entire premise of the field. Guaranteed separating-input computation; "fundamentally limited by the given control sequence" | **Yes — mature field** | Scott, Findeisen, Braatz & Raimondo 2014, *Automatica* 50:1580–1589, doi:10.1016/j.automatica.2014.03.016 (`FULL`); Kong, McMahon & Lahijanian 2025, arXiv:2509.04708 (`FULL`) | Scott et al. compute a **guarantee**; AURA observed one fault's ratio decline in one condition | **Very strong** |
| 7 | **Design-time enumeration of a diagnostic system's blind spots as a function of the input** (AURA's one candidate contribution) | "Minimal detectable and isolable faults of active fault diagnosis" — a named research object with dedicated papers | **Yes** | Xu 2023, *IEEE TAC* 68:1138–1145, doi:10.1109/tac.2022.3148305; Chen, Liu, Xu & Liang 2023, *IFAC-PapersOnLine* 56:5536–5541, doi:10.1016/j.ifacol.2023.10.449 (both `METADATA`) | AURA's version is for *unmodelled* faults rather than modelled ones — but the geometry and the threshold are the same, and Kong et al. cover the unmodelled case | **Strong** |
| 8 | **Quantitative, noise-aware fault distinguishability** (EXP-0002, EXP-0010) | Distinguishability as KL divergence between fault-mode observation distributions, related to achievable residual-generator performance; Bhattacharyya-distance diagnosability conditions | **Yes** | Eriksson, Frisk & Krysander 2013, *Automatica* 49:1591–1600, doi:10.1016/j.automatica.2013.02.045 (`METADATA`); Liu, Wang, Zhang & Zhou 2022, *IEEE TAC*, doi:10.1109/tac.2021.3108587 (`METADATA`) | AURA's deflection coefficient is the same construct in a special case (Gaussian, equal covariance) | **Very strong** |
| 9 | **Unknown fault magnitude / fault size as a nuisance parameter** (EXP-0011) | Fault-size estimation within a diagnosability framework; explicit treatment of how classification difficulty varies with fault magnitude | **Yes** | Lundgren & Jung 2022, *Control Eng. Practice* 121:105006, doi:10.1016/j.conengprac.2021.105006 (`ABSTRACT`) | AURA marginalises analytically over magnitude rather than estimating it. A method variant, not a finding | **Strong** |
| 10 | **Confidence, rejection and abstention under diagnostic uncertainty** | Reject option (Chow 1970); selective classification; conformal prediction; EVT- and distance-based open-set rejection | **Yes — multiple mature literatures** | Chow 1970 (`METADATA`); open-set / conformal FDI literature (`METADATA`) | AURA has built no decision layer, so has nothing to compare | **Very strong** |
| 11 | **Aircraft-specific application: air-data sensor fault diagnosis** | Extensive: model-driven virtual sensors (EKF/UKF/EnKF variants), signal-driven, data-driven and hybrid; validated on real flight data | **Yes — 40+ papers reviewed in one 2024 survey alone** | Lima Lopes et al. 2024 (`FULL`); Lu et al. 2015 air-data FDD on real flight data, doi:10.2514/6.2015-1311 (`METADATA`) | AURA's airframe is self-implemented and never cross-validated (TV-D10) | **Strong** |
| 12 | **AURA's negative result: no practical ambiguity at realistic noise** (F1, F2) | No prior source asserts the contrary claim that AURA falsified | **Not applicable** | — | The falsified premise was AURA's own, not the field's. Overturning a belief nobody held is not a contribution | **N/A — but not novelty** |

---

## Summary

**`OBSERVATION`** Eleven of the twelve rows resolve to "already established", most with more than one
independent source, and several with sources stronger than AURA's own evidence (theorems, guarantees,
real flight data). The twelfth is not a contribution.

**`OBSERVATION`** Row 12 deserves particular attention. AURA's most distinctive result is a negative
one — and the audit could find no source claiming what AURA disproved. A negative result acquires
value by contradicting a belief the field holds; the belief that motivated AURA appears to have been
the project's own.

**`INTERPRETATION`** No row supports a novelty claim.
