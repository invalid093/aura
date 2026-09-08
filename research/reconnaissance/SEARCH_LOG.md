# Reconnaissance Search Log — Phase 0

**Date of reconnaissance session:** 2026-09-08
**Method:** Automated web search + selective full-text retrieval.
**Recorder:** Claude (computational research engineer role, see `CLAUDE.md`).

This file is the *evidence trail* for the Phase 0 literature reconnaissance. It exists so that
the coverage of the literature review can itself be audited and criticised. It records what was
searched, what was found, and — importantly — **what was not verified**.

---

## 1. Search coverage

| # | Query (paraphrased) | Area targeted (§6) | Outcome |
|---|---------------------|--------------------|---------|
| S-01 | deep learning sensor FDI aircraft flight control uncertainty 2024 | Aircraft health mgmt | Found DX-2024 air-data survey; several accuracy-only DL papers |
| S-02 | UQ fault diagnosis distribution shift OOD calibration deep ensembles | Uncertainty; OOD | Found the core UQ-under-shift cluster (all rotating machinery) |
| S-03 | conformal prediction fault detection aerospace coverage guarantee | Uncertainty | Found conformal-FDI cluster; one space-launcher aerospace case |
| S-04 | AeroBench / F-16 / NASA TP-1538 | Aircraft model | Confirmed Nguyen 1979 provenance; AeroBenchVV + Python port |
| S-05 | ALFA dataset UAV actuator fault | Datasets | Confirmed ALFA composition and DOI |
| S-06 | structural diagnosability Krysander/Frisk residual selection | Fault diagnosis | Confirmed structural-analysis toolchain and review |
| S-07 | selective classification / reject option / abstention | Abstention | Found Chow lineage, SelectiveNet, risk–coverage framing. **No aircraft application found.** |
| S-08 | Ovadia 2019 dataset shift uncertainty | Uncertainty | Confirmed canonical reference |
| S-09 | run-time assurance / simplex / assured autonomy aircraft | Assured autonomy | Confirmed ASTM F3269 and RTA literature |
| S-10 | MMAE / IMM / Kalman filter bank aircraft sensor fault | State estimation | Confirmed KF-bank lineage incl. NASA engine work |
| S-11 | JSBSim fault injection python | Aircraft model | Confirmed JSBSim maturity and Python wheels |
| S-12 | NASA DASHlink / NGAFID open aviation data | Datasets | Confirmed both; label semantics captured |
| S-13 | physics-informed hybrid residual generation unseen conditions | Hybrid ML | Found grey-box RNN + consistency-based diagnosis cluster |
| S-14 | uncertainty-aware decision making / when to ask for help | Assured autonomy | **Found LIT-0012, the key adversarial prior** |
| S-15 | AeroBench ARCH benchmark Heidlauf | Aircraft model | Confirmed citation |
| S-16 | ECE critique / proper scoring rules | Uncertainty | Confirmed ECE is not a proper scoring rule |
| S-17 | pitot/AoA fault, icing, analytical redundancy, accidents | Fault taxonomy | Confirmed physically-grounded sensor fault models |
| S-18 | epistemic uncertainty vs structural diagnosability ground truth | **Novelty probe** | **No direct match found** — see §3 |
| S-19 | NASA GTM / AirSTAR / fixed-wing UAV models | Aircraft model | Confirmed GTM open Simulink model |
| S-20 | FDI evaluation metrics (FAR/MDR/delay) | Metrics | Confirmed standard metric vocabulary |
| S-21 | open-source fixed-wing UAV fault injection datasets | Datasets | Found BASiC, UAV-SEAD, UAVBench |
| S-22 | Bayesian NN aircraft fault diagnosis unseen flight conditions | **Novelty probe** | Only engine-level UQ found (LIT-0069) |
| S-23 | indistinguishable faults / ambiguity groups | Diagnosability | Confirmed ambiguity-group concept exists in aerospace practice |
| S-24 | "Evaluating calibration ... under distribution shift" | Uncertainty | Retrieved abstract-level findings |
| S-25 | cross-condition aircraft fault classifier generalisation | Distribution shift | Confirmed cross-condition degradation is real in aircraft subsystems |
| S-26 | ASTM F3269 | Assured autonomy | Confirmed standard scope and versions |

