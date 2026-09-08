# AURA — Research Engineering Mission

**Status:** active · **Date:** 2026-09-08 · **Supersedes:** the original scientific mission,
terminated after the TV-N1 novelty gate returned FAIL.

---

## Mission

> **AURA is a reproducible and auditable computational research framework for designing,
> executing, validating, analysing and documenting aerospace engineering experiments.**

AURA exists to demonstrate that computational research can be treated as an *engineered
system* rather than a collection of scripts: with explicit assumptions, versioned
configurations, reproducible execution, deterministic seed control, automated validity
gates, statistical analysis, provenance, failure tracking, evidence classification,
experiment registries, research reports, independent-review handoffs, and explicit
termination decisions.

## Why AURA exists *now*

AURA began as a scientific investigation into uncertainty-aware fault diagnosis for
uncrewed aircraft. That branch is closed:

| Gate | Outcome |
|---|---|
| RQ-1 (evidential ambiguity vs competence loss) | **Unsupported** |
| TV-N1 (blocking novelty audit) | **FAIL** |
| EXP-0013 (excitation) | **Cancelled** — solved in the literature |
| ML phase | **Not justified** |

The scientific result was negative. The *engineering* result was not. Over four
experiments the project accumulated a working apparatus for keeping computational
research honest — pre-registration, closed-form predictions tested unrefitted, validity
gates, failure records, evidence classification, handoffs — and repeatedly used it to
catch its own errors, including two corrections to its own published claims.

That apparatus is the contribution. AURA is now the framework, and the terminated
research branch is its most informative test case.

## The problem AURA addresses

Computational engineering projects fail in characteristic, well-documented ways. Each
row below is a failure AURA has an explicit mechanism for — and most are failures this
project actually committed before building the mechanism.

| Failure mode | AURA's response | Did AURA commit it? |
|---|---|---|
| Undocumented assumptions | `assumptions` is a required specification field; validation rejects an empty list; every report renders results as *conditional on* them | Partly — assumptions existed but were scattered |
| Irreproducible experiments | Provenance records code version, config hashes, dataset versions, environment and seed policy; `aura verify` re-checks the package | — |
| Uncontrolled parameter changes | The specification is content-hashed; any change to question, hypothesis, prediction, variables, metrics, gates or precision changes the hash | — |
| Accidental test-set contamination | `frozen_test` must be declared; a confirmatory experiment cannot omit it; integrity is checked by checksum before the run | — |
| Invalid simulation conditions | `model_validity_envelope` gate marks out-of-envelope runs `INVALID` and emits **no** conclusion | **Yes — FAIL-0001** |
| Poor provenance | `aura provenance <ID>` walks result → analysis → experiment → dataset → configuration → model → code → seed | — |
| Silent methodological changes | Status transitions are enumerated and require a recorded reason; `assert_patch_applied` refuses a no-op edit | **Yes** — a silent patch produced nine duplicate templates |
| Confusing observations with conclusions | Seven evidence classes; the report generator *structurally* separates measured from inferred and refuses researcher-supplied measured claims | **Yes** — recurring editorial risk |
| Insufficient statistical power | A precision target is declared; N is *derived* from it; achieved precision is measured and reported | — |
| Disappearing failed experiments | Failure registry is append-oriented; a rejected run writes a record automatically; `SUPERSEDED`/`INVALID` entries are never deleted | — |
| Premature novelty claims | TV-N1 was declared a blocking gate — and the project ran past it four times before closing it, which is exactly why it is now documented as a gate rather than an intention | **Yes — the central failure** |

**`INTERPRETATION`** The last row is the most important. AURA's own worst process failure
was running four experiments past a gate it had itself declared blocking. A framework
built by someone who has not made that mistake would probably not treat gates as
unconditional.

## Non-goals

AURA is **not**, and is not intended to become:

- a production aircraft health-management system;
- a novel fault detection and isolation algorithm;
- a machine-learning platform (ML is out of scope; AURA may one day *host* an ML
  experiment as a generic experiment type, but it does not require or contain one);
- a flight-control system;
- a safety-certification framework;
- evidence of safe autonomous aircraft operation.

The aircraft model in this repository (GFW-1) is a self-implemented simulation that has
never been cross-validated against flight data (TV-D10). It is retained as the historical
research record and as a realistic workload, not as a validated aerospace artefact.

## Maturity roadmap

| Stage | Content | Status |
|---|---|---|
| **M0** | Existing research infrastructure: registry YAMLs, FAIL records, manifests, handoff practice, evidence classes | **Complete** (inherited) |
| **M1** | Reproducible experiment engine: schema, registry, execution, provenance | **Complete** — `aura.spec`, `aura.registry`, `aura.runner`, `aura.provenance` |
| **M2** | Automated validation: preflight / runtime / post / statistical gates | **Complete** — `aura.validation`, `aura.gates` (10 gates) |
| **M3** | Statistical experimentation: Monte Carlo, precision, convergence | **Complete** — `aura.montecarlo`, `aura.statistics` |
| **M4** | Evidence packaging: reports, provenance, handoffs | **Complete** — `aura.report`, `aura.handoff`, `aura.runner.finalise` |
| **M5** | Demonstration: one successful and one deliberately failed experiment | **Complete** — `DEMO-0001`, `DEMO-0002` |
| **M6** | Portfolio release: documentation, tests, architecture, case study | **Complete** — 82 tests, 8 architecture documents, termination case study |

## Completion criteria

AURA is complete as a portfolio project when a new researcher can do all twelve of the
following. Each links to the mechanism that provides it.

1. **Define an experiment** — `experiments/<ID>/spec.yaml` ([schema](EXPERIMENT_SCHEMA.md))
2. **Pre-register it** — `Registry.register`, content-hashed, no silent overwrite
3. **Validate the specification** — `aura validate <ID>`, fails *before* any computation
4. **Execute it reproducibly** — `aura run <ID>`, provenance captured automatically
5. **Run stochastic trials** — `aura.montecarlo`, deterministic per-cell seeds
6. **Detect invalid conditions** — 10 registered gates ([reference](VALIDITY_GATES.md))
7. **Calculate statistical uncertainty** — Wilson / normal / order-statistic intervals
8. **Preserve provenance** — `aura provenance <ID>` ([reference](PROVENANCE.md))
9. **Record failures** — `aura failures` ([reference](FAILURE_MANAGEMENT.md))
10. **Generate a research report** — `report.md`, never converting a number into a conclusion
11. **Generate an independent-review handoff** — `handoff.md`, self-contained and adversarial
12. **Reproduce the result** — from the recorded configuration, verified by `aura verify <ID>`

Both paths are demonstrated:

- **PASS** — `DEMO-0001` runs, passes all ten gates, and recovers a known closed-form
  probability to within its declared precision.
- **FAIL** — `DEMO-0002` is rejected automatically for a known, documented reason, is
  marked `INVALID`, writes `FAIL-0002`, and emits **no** scientific conclusion.

## The governing principle

> **Do not optimise AURA for how impressive it sounds. Optimise it for whether another
> aerospace researcher could actually trust and reuse it.**

The strongest claim this project can make is not that it built a sophisticated aircraft
diagnostic. It is that it built infrastructure which forces computational research to be
reproducible, auditable and statistically defensible — and which is willing to say *"this
experiment was invalid"* and *"this hypothesis is not novel"*.

The termination of the original research branch is part of the evidence for that claim,
not a caveat to it.
