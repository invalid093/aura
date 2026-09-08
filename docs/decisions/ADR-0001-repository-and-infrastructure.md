# ADR-0001 — Repository structure and infrastructure scale

**Date:** 2026-09-08 · **Status:** Accepted

## Context

Phase 0 proposed a directory structure. Two risks attach to it: creating directories for the
appearance of organisation, and adopting infrastructure (LFS, databases, cloud, orchestration)
before measuring whether it is needed.

## Decision

Adopt the proposed structure largely as given, with these deviations:

- Added `experiments/REGISTRY.md`, `experiments/TEST_SET_ACCESS_LOG.md` and
  `experiments/failures/`. The registry and access log are integrity mechanisms, not organisation —
  the access log exists specifically because test-set reuse is the project's highest-severity
  integrity risk (TV-S1).
- Added `FINDINGS.md` at the repository root as the one-page current-state record.
- Promoted threats-to-validity to a first-class deliverable
  (`reports/phase0/THREATS_TO_VALIDITY.md`) rather than a section inside the main report, so that
  it is read rather than skimmed past.
- Implementation directories (`aircraft/`, `sensors/`, `faults/`, `estimation/`, `diagnosis/`,
  `autonomy/`, `simulation/`) are created empty with `.gitkeep`. They are justified by the
  architecture in `README.md`, not by having content today.

No CI, no containers, no workflow orchestrator, and no experiment-tracking service in Phase 1.

## Alternatives considered

- **Flat structure until needed.** Rejected: provenance requires the data/results/manifest
  separation from the very first dataset, and retrofitting it later would orphan early data.
- **Adopt an experiment-tracking service.** Rejected: a YAML registry plus Git satisfies the
  requirements at this scale with no external dependency, no account, and no vendor availability
  risk.

## Consequences

Some directories stay empty for a while. That is accepted; deleting and recreating them would churn
paths that the manifests and documents already reference.

## Revisit if

A second contributor joins, or the experiment count exceeds roughly 100.
