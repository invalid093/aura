# data/

Four layers. See `infrastructure/data_management.md` for the full policy.

| Directory | Layer | Mutable | In Git |
|---|---|---|---|
| `raw/` | Immutable source evidence: external datasets as downloaded, raw simulation output | **Never** | No |
| `processed/` | Transformations of raw (resampling, alignment, splits) | Regenerable | No |
| `derived/` | Residuals, features, labels, state estimates, uncertainty estimates, model outputs | Regenerable | No |
| `manifests/` | Dataset manifests, checksums, external-source records | Append-only | **Yes** |

## Rules

- `raw/` is append-only. Raw data is never overwritten or edited in place.
- Regeneration under materially different conditions means a **new dataset ID**, not a reused one.
- A dataset whose `parent_dataset` chain does not resolve back to RAW may not be used in a
  reported result.
- Datasets marked `frozen: true` may not be regenerated at all.
- Bulk data is deliberately absent from Git. **The manifests are the record of how it was made;
  the disk holds the data.** A clone of this repository plus the configurations and seeds should
  reproduce the data rather than download it.

## Dataset IDs

`DS-0001`, `DS-0002`, … Each has `manifests/DS-XXXX.yaml` and `manifests/DS-XXXX.sha256`.

No datasets exist yet — Phase 1 creates the first.
