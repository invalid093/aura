# HANDOFF — AURA research-engineering portfolio

**Date:** 2026-09-08 · **Framework version:** 0.8.0
**This document is self-contained.** It assumes no repository access and no memory of the
sessions that produced the work.

---

## Project purpose

> **AURA is a reproducible and auditable computational research framework for designing,
> executing, validating, analysing and documenting aerospace engineering experiments.**

The contribution is **research infrastructure and engineering methodology**, not a
fault-diagnosis algorithm. AURA demonstrates that computational research can be treated as
an engineered system: explicit assumptions, versioned configurations, reproducible
execution, deterministic seed control, automated validity gates, statistical analysis,
provenance, failure tracking, evidence classification, research reports, independent-review
handoffs, and explicit termination decisions.

## Historical research outcome

AURA began as a scientific investigation into uncertainty-aware fault diagnosis for
uncrewed aircraft (RQ-1: does representing *evidential ambiguity* separately from
*competence loss* improve act/abstain/escalate decisions?). Four pre-registered experiments
were run.

| Experiment | Finding |
|---|---|
| EXP-0002 | Deterministic ambiguity exists but condition dependence is weak — 1 verdict flip in 153 pairs. FAIL-0001: one flight condition departed controlled flight and was excluded |
| EXP-0010 | At the reference sensor spec **P_iso = 1.000** — no practical ambiguity. Ambiguity needs 10–19× that noise |
| EXP-0011 | Unknown fault magnitude costs **0.0001** at full observation; a prior excluding the truth costs 6.5–13.3 points and worsens with data |
| EXP-0012 | With the true fault outside the library, 5.8% of cells are confidently wrong with the residual silent; a χ² residual catches 47–83%, exactly where a closed-form threshold predicts (1502/1512, **99.3%**) |

A cumulative review found the premise **unsupported** and the programme **substantially
goalpost-shifting** (the target problem changed repeatedly; the intended solution never
did). It corrected two of the project's own published claims. The TV-N1 novelty audit — a
gate declared blocking at Phase 0 and run past four times — then returned:

**`NOVELTY GATE: FAIL` · `EXP-0013: CANCEL` · `ML PHASE: NOT JUSTIFIED`**

Every substantive finding had established prior art: Berk (1966) for posterior
concentration under misspecification; Massoumnia, Verghese & Willsky (1989) for design-time
characterisation of undetectable faults; Eriksson, Frisk & Krysander (2013) for quantitative
distinguishability; Scott et al. (2014) and Kong et al. (2025) for excitation-limited
diagnosability and active input design. AURA's own strongest result — a closed-form
classical threshold predicting its blind spots in 99.3% of cells — was the sharpest evidence
against its novelty.

**The research record is preserved unedited.** RQ-1 remains published verbatim with a dated
status note. The sequence *hypothesis → experiment → falsification → audit → termination* is
the evidence for the methodology, not an embarrassment to be smoothed over.

## Current architecture

21 modules, dependencies pointing downward only, no cycles.

```
cli → runner → {report, handoff, registry, compare, failures, retention}
             → {validation, gates, provenance, montecarlo}
             → {spec, status}
             → {evidence, statistics, seeds, hashing, integrity} → errors
```

Lifecycle:

```
specification → preflight validation → PREFLIGHT gates → execution
    → RUNTIME gates → POST gates → STATISTICAL gates → evidence package
```

Gate outcome precedence: `INVALID > FAIL > INCONCLUSIVE > PASS`.

**Dependencies: Python 3.11+, numpy, PyYAML.** No scipy, no jsonschema, no pytest. Special
functions are built on `math.erf`/`erfc`; the one approximation used (Wilson–Hilferty)
*refuses to run* outside its accurate regime rather than returning a wrong critical value.

## Implemented capabilities

