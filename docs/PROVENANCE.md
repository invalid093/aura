# AURA — Provenance and data management

**Question this document answers:** *where did this number come from, and where does each
kind of file belong?*

---

## The chain

AURA must be able to answer *"where did this number come from?"* completely:

```
result → analysis → experiment → dataset → configuration → model → code version → random seed
```

```bash
python -m aura provenance DEMO-0001 --metric detection_probability
```

```
Provenance for DEMO-0001 (run 8c09e34ae8d3aa13)

  result        <- detection_probability
  experiment    <- DEMO-0001
  specification <- experiments/DEMO-0001/spec.yaml  sha256:00255c940ca336d1
  configuration <- specification  sha256:f5c680578b51c768
  dataset       <- DS-DEMO-0001 @ 1.0
  model         <- threshold-detector @ 1.0
  code          <- ce8a9a6368984318 (dirty=True) framework=0.8.0
  seed          <- base=20260908 labels=['deflection', 'threshold', 'trial']
```

## What is recorded

| Field | Why |
|---|---|
| `experiment_id`, `run_id` | Two runs of one specification are distinguishable while both trace to it |
| `spec_hash` | The pre-registered scientific content; changes if the question, hypothesis, prediction, variables, metrics, gates or precision change |
| `config_hashes` | Text-normalised SHA-256 per configuration file |
| `dataset_versions` | `identifier → version` for every declared dataset |
| `model` | Identifier, version and the declared validity envelope |
| `code.git_commit`, `code.git_dirty` | Which code produced this, and whether the commit alone reproduces it |
| `code.framework_version` | AURA's own version, so a framework change is attributable |
| `environment` | Python version, platform system, platform machine, numpy version |
| `seed_policy` | Scheme, base seed, label fields — sufficient to regenerate every seed |
| `started_utc`, `finished_utc`, `runtime_seconds` | — |
| `notes` | Anything the runner could not do (e.g. a registry status it could not update) |

## What is deliberately **not** recorded

No hostname, no username, no absolute path, no CPU model, no environment variables.

Provenance is published, so it must contain nothing private. Python version and platform
*family* are recorded because they can change floating-point behaviour; anything finer
would leak the machine without aiding reproduction. This is enforced by design in
`aura.provenance.Environment`, and independently checked by the public-release audit.

## Completeness vs certifiability

Two distinct questions, deliberately separated:

- **`missing_links()`** — links that are *always* recordable and are absent (`spec_hash`,
  `model.identifier`). Their absence is a genuine defect ⇒ gate **FAIL**.
- **`code_version_certifiable`** — whether a git commit is available at all. A repository
  exported without `.git` cannot supply one. Absence ⇒ gate **INCONCLUSIVE**, never PASS.

`config_hashes` is excluded from the required links: a specification constructed in memory
has no file to hash, and `spec_hash` already covers its content.

---

## Data hierarchy

| Tier | Contains | Mutability | Default retention |
|---|---|---|---|
| **RAW** | Direct simulator output — trajectories, per-trial records | **Immutable.** Never modified in place. Regeneration means a *new dataset id* | `REGENERABLE` |
| **PROCESSED** | Cleaned, aligned or resampled data derived from RAW by a recorded transformation | Derived; regenerable | `REGENERABLE` |
| **DERIVED** | Compact analysis surfaces — metrics, matrices, the arrays behind figures | Derived; small | `RETAIN-COMPACT` |
| **RESULTS** | The evidence package: metadata, provenance, statistics, gates, report, handoff, checksums | Final | `RETAIN-PERMANENT` |

**Raw data is append-only.** The `raw_data_immutable` gate marks any run that modified a
pre-existing raw artefact as `INVALID`.

Bulk RAW and PROCESSED data is **not committed**. What is published instead: the manifest,
the configuration, the seeds and the reproduction procedure — everything needed to
regenerate it. Compact DERIVED surfaces *are* published when they let a reader reproduce a
figure without re-running the experiment.

## Retention classes

| Class | Meaning | Deletable |
|---|---|---|
| `RETAIN-PERMANENT` | Essential evidence or provenance. Small by construction | never |
| `RETAIN-COMPACT` | Regenerable, but a compact summary must remain | never (the summary) |
| `REGENERABLE` | Large intermediates reproducible from configuration and seeds | after finalisation |
| `TEMPORARY` | Scratch | after finalisation |

`aura.retention.plan_cleanup` returns a **plan** and never deletes anything. Nothing is
eligible until the experiment is finalised — a REGENERABLE artefact is only safe to lose
once the permanent record of how to regenerate it exists.

## The evidence package

One file per question a reader will actually ask:

```
results/<ID>/
├── metadata.json     what ran, when, under what status, was a conclusion emitted
├── provenance.json   the full result → seed chain
├── statistics.json   every measured quantity with its interval
├── gates.json        every gate, its outcome and its evidence
├── validation.json   the preflight specification check
├── report.md         the research report
├── handoff.md        the self-contained independent-review document
└── checksums.txt     sha256 of every file above
```

21.5 kB for `DEMO-0001`. Deliberately small: an evidence package that nobody reads because
it contains four hundred files is not evidence.

Verify at any time:

```bash
python -m aura verify DEMO-0001
```