**Full-text retrieval attempted on 4 sources; 3 succeeded.**

| Source | Result |
|--------|--------|
| LIT-0012 (Confidence-Gated Robot Autonomy) | **Retrieved and extracted in full** |
| LIT-0004 (Mohammadi et al., Probabilistic ML for UQ diagnosis) | **Retrieved and extracted in full** |
| LIT-0002 (Fault Diagnosis Toolbox) | Retrieved; license not stated on landing page |
| LIT-0033 (DX-2024 air data survey) | **FAILED** — PDF returned as unparsed binary. Must be read manually. |

---

## 2. Honest coverage limitations (LIMITATION)

These are real gaps in the reconnaissance and must not be papered over:

1. **Search-engine mediated.** Coverage came from a general web search index, not from a systematic
   database query (Scopus / Web of Science / IEEE Xplore / AIAA ARC). Recall is unknown and
   probably biased toward open-access and recently-indexed material.
2. **Paywall bias.** Many of the most relevant journals (RESS, Control Engineering Practice, MSSP,
   JGCD, AIAA Journal) returned abstract-level metadata only. For those entries, `key_result` in
   `literature_index.csv` reflects abstract/snippet claims, **not** a read of the method section.
3. **Verification is stratified, not uniform.** Every row in `literature_index.csv` carries a
   `verification` field with one of:
   - `FETCH_VERIFIED` — full text retrieved and extracted in this session (3 sources).
   - `SEARCH_METADATA` — title/venue/year/URL plus substantive abstract-level content from search
     results. Author lists may be partial or reconstructed and **must be checked before citation**.
   - `TITLE_URL_ONLY` — only the title and URL are reliable. Everything else is provisional.
   - `PRIOR_KNOWLEDGE` — asserted from model prior knowledge, not retrieved this session
     (LIT-0014, LIT-0026). **Must be independently confirmed.**
4. **No systematic citation-graph traversal.** Forward/backward citation chasing was not performed.
   The single highest-value next reconnaissance action is a backward/forward citation sweep from
   LIT-0004 and LIT-0005.
5. **Author attribution risk.** Several rows read `(authors not verified)`. This is deliberate:
   inventing a plausible author list is worse than recording the absence.
6. **Non-English literature not covered.**
7. **Recency asymmetry.** The index skews toward 2019–2026. Foundational 1980s–2000s FDI work
   (Willsky, Frank, Patton, Gertler, Isermann, Blanke) is under-represented and should be added
   in Phase 1 — AURA's baselines derive from that lineage.

---

## 3. Result of the explicit novelty probes

Two searches (S-18, S-22) were run specifically to try to *kill* the proposed contribution by
finding it already done. Neither returned a direct match.

**OBSERVATION (S-18):** No retrieved source validates a learned epistemic-uncertainty estimate
against structural-diagnosability ground truth. The two literatures (structural analysis /
consistency-based diagnosis, and deep UQ / calibration) are adjacent and increasingly cited
together — LIT-0004 and LIT-0047 come from the same research group and bridge them — but the
specific move of *using analytically-derived isolability as the reference against which an
uncertainty estimate is scored* was not found.

**OBSERVATION (S-22):** Uncertainty-aware fault diagnosis validated across *flight conditions* on
*aircraft flight dynamics* was not found. The nearest results are (a) engine-level UQ (LIT-0069,
unverified) and (b) aircraft-subsystem transfer learning without UQ (LIT-0051).

**INTERPRETATION (not fact):** This is weak evidence of a gap. Absence of evidence from a
non-systematic search is not evidence of absence. Before any novelty claim is published, a
systematic database search must be run. This is recorded as an open risk in
`reports/phase0/THREATS_TO_VALIDITY.md` (TV-N1).

---

## 4. Sources consulted

All URLs are recorded in `research/literature/literature_index.csv` (field `doi_or_url`).
