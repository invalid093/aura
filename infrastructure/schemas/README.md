# Schemas

Machine-readable definitions of AURA's provenance records. Validation is enforced by
`infrastructure/validation/` before any confirmatory experiment runs.

| File | Governs | Written to |
|---|---|---|
| `dataset_manifest.schema.json` | Dataset provenance | `data/manifests/DS-XXXX.yaml` |
| `experiment.schema.json` | Experiment registry entries | `experiments/EXP-XXXX.yaml` |
| `run_manifest.schema.json` | Individual run records | alongside each run's output |

---

## Constraints the schemas enforce (not just describe)

These are the rules that would otherwise be honoured only by intention:

- **A raw dataset has no parent; a processed or derived dataset must have one.** This makes the
  provenance chain checkable rather than aspirational — a derived dataset with a dangling parent
  fails validation.
- **A frozen dataset must record its freeze date.** Combined with the checksum manifest, this makes
  post-hoc modification of a frozen test set detectable.
- **A confirmatory experiment must declare its hypothesis, primary metric and analysis plan.** The
  schema refuses an entry that leaves them null, so a confirmatory claim cannot be assembled after
  seeing results.
- **A gate experiment must state its pass criterion in advance.**
- **An `INVALID` experiment must record why, and which conclusions are affected.** Marking something
  invalid without tracing the consequences is not permitted.
- **A `COMPLETED` experiment must record runtime and results location** — so every stage's forecast
  for the next stage is grounded in measurement.
- **Seeds are explicit and per-component.** The run manifest requires `scenario`, `sensor_noise`
  and `init` seeds; there is no field for "global seed", because relying on global RNG state is
  prohibited.
- **`git_dirty: true` is representable.** It is not silently forbidden — it is recorded, and it
  disqualifies the run from a confirmatory claim. Hiding the condition would be worse than logging it.

---

## Units

The dataset manifest requires an explicit `units` string, and angles must state `rad` or `deg`.
Unit ambiguity between an aerodynamic model, an estimator and a fault injector is a mundane and
entirely plausible way to produce a confidently wrong result.
