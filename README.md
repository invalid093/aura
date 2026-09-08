# AURA

**Autonomous Uncertainty & Reliability Architecture**

> Independent computational research into uncertainty-aware fault diagnosis and autonomous health
> management for high-performance uncrewed aircraft.

**AURA is an ongoing independent research project.** Phase 0 is complete and two experiments have
run. There are **two validated results**, and **no result yet bearing on the central hypothesis**,
which remains untested. The most recent result **weakens one of the project's own premises** — see
Validated findings.

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

**Phase 0 complete. EXP-0002 (the design gate) complete and PASSED — with qualifications.**

| Phase | Content | Status |
|---|---|---|
| 0 | Reconnaissance, scientific definition, infrastructure | **Complete** |
| 1a | **Gates:** licence verification ✔ (GPL-3.0, [ADR-0007](docs/decisions/ADR-0007-aircraft-model-licence-substitution.md)); runtime measurement ✔; **EXP-0002 distinguishability ✔ PASS**; systematic literature search — **still outstanding** | Mostly complete |
| 1b | Simulation, fault injection, estimator, residuals, baselines | Blocked on EXP-0010 |
| 1c | Pilot → medium → frozen test | Blocked on 1b |
| 1d | External validity check, sensitivity analyses, reporting | Blocked on 1c |
| 2 | Only if Phase 1 findings warrant it | — |

Experiments run: **2** (EXP-0002: 90 simulation runs + 5 sensitivity sweeps; EXP-0010: 130 M
classification trials reusing the same trajectories). Datasets: **1** (DS-0001, regenerable, not
published — see Data policy).

EXP-0002 asked whether fault distinguishability varies with flight condition — it does, modestly.
EXP-0010 then asked whether that survives measurement uncertainty, and found that **at realistic
sensor noise there is no ambiguity to be uncertain about at all**. No learning component, uncertainty
estimator or decision layer is built until two remaining assumptions are relaxed, because both can
only increase ambiguity and either could restore the motivation on evidence rather than assumption.

## Validated findings

**Two.** The more recent one is uncomfortable for the project, and is stated first.

### [EXP-0010](reports/technical/EXP-0010_MEASUREMENT_UNCERTAINTY.md) — measurement uncertainty

- **At the reference sensor specification, fault isolation is perfect.** Probability of correct
  18-way isolation is **1.000** at every valid flight condition, with **zero** of 153 pairs
  practically ambiguous. EXP-0002's five-member ambiguity group dissolves — its per-sample threshold
  was conservative by a factor of sqrt(K*N) ~ 153.
- **But isolation takes about 5 seconds.** Even with perfect sensors, P_iso = 0.45 at 0.05 s and does
  not reach 0.95 until ~5 s. **The binding constraint is time, not noise.** None of the five
  pre-declared decision-gate outcomes anticipated this.
- Ambiguity requires 10-19x the reference uncertainty to appear. Condition dependence is real but
  modest (1.83x spread, fixed ordering, robust to fault magnitude).
- Temporally correlated noise costs a further 21% — *quantitatively* predicted by
  sqrt((1+rho)/(1-rho)) at r = 0.9993, so it is a limitation with a correction rather than an unknown.
- **Every probability is an upper bound**: the classifier knows the fault templates and magnitudes
  exactly. No real system does (threat TV-M5).

**What this means for AURA:** the case for uncertainty-aware *isolation* at realistic sensor noise is
**weak in this configuration**. The problem relocates to the transient — *what should an aircraft do
during the several seconds in which isolation is impossible?* — which is a better-grounded question
because it was measured rather than assumed.

### [EXP-0002](reports/technical/EXP-0002_STRUCTURAL_ISOLABILITY.md) — response-based fault
distinguishability in a nonlinear 6-DOF fixed-wing model (deterministic, noise-free):

- A **stable five-member ambiguity group** persists at all four valid flight conditions: nominal, a
  scale error on pitch rate, a scale error on angle of attack, a stuck angle-of-attack sensor and a
  stuck airspeed sensor are mutually indistinguishable (10–11 ambiguous pairs of 153 at each
  condition). The mechanism is textbook: a scale-factor fault is unobservable when the true signal
  is near zero, and a stuck fault is nearly inert on a regulated channel.
