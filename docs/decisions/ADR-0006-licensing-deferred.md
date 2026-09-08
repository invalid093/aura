# ADR-0006 — Licensing deferred; no licence during Phase 0

**Date:** 2026-09-08 · **Status:** Accepted · **Supersedes:** an MIT licence added earlier in Phase 0

## Context

An MIT `LICENSE` file was added during initial repository setup, on the reasoning that MIT is a
conventional default for research code.

The project's public repository policy is explicit that this is wrong:

> Do not add a software or data license during Phase 0 unless explicitly instructed by the
> researcher. Do not add MIT/BSD/Apache/GPL merely because they are common.

## Decision

**The `LICENSE` file is removed. The repository carries no licence.**

The README states plainly that no permission to reuse is offered and that licensing will be decided
later. Licensing will be evaluated deliberately, and separately, when the project reaches a suitable
maturity point:

- source-code licence
- dataset licence
- documentation licence
- research and publication rights
- obligations inherited from third-party dependencies

That last item matters here and is a concrete reason not to have guessed. AURA intends to build on
external components (the aircraft model, a structural-analysis toolbox, possibly a public flight
dataset) whose licences are **still unverified** — open actions A-1, A-2 and A-6. Declaring an
outbound licence before knowing the inbound obligations is the wrong order.

## Alternatives considered

- **Keep MIT.** Rejected: it was chosen by default rather than decided, it may conflict with
  dependency terms not yet checked, and choosing a licence is the researcher's call, not an
  implementation detail.
- **Add a "licence TBD" placeholder file.** Rejected: an absent licence already means "all rights
  reserved, no permission granted". A placeholder file adds no legal effect and risks reading as a
  promise of future openness.

## Consequences

- Nobody may reuse the repository contents at this stage. That is the intended and correct default
  for work with no validated results.
- The licence question must be revisited before any of: publishing a benchmark dataset, inviting
  contributions, or submitting work that requires an artefact-availability statement.
- Because the MIT file existed in an earlier local commit, the Phase 0 commit was amended before
  any publication so that no licence was ever offered publicly.

## Revisit when

The first of: a benchmark artefact is ready to publish; an external contributor asks; or a
publication requires an artefact-availability statement.