| Capability | Status | Evidence |
|---|---|---|
| Experiment registry with enumerated status transitions | complete | `aura.registry`, `aura.status`; every transition requires a recorded reason |
| Machine-readable experiment specification | complete | `aura.spec`; content-hashed excluding status/path |
| Preflight validation | complete | `aura.validation`; 20+ checks; reports all problems at once |
| Reproducible execution + provenance | complete | `aura.runner`, `aura.provenance`; machine-independent by construction |
| Deterministic seeding | complete | `aura.seeds`; SHA-256 derivation; order-independent; no global RNG |
| Monte Carlo engine | complete | `aura.montecarlo`; failures recorded not dropped; all-fail raises |
| Statistical sufficiency & convergence | complete | `aura.statistics`; required-N derived from a declared target |
| Validity gates | complete | `aura.gates`; 10 gates across 4 phases |
| Failure registry | complete | `aura.failures`; automatic on rejection; `became_test` linkage |
| Evidence classification | complete | `aura.evidence`; 7 classes; measured/inferred separated structurally |
| Evidence package generation | complete | 8 files, 21.5 kB, checksummed |
| Report generation | complete | `aura.report`; cannot convert a number into a conclusion |
| Handoff generation | complete | `aura.handoff`; self-contained; adversarial by design |
| Experiment comparison | complete | `aura.compare`; blocks incommensurable comparisons |
| Retention policy | complete | `aura.retention`; 4 classes; plans cleanup, never performs it |
| CLI | complete | 8 commands |
| Regression tests | complete | 82 tests, standard library only |

## Demonstration status

**PASS path — `DEMO-0001`.** Monte Carlo recovery of a closed-form detection probability.
All ten gates PASS; status `COMPLETED`; conclusion emitted.

| Quantity | Value |
|---|---|
| Closed form Φ(2.0 − 1.6449) | 0.638760 |
| Monte Carlo, n = 8,851 (derived from the precision target) | 0.644221 |
| Absolute error | 0.005461 vs target half-width 0.010 |
| 95% CI | [0.63419, 0.65413] — contains the exact value |
| Repeat execution | bit-identical |

**FAIL path — `DEMO-0002`.** Same model, operating point 9.0 outside the declared envelope
[0.0, 6.0]. The estimate looks essentially perfect. AURA marks the run `INVALID`, writes
`FAIL-0002` automatically, and emits **no** scientific conclusion.

Both are reproducible in under a second on an ordinary computer.

## Test status

```
python -m unittest discover -s tests -t .
Ran 82 tests in ~1.7s — OK
```

Coverage includes schema validation, seed determinism, Monte Carlo aggregation,
statistical calculations against published reference values, configuration hashing,
provenance generation, validity gates, failure registration, status transitions,
frozen-test protection, raw-data immutability, report generation, handoff generation, and
experiment comparison.

**Regression tests derived from real research failures:** envelope violation (FAIL-0001),
duplicate templates from a silent patch, reported-N mismatch, non-dividing timestep,
asymmetric admissible sets.

**Two bugs in the framework were found by its own tests during this conversion**, and both
are recorded rather than quietly fixed:

1. the failure-id allocator would have re-issued `FAIL-0001`, colliding with the historical
   FC-4 record, because it scanned only its own YAML format;
2. a run that crashed during execution reported `conclusion_emitted: true`, because its
   status was `FAILED` while its preflight gates had all passed.

## Public repository status

Published under the project's public repository policy. **No licence is applied** — the
repository is a research record, not reusable software.

Not published: personal information, credentials, machine-specific paths, bulk raw
trajectory data, copyrighted papers. Published: architecture, schemas, reusable
infrastructure, tests, compact examples, experiment specifications, methodology, research
reports, failure case studies, provenance examples, literature references, reproduction
instructions.

Provenance records are machine-independent **by construction** — no hostname, username,
absolute path or CPU model — which is both a reproducibility and a privacy property.

## Known limitations

- **Cross-platform bitwise identity is not claimed.** Different numpy builds and CPU
  architectures can differ in the last bits; the platform is recorded so a difference can be
  attributed.
