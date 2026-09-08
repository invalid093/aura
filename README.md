# AURA

**Autonomous Uncertainty & Reliability Architecture**

> Independent computational research into uncertainty-aware fault diagnosis and autonomous health
> management for high-performance uncrewed aircraft.

**AURA is an ongoing independent research project.** It is at Phase 0. **There are no validated
scientific results yet.** Everything in this repository is definition, design and reasoning — not
findings.

---

## What AURA is investigating

An autonomous aircraft that detects a fault must decide what to do about it. That decision depends
on how much it can trust its own diagnosis — and there are two structurally different reasons a
diagnosis might not be trustworthy:

- **Evidential ambiguity.** Two or more fault hypotheses explain the measurements equally well. The
  information is not present in the available sensors at this flight condition. More confidence
  would not help.
- **Competence loss.** The flight condition has moved outside the envelope the diagnostic system was
  developed for, so its outputs are unreliable even when they look clean.

These call for **opposite responses**. Ambiguity means acting on what the candidate hypotheses
share — escalating would hand a human no more information than the aircraft has. Competence loss
means escalating or degrading, because a confident-looking answer is exactly the dangerous case.

A single scalar confidence score cannot tell them apart. Whether separating them actually changes
what an aircraft does is the research question.

## Why the problem matters

Air data sensor faults — pitot blockage, static obstruction, angle-of-attack vane sticking — are a
documented, physically-modelled failure class that has caused transport-category accidents. Run-time
assurance (ASTM F3269) is the standardised architecture for bounding functions that cannot be
conventionally verified: it switches control based on a monitor's output. That architecture assumes
the monitor is trustworthy. **The reliability of the monitor under conditions it was not developed
for is the assumption nobody has tested.**

A false escalation costs mission capability. An unsafe continuation costs the aircraft. The
distinction is where the safety value sits, and it is where a scalar confidence is weakest.

---

## Current research question

> **When an autonomous aircraft's operating regime departs from the conditions under which its
> diagnostic system was developed, does representing evidential ambiguity separately from
> competence loss produce better act / abstain / escalate decisions than a single scalar
> confidence — and does that separation survive when regime shift and fault onset occur
> simultaneously?**

Full statement and definitions: [`docs/research_question.md`](docs/research_question.md)
Hypotheses and falsification criteria: [`docs/hypotheses.md`](docs/hypotheses.md)

The project's original framing — *"how can an autonomous aircraft detect, isolate and respond to
degradation when human intervention is unavailable?"* — was assessed as **not testable**: it
contained at least four separable research programmes, specified no comparison, and had no
falsification condition. Replacing it is recorded in
[`ADR-0002`](docs/decisions/ADR-0002-research-question.md).

## Current research status

**Phase 0 complete (2026-09-08). Phase 1 not started.**

| Phase | Content | Status |
|---|---|---|
| 0 | Reconnaissance, scientific definition, infrastructure | **Complete** |
| 1a | **Gates:** systematic literature search; licence verification; runtime measurement; **structural isolability** | Not started |
| 1b | Simulation, fault injection, estimator, residuals, baselines | Blocked on 1a |
| 1c | Pilot → medium → frozen test | Blocked on 1b |
| 1d | External validity check, sensitivity analyses, reporting | Blocked on 1c |
| 2 | Only if Phase 1 findings warrant it | — |

Experiments run: **0.** Datasets generated: **0.**

Each Phase 1a gate is cheap and each can end the project. The decisive one is **EXP-0002**: whether
structural isolability actually varies with flight condition for this model and fault set. If it
does not, the ambiguity component loses its ground truth and the design must change. No learning
code is written before it passes.

## Validated findings

**None.** No experiment has been run. This section will be populated only with results that have
passed the confirmatory protocol in [`docs/methodology.md`](docs/methodology.md), and each will cite
its experiment ID, dataset ID and configuration.

## Preliminary findings

**None from experiment.** The following are *reconnaissance observations* from Phase 0 literature
work — they characterise the state of the field, not AURA's results, and rest on abstract-level
reading of most sources:

- The uncertainty-quantification-under-distribution-shift literature is mature but concentrated in
  rotating machinery. It has not been transferred to flight dynamics with a state estimator in the
  loop.
- Recent machine-learning aircraft fault-diagnosis papers report accuracy only, in-distribution,
  with a forced single-class output — no calibration, no abstention, no shift protocol.
- Classical multiple-model / Kalman-filter-bank diagnosers produce a principled fault posterior
  with a known lock-in failure mode, but no retrieved source evaluates that posterior as a
  *calibrated* probability.
- Structural diagnosability analysis is used at design time and, as far as this reconnaissance
  found, never as ground truth for evaluating a learned uncertainty estimate.

Full synthesis: [`reports/phase0/LITERATURE_REVIEW.md`](reports/phase0/LITERATURE_REVIEW.md)

## Why this might not work

There is direct published evidence against AURA's central hypothesis. A 2026 study of
confidence-gated robot autonomy compared seven uncertainty estimators and found their act/defer
decisions agreed more than 97.8% of the time; the *threshold* dominated, not the estimator, and
out-of-distribution detection performed near chance.

AURA's stated reason for expecting a different outcome is that its two components read
*structurally different evidence* — ambiguity from residual likelihood structure, competence loss
from operating-point position — rather than being transformations of the same softmax output.

**That is an argument, not a result.** It has been adopted as the falsification condition rather
than argued around. If the equivalence reproduces, that is the finding, and it would be a stronger
and more general result than the original.

**Stated in advance: the most likely outcome is that the primary hypothesis is falsified and the
secondary one supported.** The design is built so that combination is a publishable result.