- **Distinguishability depends on operating condition, monotonically.** Cross-condition rank
  correlation of the pairwise distances runs from 0.984 for the designed control pair (matched
  dynamic pressure, different altitude and airspeed) down to 0.658 for the most separated pair —
  6 of 6 condition pairs in strict rank order of operating-point separation.
- **One ambiguity was predicted in closed form before the simulation and confirmed at r = 0.979.**
  A bias fault and a scale fault on a regulated channel become identical at V\* = b/(k−1) = 50 m/s.

Evidence: EXP-0002 → DS-0001 → `experiments/EXP-0002/config/exp0002.yaml` → commit recorded in
`results/validation/EXP-0002/exp0002_results.json`. Robust to integration step, fault magnitude and
run duration; all 90 runs bitwise reproducible.

**What this does not show:** it says nothing about whether uncertainty-aware diagnosis works. It
establishes only that ambiguity and condition-dependent diagnosability are real phenomena in this
model — the substrate the research question presumes.

## Preliminary findings

**From experiment.** One Phase 0 assumption was **refuted in its specifics**: A-FLT-03 named a
pitch-rate scale error and an elevator effectiveness loss as the flight-condition-dependent
ambiguity pair. They are distinguishable at every valid condition. The pair that actually behaves
that way is bias-versus-scale on airspeed. The assumption was right in general and wrong in detail.

**From literature.** The following are *reconnaissance observations* from Phase 0 — they
characterise the state of the field, not AURA's results, and rest on abstract-level reading of most
sources:

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

1. **How much ambiguity does unknown fault magnitude create?** EXP-0010 assumed it known; with free
   magnitude, bias and scale faults on one channel intersect exactly. Probably the dominant
   unmeasured effect. (EXP-0011)
2. **How much does template/model error raise the effective uncertainty?** If it reaches ~10x the
   sensor spec, the ambiguity EXP-0010 found only under stress becomes the realistic regime — and
   AURA's motivation returns on evidence.
3. **What is actually knowable during the ~5 s before isolation is possible?** (EXP-0012)
4. **Is one verdict flip in 153 pairs enough condition-dependence** to justify a condition-dependent
   ambiguity model? Still open, and still the question that most threatens the design.
3. Does a systematic database search close the identified gaps? (still outstanding)
4. Does the result reproduce on an **independently sourced** aircraft model? (TV-D10)
5. Does excitation change the ambiguity matrix more than flight condition does?
6. Is expected decision cost the right primary metric for the decision layer?

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
- **Single airframe, single sensor suite** — and the airframe is now **self-implemented**, its
  parameters chosen by the experimenter, after the intended model was found to be GPL-3.0 (TV-D10,
  HIGH). Reproduction on an independently sourced model is required before EXP-0002's result becomes
  load-bearing.
- **EXP-0002 is deterministic and noise-free.** Every distance it reports is an upper bound on what
  an estimator could achieve from one noisy realisation.
- **One flight condition was invalidated** ([FAIL-0001](experiments/failures/FAIL-0001.md)) after it
  produced the most favourable-looking numbers in the experiment by stalling.

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

## How this repository is maintained

AURA publishes the scientific record, not the whole laboratory. What gets published, what stays
local, and the privacy, security, data, literature and scientific-honesty rules that govern that
decision are set out in [`docs/public_repository_policy.md`](docs/public_repository_policy.md).
Every push runs the audit in
[`infrastructure/public_release_checklist.md`](infrastructure/public_release_checklist.md), which
carries a dated record of what was checked and what was found.

## Reading order for a new reader

1. This README.
2. [`FINDINGS.md`](FINDINGS.md) — one-page current state.
3. [`reports/phase0/PHASE0_RESEARCH_REPORT.md`](reports/phase0/PHASE0_RESEARCH_REPORT.md) — the full
   Phase 0 argument, including whether AURA is worth building.
4. [`reports/phase0/THREATS_TO_VALIDITY.md`](reports/phase0/THREATS_TO_VALIDITY.md) — read this
   before believing anything above.