- **A dirty working tree** means the recorded commit alone does not reproduce a run. This is
  recorded as a warning and surfaced in report Limitations, not blocked.
- **Without git**, the code version cannot be recorded; the provenance gate returns
  `INCONCLUSIVE`, never PASS.
- **`chi2_quantile` refuses dof < 10** rather than returning an inaccurate critical value.
  Correct, but a real functional limit.
- **No parallel execution.** The seed scheme supports it (seeds depend on labels, not order)
  but it has not been implemented; no measured need.
- **The historical experiments predate the framework.** EXP-0002…EXP-0012 carry their own
  provenance in their results JSON but do not have AURA evidence packages, and are indexed
  read-only as legacy records.
- **The aircraft model (GFW-1) has never been cross-validated against flight data** (TV-D10).
- **The TV-N1 literature audit was narrower than the Phase 0 protocol specified** — no
  institutional database access; several sources assessed from verbatim abstracts plus
  verified metadata rather than full text.
- **Gate coverage is a design claim, not a proof.** Ten gates cover the failure modes this
  project encountered. There is no argument that they are complete.

## Portfolio claims that ARE supported

> Built a reproducible computational research framework for aerospace experiments with
> versioned experiment specifications, deterministic execution, Monte Carlo analysis,
> automated validity gates, provenance tracking, and structured research reporting.

> Designed automated safeguards for experiment validity, statistical sufficiency,
> reproducibility, and frozen-test integrity.

> Developed an auditable research workflow that preserves failed experiments, tracks
> methodological deviations, and generates independent-review handoffs.

> Converted concrete research failures into permanent regression tests, including a
> simulation that left its validity envelope while producing the study's most
> favourable-looking results.

> Conducted a blocking literature and novelty audit that terminated the project's own
> research branch, and published the negative outcome.

## Claims that must NOT be made

- ❌ "Developed a novel aircraft fault-diagnosis method." — The novelty audit returned FAIL.
- ❌ "Developed an ML-based uncertainty-aware health-management system." — There is no ML in
  this project, by design.
- ❌ "Demonstrated safe autonomous aircraft operation." — Nothing here bears on safety.
- ❌ Any claim of real-aircraft, operational, or certification applicability.
- ❌ Any claim that the aircraft model is validated. It is not.
- ❌ Any claim that the gate set is complete or that passing gates implies correctness. A
  satisfied precision target is not a validated result, and AURA says so in every report.

## Recommended final presentation

Lead with the **failure path**, not the success path. Anyone can show a pipeline that
produces a number. The distinguishing demonstration is `DEMO-0002`: an experiment whose
result looks excellent, automatically rejected for a documented reason, with no scientific
conclusion emitted — and a failure record written without anyone remembering to.

Then show the lineage: this behaviour exists because of FAIL-0001, where a flight condition
that had departed controlled flight produced the most favourable-looking numbers in the
study. **A research failure became an engineering test.**

Close with the termination. The project ran a blocking novelty audit against its own work,
found the answer was already in the literature, cancelled the follow-up experiment,
declined to introduce ML, and published all of it.

The strongest available claim is not *"I built a sophisticated AI aircraft."* It is:

> **"I built infrastructure that forces computational research to be reproducible,
> auditable, statistically defensible, and willing to say 'this experiment was invalid' or
> 'this hypothesis is not novel.'"**

## Questions for independent review

- Are the ten gates the *right* ten, or merely the ones this project's failures suggested?
- Does the report generator's separation of measured from inferred actually hold under
  adversarial use, or can an interpretation be smuggled into a measured slot?
- Is the seed scheme genuinely order-independent under parallel execution, which has not
  been implemented or tested?
- Does `aura compare`'s blocking-field list capture real incommensurability, or is it a
  heuristic that will produce both false blocks and false clearances?
- Is a specification content hash that excludes `status` the right boundary between
  scientific content and lifecycle metadata?
- Is 21.5 kB of evidence package genuinely sufficient to reconstruct a disputed result?
