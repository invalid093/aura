# Frozen Test Set Access Log

**Append-only.** Every evaluation against a frozen dataset is logged here, regardless of whether
the result was welcome. Repeated evaluation of the same method version against the same frozen set
must be justified in the notes.

Rationale: test-set reuse is the highest-severity integrity risk in this project (TV-S1). A log
that only records successful evaluations is worse than no log.

| # | Date (UTC) | Dataset ID | Method + version | Experiment | Result recorded? | Notes |
|---|-----------|------------|------------------|------------|------------------|-------|
| — | — | — | — | — | — | *No frozen dataset exists yet* |
