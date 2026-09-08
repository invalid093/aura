# Autonomous Uncertainty & Reliability Architecture (AURA)

**Auditable computational research infrastructure for aerospace engineering.**

`RESEARCH BRANCH: TERMINATED` · `RESEARCH-ENGINEERING PLATFORM: ACTIVE`

---

## What it does

AURA is a framework for designing, executing, validating, analysing and documenting
computational research experiments, so that assumptions, failures, uncertainty, provenance
and scientific decisions are **explicit rather than implicit**.

You write a pre-registered specification. AURA validates it before anything runs, executes
it with recorded provenance and deterministic seeds, checks it against automatic validity
gates, computes statistical uncertainty against a precision target you declared in advance,
packages the evidence, and generates a research report and an independent-review handoff.

If a gate rejects the run, AURA marks it `INVALID`, writes a failure record, and **emits no
scientific conclusion** — however good the numbers look.

```bash
python -m aura validate DEMO-0001    # reject a bad specification before computing
python -m aura run      DEMO-0001    # execute with gates, provenance, packaging
python -m aura provenance DEMO-0001  # where did this number come from?
python -m aura verify   DEMO-0001    # is the evidence package unmodified?
python -m aura failures              # what has gone wrong, and what now prevents it
```

Requires Python 3.11+, numpy and PyYAML. Nothing else — no scipy, no pytest.

## Why it exists

Computational engineering projects fail in characteristic ways: undocumented assumptions,
irreproducible runs, uncontrolled parameter changes, test-set contamination, invalid
simulation conditions, poor provenance, silent methodological changes, observations
promoted to conclusions, insufficient statistical power, failed experiments that quietly
disappear, and novelty claimed before the literature was checked.

AURA has a specific mechanism for each. Most of them exist because **this project committed
that failure first** — see the [case study](docs/CASE_STUDY_AURA_RESEARCH_TERMINATION.md).

## Core capabilities

| Capability | Module | Notes |
|---|---|---|
| Experiment registry & pre-registration | `aura.registry`, `aura.spec` | Content-hashed; no silent overwrite; enumerated status transitions each requiring a reason |
| Specification validation | `aura.validation` | Runs before any computation; reports every problem at once |
| Reproducible execution | `aura.runner`, `aura.provenance` | Records code version, config hashes, dataset versions, environment, seed policy |
| Deterministic seeding | `aura.seeds` | `SHA-256(base ‖ labels) mod 2⁶³`; order-independent; no global RNG |
| Monte Carlo | `aura.montecarlo` | Failed trials recorded not dropped; zero surviving samples raises |
| Statistical analysis | `aura.statistics` | Wilson / normal / order-statistic intervals; required-N derived from a declared precision target |
| Validity gates | `aura.gates` | 10 built-in across 4 phases; **a gate that cannot be evaluated raises and never returns PASS** |
| Failure tracking | `aura.failures` | Append-oriented; automatic on rejection; `RESOLVED` requires recorded verification |
| Evidence classification | `aura.evidence` | 7 classes; measured and inferred content kept structurally separate |
| Research reports | `aura.report` | Never converts a number into a conclusion |
| Cross-AI handoffs | `aura.handoff` | Self-contained; ends with *"what should another researcher try to prove wrong?"* |
| Experiment comparison | `aura.compare` | Blocks comparison of scientifically incompatible experiments |
| Retention policy | `aura.retention` | 4 classes over RAW / PROCESSED / DERIVED / RESULTS; plans cleanup, never performs it |

## Demonstrations

Both paths ship with the framework, because a framework that only demonstrates its
successes demonstrates nothing.

**`DEMO-0001` — the passing path.** Monte Carlo recovery of a closed-form detection
probability. All ten gates PASS.

| Quantity | Value |
|---|---|
| Closed form Φ(2.0 − 1.6449) | 0.638760 |
| Monte Carlo (n = 8,851, derived from the precision target) | 0.644221 |
| Absolute error | 0.005461 (target half-width 0.01) |
| 95% CI | [0.63419, 0.65413] — contains the exact value |
| Repeat execution | bit-identical |

**`DEMO-0002` — the failure path.** The same model at an operating point outside its
declared validity envelope. The estimate looks essentially perfect; AURA rejects it anyway.

```
[INVALID] model_validity_envelope (RUNTIME): 1 envelope violation(s);
                                             results must not be interpreted
failure recorded: FAIL-0002
scientific conclusion emitted: False
```

Run both: `python -m aura run DEMO-0001 && python -m aura run DEMO-0002`

## Research case study

Before becoming a framework, AURA was a scientific investigation into uncertainty-aware
fault diagnosis for uncrewed aircraft. Four pre-registered experiments (EXP-0002, EXP-0010,
EXP-0011, EXP-0012) tested whether diagnosis is limited by ambiguity among plausible fault
hypotheses under realistic uncertainty. Each derived a closed-form prediction before
simulating and tested it unrefitted (agreement r = 0.979, 0.9993, 0.973, and 99.3%).

The record includes a flight condition that departed controlled flight while producing the
study's most favourable-looking numbers, two corrections to the project's own published
claims, and a cumulative review that judged the programme substantially goalpost-shifting.

Full history: [`docs/CASE_STUDY_AURA_RESEARCH_TERMINATION.md`](docs/CASE_STUDY_AURA_RESEARCH_TERMINATION.md)

