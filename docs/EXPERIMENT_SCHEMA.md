# AURA — Experiment specification schema

**Question this document answers:** *what goes in `spec.yaml`, and why is each field
required?*

Every required field below exists because its absence caused a concrete problem in the
EXP-0002 → EXP-0012 research record. The schema was derived from that record, not
designed in the abstract.

Validate a specification with `python -m aura validate <ID>`. Validation runs **before any
computation**: an invalid specification never reaches a simulator.

---

## Minimal complete example

```yaml
experiment_id: DEMO-0001
title: Monte Carlo recovery of a closed-form detection probability
kind: infrastructure            # exploratory | confirmatory | calibration | infrastructure

research_question: Does the AURA Monte Carlo and statistics pipeline recover a known
  closed-form probability to its declared precision?
hypothesis: A Monte Carlo estimate produced by this framework agrees with the exact
  closed-form value Phi(d - z) to within the pre-declared statistical precision.
prediction: 'With d = 2.0 and z = 1.6449 the exact value is 0.63875. The estimate will
  lie within the declared half-width of 0.01, and the 95% CI will contain it.'

variables:
  independent: {deflection: 2.0}
  dependent: [detection_probability]
  controlled: {threshold: 1.6448536269514722, noise_variance: 1.0, estimator: proportion}

metrics: [detection_probability, absolute_error_vs_closed_form]

model:
  identifier: threshold-detector
  version: '1.0'
  validity_envelope:
    deflection: [0.0, 6.0]

datasets:
  - {identifier: DS-DEMO-0001, version: '1.0', role: output}

assumptions:
  - Trials are independent and identically distributed.
  - The detector statistic is exactly Gaussian with unit variance.

randomisation:
  enabled: true
  base_seed: 20260908
  label_fields: [deflection, threshold, trial]

statistical_precision:
  metric: proportion            # proportion | mean
  confidence: 0.95
  half_width: 0.01
  planning_value: 0.64

frozen_test:
  enabled: false

gates: [provenance_complete, seed_policy_declared, model_validity_envelope,
        numerical_validity, data_completeness, reproducibility, statistical_precision,
        convergence]

output_dir: results/DEMO-0001
status: PLANNED
```

---

## Field reference

### Identity

| Field | Required | Rule | Rationale |
|---|---|---|---|
| `experiment_id` | yes | `EXP-####` or `DEMO-####` | `DEMO-` is reserved for framework demonstrations so they can never be mistaken for research results |
| `title` | yes | non-empty | — |
| `kind` | yes | one of the four kinds | `confirmatory` additionally *requires* a frozen-test declaration |
| `status` | no | a valid `Status` | Lifecycle metadata; **excluded from the content hash** |

### Scientific content

| Field | Required | Rule | Rationale |
|---|---|---|---|
| `research_question` | yes | ≥ 15 characters | — |
| `hypothesis` | yes | ≥ 15 characters | A specification without one cannot be falsified |
| `prediction` | yes | ≥ 15 characters | Pre-registration only means something if the expected outcome is written *before* the run |
| `metrics` | yes | non-empty, unique | Duplicates indicate a copy-paste error that would double-count |
| `assumptions` | yes | **non-empty list** | Results are rendered as conditional on these. An empty list is rejected: every computational experiment assumes something |

The length floors are crude but catch the real failure — `hypothesis: TBD`.

### Variables

| Field | Required | Rationale |
|---|---|---|
| `variables.dependent` | yes | At least one measured quantity must be named |
| `variables.independent` | warning if absent | A fixed-point run is legitimate but unusual |
| `variables.controlled` | warning if absent | **An undeclared control is untraceable later.** This is what makes `aura compare` able to detect incommensurable experiments |

### Model

| Field | Required | Rationale |
|---|---|---|
| `model.identifier`, `model.version` | yes | Provenance and comparability both depend on them |
| `model.validity_envelope` | **error** for exploratory/confirmatory; warning otherwise | Direct descendant of **FAIL-0001**. Each entry is `name: [min, max]` and is checked at runtime against reported observations. Numbers from outside a declared envelope are not evidence |

### Datasets

`identifier`, `version` and `role` (`input`/`output`) are required per entry; identifiers
must be unique. Versions are required because "which version of DS-0002?" is unanswerable
six months later otherwise.

### Randomisation

| Field | Rule |
|---|---|
| `enabled` | — |
| `base_seed` | integer, **required when enabled** |
| `label_fields` | non-empty, **required when enabled** |
| `repetitions` | ≥ 1 if present |

`base_seed` plus `label_fields` fully determines every per-cell seed through
[`aura.seeds`](MONTE_CARLO.md#seed-derivation), so seeds need not be stored individually
for large sweeps. Global RNG state is never used.

### Statistical precision

| Field | Rule |
|---|---|
| `metric` | `proportion` or `mean` |
| `confidence` | strictly in (0, 1) |
| `half_width` | positive |
| `planning_value` | proportion in [0,1] for `proportion`; positive σ for `mean` |

A precision target **requires randomisation to be enabled** — a deterministic experiment
has no sampling error to bound. Its absence on a stochastic experiment is a warning:
*"N is then an unjustified choice"*. The sample size is derived from this block, not typed
by hand.

### Frozen test

`enabled` must be stated. When enabled, `path` must exist and `checksum_file` is
required — integrity cannot be asserted without a recorded checksum. A `confirmatory`
experiment without a frozen-test declaration is rejected.

### Gates and outputs

`gates` must be non-empty, contain no duplicates, and name only registered gates
(`python -m aura gates`). A typo is an error, not a silently skipped check.

`output_dir` must be repository-relative (no absolute or machine-specific paths), must not
escape the root, and must not already exist non-empty — the framework refuses to overwrite
a previous experiment's evidence package unless explicitly told to.

---

## Content hash

`ExperimentSpec.content_hash` is the SHA-256 of the specification's *scientific content*,
excluding `status` and `source_path`. It is recorded in provenance and in
`metadata.json`, so a changed pre-registration is detectable rather than deniable.

## Validation severities

- **ERROR** blocks execution.
- **WARNING** is recorded in `validation.json` and the run proceeds.

`python -m aura validate <ID>` exits 0 when valid, 1 when rejected, and lists *every*
problem at once rather than stopping at the first — fixing a specification one error per
run is how researchers stop reading error messages.
