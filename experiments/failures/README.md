# Failure Records

One file per failure: `FAIL-XXXX.md`. Nothing here is deleted.

## Template

```markdown
# FAIL-XXXX — <short title>

- **What failed:**
- **When:** date, experiment ID, git commit
- **Why:** root cause, or "unknown" if not established
- **Category:** SOFTWARE | NUMERICAL | EXPERIMENTAL_INVALIDITY | SCIENTIFIC_NEGATIVE_RESULT
- **Scientific impact:**
- **Are prior conclusions affected?** list experiment IDs, or "none"
- **Methodological implication:**
- **Resolution:**
```

## The categories are not interchangeable

| Category | Meaning | Evidence? |
|---|---|---|
| `SOFTWARE` | The implementation was wrong | No — fix and rerun |
| `NUMERICAL` | The computation was unstable or invalid | No — may indicate a modelling problem |
| `EXPERIMENTAL_INVALIDITY` | Not a valid test (leakage, contamination, bad control) | No — any conclusion drawn from it must be retracted |
| `SCIENTIFIC_NEGATIVE_RESULT` | Valid experiment; hypothesis unsupported | **Yes. This is research evidence and gets reported.** |

Filing a negative result under one of the first three categories is how findings get buried, and
is prohibited.

## Current records

| ID | Title | Category | Status |
|----|-------|----------|--------|
| — | *none* | — | — |

**Phase 0 process note (not a numbered failure, no experiment involved):** full-text retrieval of
LIT-0033 failed (PDF returned unparsed). Recorded in `research/reconnaissance/SEARCH_LOG.md`.
