# Data Management

**Date:** 2026-09-08

---

## 1. Four layers

| Layer | Path | Content | Mutable? | In Git? |
|---|---|---|---|---|
| **RAW** | `data/raw/` | Immutable source evidence: external datasets as downloaded, raw simulation output | **Never modified** | No (manifests only) |
| **PROCESSED** | `data/processed/` | Transformations of raw: resampling, alignment, splits | Regenerable | No |
| **DERIVED** | `data/derived/` | Residuals, features, labels, state estimates, uncertainty estimates, model outputs | Regenerable | No |
| **RESULTS** | `results/` | Metrics, statistical summaries, final tables, publication figures | Append-only | Metrics/figures yes; bulk arrays no |

Every processed and derived dataset records its `parent_dataset`. A dataset with no resolvable
parent chain back to RAW is invalid and may not be used in a reported result.

---

## 2. Dataset identity

```
DS-0001, DS-0002, ...
```

Every dataset has a manifest at `data/manifests/DS-XXXX.yaml`:

```yaml
dataset_id: DS-0007
name: frozen-test-combined-shift
layer: raw
source: simulation
generation_date: 2026-09-15
generation_method: simulation/run_montecarlo.py
software_version: aura 0.1.0
git_commit: <40-char sha>
configuration: infrastructure/configuration/exp0007_test.yaml
configuration_sha256: <sha>
random_seed_base: 20260915
n_runs: 10000
parent_dataset: null
checksum_manifest: data/manifests/DS-0007.sha256
units: SI (rad, m, m/s, N); angles in radians
sampling_rate_hz: 100
frozen: true
frozen_date: 2026-09-15
description: >
  Frozen test set. Combined flight-regime and fault shift (axis S6).
  Generated once before any method training. Never regenerate under this ID.
license: internal
```

**Rules:**
- IDs are stable and never reused.
- Raw data is **never overwritten**. If regeneration happens under materially different conditions
  (different code, config, seeds, or model), it gets a **new dataset ID**.
- Results computed on a superseded dataset are marked `SUPERSEDED`, not deleted.
- A `frozen: true` dataset may not be regenerated at all. Attempting to is a process failure and
  gets a `FAIL-####` record.

---

## 3. What Git stores

**Yes:** source code, configuration, documentation, schemas, dataset manifests and checksums,
metrics tables, final figures, small reference data (<1 MB, and only where it aids reproduction).

**No:** raw simulation output, processed/derived arrays, caches, temporary intermediates, model
checkpoints (unless individually justified in an ADR).

Enforced by `.gitignore`. The rule is not "keep the repo small" — it is that **Git is the record of
how data was made, and the disk holds the data.**

---

## 4. Storage strategy

**Decision: local filesystem only. No Git LFS, no cloud object storage, no database.**

Justification (CALCULATION, `reports/phase0/EXPERIMENTAL_DESIGN_PRELIMINARY.md` §10): projected
total ≈ 28 GB. Introducing LFS or object storage at this scale adds operational complexity, failure
modes, and cost without buying anything.

**Revisit conditions** — any one triggers a re-decision via ADR:
- Projected storage exceeds **100 GB**
- Data must be shared with a collaborator or published as a benchmark artefact
- Multiple machines need concurrent access

**Format:** columnar (Parquet) with zstd compression for time series; `float32` for signals
(A-INF-01); YAML for configuration; JSON for machine-readable results; CSV for small tables.

---

## 5. What is retained vs regenerated

**Permanently retained** (expensive or impossible to recreate):
- Raw external datasets as downloaded, with licence records
- Final experiment configurations
- **Frozen test sets** and their checksums
- Important validation sets
- Final model artefacts used in reported results
- Final metrics, figures, provenance manifests
- **Scientifically important failures** and the data that revealed them

**Regenerated on demand** (cheap):
- Temporary features and caches
- Exploratory plots
- Intermediate residual files from a fixed seed and config
- Disposable pilot outputs

Guiding rule: *preserve evidence that is expensive or impossible to recreate; regenerate cheap
intermediates.*

---

## 6. Integrity

- Every dataset directory has a `.sha256` file covering all its files.
- `infrastructure/validation/verify_manifests.py` (to be written) checks that every manifest
  resolves, every checksum matches, and every parent chain reaches RAW.
- **Split-leakage check:** no run identifier may appear in more than one split (TV-D6). This runs
  before any training and fails hard.

---

## 7. External sources

Every external dataset, model, code library and figure is recorded in
`data/manifests/EXTERNAL_SOURCES.md` with: source, URL, version/commit, licence, attribution
requirement, date retrieved, and how it is used.

**No external artefact is used before its licence is recorded.** Open actions A-1, A-6, A-9.