## Open questions

1. Does structural isolability actually vary with flight condition for this model, sensor suite and
   fault set? **If not, the design fails.** (EXP-0002)
2. Does a systematic database search close the identified gaps?
3. Are the candidate model, toolbox and dataset licences suitable for research use?
4. Should evidential ambiguity be defined over fault modes, or fault modes plus magnitude?
5. Is expected decision cost the right primary metric, or should the decision layer be evaluated
   another way?

## Known limitations

Twenty-three threats to validity are catalogued in
[`reports/phase0/THREATS_TO_VALIDITY.md`](reports/phase0/THREATS_TO_VALIDITY.md). **Three are
unmitigated:**

- **Novelty is unverified.** The gap analysis rests on a non-systematic, search-engine-mediated
  review. Absence of evidence is not evidence of absence. A systematic database search is a hard
  gate before any novelty claim.
- **Residual simulation bias.** Even the strongest out-of-distribution axis stays within one
  aerodynamic data lineage. Whether real sensor faults resemble the injected fault models is not
  verifiable within scope.
- **Single airframe, single sensor suite, seven fault modes.**

Further, of 70 indexed literature sources, **only 3 were read in full**. The literature index records
the verification level of every entry, and sources with unconfirmed authorship are marked as such
rather than being given plausible-looking citations.

---

## Research philosophy

> Maximise scientific information gained per unit of computation, time, storage and researcher
> attention.

- More simulations, more algorithms and more plots do not automatically produce better research.
- Model fidelity is a cost. AURA needs *analysable* equations, not accurate ones.
- A negative result is a result, and is reported with the same prominence as a positive one.
- Nothing is claimed beyond what the evidence supports.

## Conceptual architecture

```
                     Aircraft sensors (13 channels)
                                │
                        State estimation  ──────►  Σx
                                │
                        Residual generation
                                │
                ┌───────────────┴───────────────┐
                ▼                               ▼
   Evidential ambiguity  A              Competence loss  N
   (which hypotheses are            (is this operating point
    indistinguishable here?)         outside development?)
                └───────────────┬───────────────┘
                                ▼
                        Decision policy
                                │
        ┌───────────────┬───────┴────────┬──────────────────┐
        ▼               ▼                ▼                  ▼
    CONTINUE      Act on set      DEGRADED MODE        ESCALATE
                  intersection
```

Ground truth for ambiguity comes from structural isolability analysis computed per flight
condition. This is unusual: uncertainty research rarely has an analytic reference for what the
uncertainty *should* be.

## Repository structure

```
docs/            Research question, hypotheses, assumptions, scope, methodology, decisions (ADRs)
research/        Reconnaissance log, literature index, gap matrix, candidate questions, research log
infrastructure/  Data management, experiment management, reproducibility, reporting, schemas
aircraft/ sensors/ faults/ estimation/ diagnosis/ autonomy/ simulation/   (implementation, Phase 1)
experiments/     Experiment registry, frozen-test-set access log, failure records
analysis/ visualization/
data/            raw / processed / derived / manifests   (bulk data not published — see below)
results/         exploratory / validation / final / figures
reports/         phase0 / technical / research
handoffs/        Self-contained reports written for independent critical review
archive/         Superseded and retired work, retained with provenance
tests/
```

## Reproducibility

Parameters live in version-controlled configuration, not in code. Every run records its commit,
configuration hash, dataset IDs, per-component seeds, environment lockfile and runtime. Determinism
is *verified*, not assumed. Figures are generated by committed scripts and never hand-edited.

The frozen test set is generated once, hashed and committed before any method is trained. Every
evaluation against it is logged — welcome or not.

See [`infrastructure/reproducibility.md`](infrastructure/reproducibility.md).

## Data policy

This repository publishes **the scientific record, not the entire laboratory**. It contains dataset
descriptions, IDs, manifests, provenance, checksums, generation procedures and configurations —
the recipe and the evidence — rather than bulk simulation output. Projected raw data is ~28 GB and
regenerable from committed configurations and seeds.

Small datasets are published only where they are necessary to reproduce a central figure, cannot
reasonably be regenerated, or constitute a benchmark artefact.

See [`infrastructure/data_management.md`](infrastructure/data_management.md).

## Scope and limits

Simulation-based. The aircraft model is a *representative* nonlinear high-performance aircraft built
from 1979 public NASA wind-tunnel data — **no result licenses any claim about a real F-16**
(assumption A-SIM-01). All sources are public and unclassified. Defence relevance is not treated as
a research contribution.

What is deliberately **not** being built, and why, is in [`docs/scope.md`](docs/scope.md).

## Licensing

**Not yet determined.** No licence is offered at this stage, so no permission to reuse this code,
data or documentation should be inferred. Source-code, dataset and documentation licensing will be
decided deliberately at a later phase — see
[`ADR-0006`](docs/decisions/ADR-0006-licensing-deferred.md).

External datasets, models and code retain their own licences, recorded in
[`data/manifests/EXTERNAL_SOURCES.md`](data/manifests/EXTERNAL_SOURCES.md). No external artefact is
adopted before its licence is verified.

---

## Reading order for a new reader

1. This README.
2. [`FINDINGS.md`](FINDINGS.md) — one-page current state.
3. [`reports/phase0/PHASE0_RESEARCH_REPORT.md`](reports/phase0/PHASE0_RESEARCH_REPORT.md) — the full
   Phase 0 argument, including whether AURA is worth building.
4. [`reports/phase0/THREATS_TO_VALIDITY.md`](reports/phase0/THREATS_TO_VALIDITY.md) — read this
   before believing anything above.
