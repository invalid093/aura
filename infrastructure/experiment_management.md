# Experiment Management

**Date:** 2026-09-08

---

## 1. Experiment registry

Single source of truth: `experiments/REGISTRY.md` (human-readable index) backed by one YAML file
per experiment at `experiments/EXP-XXXX.yaml`.

**A registry entry is created with status `PLANNED` *before* the experiment runs.** An experiment
that appears in the registry only after it produced a good result is not evidence.

```yaml
experiment_id: EXP-0005
title: Pilot - diagnosis difficulty calibration
hypothesis: null            # pilot; no hypothesis under test
purpose: >
  Establish that in-distribution isolation accuracy lies between 20% and 99%,
  so the main experiment can discriminate between methods.
type: exploratory           # exploratory | confirmatory
status: PLANNED
configuration: infrastructure/configuration/exp0005_pilot.yaml
configuration_sha256: <sha>
git_commit: <sha>
dataset_ids: [DS-0004]
random_seeds: [1001..1030]
parameters:
  n_runs: 200
  methods: [B0, B1, AURA]
date_planned: 2026-09-20
date_started: null
date_completed: null
results_location: results/exploratory/EXP-0005/
analysis_version: null
runtime_seconds: null
storage_bytes: null
supersedes: null
superseded_by: null
notes: ""
```

### Allowed statuses

| Status | Meaning |
|---|---|
| `PLANNED` | Registered, not run |
| `RUNNING` | In progress |
| `COMPLETED` | Finished; results valid |
| `FAILED` | Did not complete (see linked `FAIL-####`) |
| `INVALID` | Completed but scientifically invalid (e.g. leakage found afterwards) |
| `SUPERSEDED` | Replaced by a later experiment; retained |
| `ARCHIVED` | Moved to `archive/experiments/` |

**Nothing is deleted.** `INVALID` and `FAILED` entries stay, with reasons.

---

## 2. Confirmatory vs exploratory

Every experiment declares `type`. The rules differ:

- **Exploratory** — may iterate freely. Results **may not** be cited as evidence for a hypothesis.
- **Confirmatory** — hypothesis, metric, threshold and analysis plan are fixed in the YAML *before*
  the run, and the file is committed before execution. There is exactly **one primary confirmatory
  experiment** (H1 at shift axis S6, EXP-0007).

Converting an exploratory result into a confirmatory claim after the fact is prohibited.

---

## 3. Test-set access log

Because test-set reuse is the highest-severity integrity risk (TV-S1), every evaluation against a
frozen dataset is appended to `experiments/TEST_SET_ACCESS_LOG.md`:

| Date | Dataset | Method + version | Experiment | Result recorded? | Notes |
|---|---|---|---|---|---|

The log is append-only. Entries are added **regardless of whether the result was welcome.** A
method version evaluated twice against the same frozen set must be justified in the notes.

---

## 4. Failure records

`FAIL-0001`, `FAIL-0002`, … in `experiments/failures/FAIL-XXXX.md`:

```markdown
# FAIL-0003
- What failed:
- When (date, experiment ID, commit):
- Why (root cause, if known):
- Category: SOFTWARE | NUMERICAL | EXPERIMENTAL_INVALIDITY | SCIENTIFIC_NEGATIVE_RESULT
- Scientific impact:
- Are any prior conclusions affected? (list experiment IDs)
- Methodological implication:
- Resolution:
```

### The four categories, kept distinct

| Category | Meaning | Is it evidence? |
|---|---|---|
| **Software failure** | The implementation was wrong | No — fix and rerun |
| **Numerical failure** | The computation was unstable or invalid | No — but may indicate a modelling problem |
| **Experimental invalidity** | The experiment was not a valid test (leakage, contamination, mis-specified control) | No — and any conclusion drawn from it must be retracted |
| **Scientific negative result** | The experiment was valid; the hypothesis was unsupported | **Yes. This is research evidence and is reported.** |

Conflating the fourth category with the first three is how negative results get buried. It is
explicitly prohibited.

---

## 5. Staged escalation

No experiment scales up until the previous stage passes its gate
(`reports/phase0/EXPERIMENTAL_DESIGN_PRELIMINARY.md` §9):

```
Small test → runtime estimate → storage estimate → output verification
  → fault-injection verification → metric verification → reproducibility check
  → pilot → medium → full
```

Every stage records `runtime_seconds`, `storage_bytes`, `n_runs` so the forecast for the next stage
is grounded in measurement rather than assumption.

---

## 6. Archiving

Material moves to `archive/` when superseded, retaining: original ID, provenance, reason for
archival, date, and a pointer to the replacement work. An archive is a record, not a bin.

**Scientifically meaningful failed experiments are never deleted** because they produced poor
results.