## Scientific outcome

> **The original fault-diagnosis research hypothesis was not supported, and the subsequent
> novelty audit found no defensible novel contribution in the investigated branch.**

At the reference sensor specification, fault isolation was perfect (P_iso = 1.000) — the
motivating ambiguity was absent. Unknown fault magnitude cost 0.0001 at full observation.
The one real failure mode found, confident misdiagnosis when the true fault lies outside
the hypothesis library, turned out to be Berk's 1966 theorem on posterior concentration
under misspecification, detected by the classical FDI residual test, bounded by the
classical minimum detectable fault, with the proposed follow-up experiment already answered
by theorems in the active-fault-diagnosis literature.

`NOVELTY GATE: FAIL` · `EXP-0013: CANCEL` · `ML PHASE: NOT JUSTIFIED`

Audit: [`research/literature/TV-N1_LITERATURE_AUDIT.md`](research/literature/TV-N1_LITERATURE_AUDIT.md)

A failed gate is a valid scientific outcome. It is published here rather than quietly
absorbed, and RQ-1 is retained verbatim with a dated status note rather than rewritten to
match the result.

## Engineering outcome

What was built despite — and partly because of — the scientific termination:

- a 21-module framework with a clean CLI and no dependency beyond numpy and PyYAML;
- 82 tests running on the standard library alone, including regression tests derived from
  real research failures;
- ten validity gates, each traceable to a specific way research goes wrong;
- an evidence-package format small enough that people actually read it (21.5 kB, 8 files);
- documentation answering practical questions rather than describing structure.

Every major research failure in the historical record is now an engineering test:

| Research failure | Now prevented by |
|---|---|
| A flight condition that departed controlled flight while looking best (FAIL-0001) | `model_validity_envelope` gate + 3 tests + `DEMO-0002` |
| A silent patch that left nine duplicate templates | `assert_distinct`, `assert_patch_applied` |
| A label claiming 72 runs while 90 were checked | `assert_reported_n`, `data_completeness` gate |
| A timestep that did not divide the sample interval | `assert_divides`, `numerical_validity` gate |
| Comparing cases with differently-shaped hypothesis sets | `assert_symmetric_sets`, `aura compare` |

Two bugs in the framework itself were found by its own tests during this conversion and are
recorded in the failure registry rather than quietly fixed.

## Status

| Track | Status |
|---|---|
| **Research branch** (RQ-1, aircraft fault diagnosis) | **`TERMINATED`** — premise unsupported, novelty gate FAIL, EXP-0013 cancelled, ML not justified |
| **Research-engineering platform** | **`ACTIVE`** — M0–M6 complete; 82 tests passing |

The historical research record is preserved unedited. It is not rewritten to make the
platform look successful; the sequence *hypothesis → experiment → falsification → audit →
termination* is the evidence for the methodology.

## Reproducibility

```bash
python -m unittest discover -s tests -t .   # 82 tests
python -m aura run DEMO-0001                # ~0.8 s
python -m aura verify DEMO-0001             # checksum every artefact
```

- **Deterministic experiments** are expected to be bit-identical; the `reproducibility`
  gate asserts exact equality.
- **Stochastic experiments** require deterministic seed generation, recorded seeds,
  reproducible aggregation, and a documented tolerance.
- **Cross-platform bitwise identity is not claimed**; python, platform and numpy versions
  are recorded so a difference can be attributed.

Details: [`docs/REPRODUCIBILITY.md`](docs/REPRODUCIBILITY.md)

## Documentation

| Document | Answers |
|---|---|
| [Research engineering mission](docs/RESEARCH_ENGINEERING_MISSION.md) | Why AURA exists now; non-goals; roadmap; completion criteria |
| [Architecture](docs/ARCHITECTURE.md) | What the pieces are and why |
| [Experiment schema](docs/EXPERIMENT_SCHEMA.md) | What goes in `spec.yaml`, and why each field is required |
| [Research workflow](docs/RESEARCH_WORKFLOW.md) | Step by step, from question to reviewed result |
| [Validity gates](docs/VALIDITY_GATES.md) | What is checked automatically, and what each outcome means |
| [Monte Carlo](docs/MONTE_CARLO.md) | Running trials; how many; what the intervals mean |
| [Provenance](docs/PROVENANCE.md) | Where a number came from; where each file belongs |
| [Reproducibility](docs/REPRODUCIBILITY.md) | What is promised, and what is explicitly not |
| [Failure management](docs/FAILURE_MANAGEMENT.md) | What happens when things go wrong |
| [Case study](docs/CASE_STUDY_AURA_RESEARCH_TERMINATION.md) | How the research branch ended, and what it taught the framework |

## What AURA does not claim

- It is **not** a novel aircraft fault-diagnosis method.
- It is **not** an ML-based uncertainty-aware health-management system. There is no ML in
  it, by design.
- It does **not** demonstrate safe autonomous aircraft operation, and makes no claim of
  real-aircraft, operational, or safety-certification applicability.
- The aircraft model (GFW-1) is self-implemented and has never been validated against
  flight data (TV-D10). It is a historical artefact and a realistic workload, not a
  validated aerospace model.

## Licence

**None.** No licence has been applied. All rights reserved by the author; this repository
is published as a research record, not as reusable software. Contact the author before
reuse.
