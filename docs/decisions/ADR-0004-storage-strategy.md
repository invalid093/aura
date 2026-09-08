# ADR-0004 — Storage strategy: no Git LFS, no cloud

**Date:** 2026-09-08 · **Status:** Accepted

## Context

The Phase 0 brief asks whether Git LFS, external artefact storage, compressed archives, local
archive storage or cloud object storage are needed — and instructs that actual data generation be
measured before introducing complicated infrastructure.

## Decision

**Local filesystem only.** Bulk data stays out of Git; manifests and checksums go in Git. Columnar
Parquet with zstd compression for time series; `float32` for signals; YAML for configuration.

## Basis (CALCULATION — assumptions stated so the arithmetic can be checked)

- 30 s runs at 100 Hz → 3,000 samples
- ~48 channels (13 states + 4 controls + 13 measurements + ~13 residuals + ~5 diagnostic outputs)
- `float32` → 3000 × 48 × 4 = **576 kB/run uncompressed**
- Assumed 3× compression on smooth flight-dynamics signals → **~190 kB/run stored**

Across pilot (200), medium (5,000), full dev+val (50,000) and frozen test (10,000) runs, with
derived artefacts (+50%) and repeats (×1.5): **≈ 28 GB total.**

At 28 GB this is a local-disk problem. LFS or object storage would add operational complexity,
failure modes and cost while buying nothing.

## Alternatives considered

- **Git LFS from the start.** Rejected: pushes bulk data into the version-control path for no
  reproducibility gain, since configuration plus seeds already regenerate the data.
- **Cloud object storage.** Rejected: introduces credentials, cost and network dependency at a scale
  that does not need them.
- **float64 storage.** Rejected: precision far below sensor noise (A-INF-01). Verified in EXP-0001
  by comparing float64 and float32 residuals rather than assumed.

## Consequences

Anyone reproducing the work **regenerates** the data rather than downloading it. This makes
determinism verification (A-INF-05) load-bearing rather than a nicety — if simulation is not
bitwise reproducible, the storage strategy fails with it. EXP-0001 therefore checks determinism
before anything else depends on it.

## Revisit if

- Projected storage exceeds **100 GB** (re-forecast after EXP-0005).
- Data must be shared with a collaborator, or published as a benchmark artefact. **Publishing the
  benchmark is a plausible Phase 1d outcome, so this ADR is expected to be reopened.**
- Multiple machines need concurrent access.
