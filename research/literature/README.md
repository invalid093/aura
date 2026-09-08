# Literature Database

**Primary file:** `literature_index.csv` — 70 curated sources with stable IDs `LIT-0001` … `LIT-0070`.
**Evidence trail:** `../reconnaissance/SEARCH_LOG.md`.
**Narrative synthesis:** `../../reports/phase0/LITERATURE_REVIEW.md`.

---

## Schema

Columns follow §7 of the Phase 0 brief, plus one addition:

```
source_id, authors, title, year, publication, doi_or_url, source_type, research_area,
method, dataset, vehicle, fault_type, uncertainty_method, evaluation_metrics,
key_result, limitation, relevance_to_AURA, possible_gap, verification
```

CSV convention: fields use `;` as an internal separator so that `,` remains an unambiguous
delimiter.

---

## The `verification` field

This column is the most important one in the file. It exists because a literature database that
does not distinguish *"I read this"* from *"I saw the title"* is a liability.

| Value | Meaning | Safe to cite? |
|---|---|---|
| `FETCH_VERIFIED` | Full text retrieved and extracted in the reconnaissance session | Yes |
| `SEARCH_METADATA` | Title, venue, year and URL reliable; substantive content from abstract-level search results. Author lists may be partial or reconstructed | **Verify authors before citing** |
| `TITLE_URL_ONLY` | Only title and URL are reliable. Everything else is provisional | **No — verify first** |
| `PRIOR_KNOWLEDGE` | Asserted from model prior knowledge, not retrieved | **No — confirm against a database** |

Counts as of 2026-09-08 (n = 70): `FETCH_VERIFIED` 3 · `SEARCH_METADATA` 53 · `TITLE_URL_ONLY` 12 ·
`PRIOR_KNOWLEDGE` 2. **Only 3 of 70 sources (4%) were read in full.**

**Rows reading `(authors not verified)` are deliberate.** Inventing a plausible author list is
worse than recording the absence of one.

---

## Triage stage reached

```
Discovery ──► Title/Abstract screen ──► Relevance assessment ──► High-value papers ──► Full extraction
   ✔                    ✔                        ✔                       ✔                  partial
```

Full extraction was performed on three sources only. That was deliberate — the brief warns against
deep-reading everything. Extraction was prioritised on sources that could change the research
question, methodology or novelty assessment:

| Source | Why it was prioritised |
|---|---|
| **LIT-0012** — Confidence-Gated Robot Autonomy | The strongest adversarial prior. Its equivalence result became AURA's falsification condition |
| **LIT-0004** — Mohammadi, Krysander, Jung & Frisk | The closest prior work. Its stated limitation became hypothesis H3 |
| **LIT-0002** — Fault Diagnosis Toolbox | The candidate tool for H2's ground truth |

---

## Priority reading queue for Phase 1

Ordered by how much each could change the plan:

1. **LIT-0033** — DX-2024 air data sensor diagnosis survey. Retrieval failed in Phase 0; must be
   read manually. A survey-level gap statement could confirm or dissolve G1.
2. **LIT-0004** — re-read the method section in full, not just the extraction. It is the baseline
   AURA must beat (B4), so its implementation details matter.
3. **LIT-0005** — the shift-calibration protocol AURA adapts.
4. **LIT-0043 / LIT-0044** — MMAE posterior behaviour, for baseline B1 and hypothesis H4.
5. **LIT-0031** — UAV-SEAD. If it already benchmarks uncertainty on state-estimation anomalies, it
   affects AURA's novelty claim.
6. **Foundational FDI literature** (Willsky, Frank, Patton, Gertler, Isermann, Blanke) — currently
   under-represented in the index, and AURA's baselines derive from that lineage.

---

## Known gaps in coverage

Stated in full in `../reconnaissance/SEARCH_LOG.md` §2. In short: search-engine mediated (not a
systematic database query), paywall-biased, no citation-graph traversal, English only, and skewed
toward 2019–2026.

**A systematic search is a Phase 1 gate before any novelty claim (TV-N1).**
