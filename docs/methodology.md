# AURA — Methodology

**Date:** 2026-09-08

---

## 1. Research process

Every substantive activity follows this chain, and each stage must be traceable to the one before it:

```
QUESTION → HYPOTHESIS → EXPERIMENT DESIGN → CONFIGURATION → SIMULATION
   → RAW DATA → ANALYSIS → RESULT → INTERPRETATION → REVIEW → DECISION → ARCHIVE
```

Operational consequences:

- No algorithm is implemented without a hypothesis it serves.
- No experiment is run without a registry entry created **before** it runs (status `PLANNED`).
- No result is interpreted without its provenance chain being resolvable back to a configuration
  file and a Git commit.
- No expensive experiment runs before a cheap one shows it is justified.

---

## 2. Evidence classification

Every significant statement in AURA documents carries one of these classes. Mixing them is the
primary way research documents mislead.

| Class | Meaning | Test |
|---|---|---|
| `FACT` | Externally verifiable; traceable to a cited source or a standard | Could a reviewer check it without trusting us? |
| `CALCULATION` | Derived arithmetically from stated inputs | Are the inputs and the arithmetic both shown? |
| `OBSERVATION` | Something measured in our own experiments | Is the experiment ID attached? |
| `INTERPRETATION` | Our reading of what an observation means | Could a competent person read it differently? |
| `HYPOTHESIS` | A claim we intend to test | Is the falsification condition stated? |
| `ASSUMPTION` | Taken as true without testing | Is it recorded in `docs/assumptions.md` with an ID? |
| `LIMITATION` | A known weakness | Is it stated where a reader will actually see it? |

**Rules:**
- An interpretation is never presented as a fact.
- A hypothesis is never presented as a result.
- Assumptions are never hidden inside code. If code assumes something, the assumption gets an ID
  in `docs/assumptions.md` and the code cites the ID in a comment.

---

## 3. Experimental discipline

### Exploratory vs confirmatory

Both are legitimate; conflating them is not.

- **Exploratory** — free to iterate, look at data, change approach. Results are labelled
  exploratory and **may not be used as evidence for a hypothesis.**
- **Confirmatory** — hypothesis, metric, threshold and analysis are fixed before the run. Exactly
  one primary confirmatory comparison exists (H1 at shift axis S6).

### The frozen test set

- Generated once, hashed, manifest committed **before any method is trained**.
- Never regenerated to fix an inconvenient result. If it must change, it becomes a **new dataset ID**
  and every result computed on the old one is marked `SUPERSEDED`, not deleted.
- Evaluated once per method version; every evaluation logged regardless of outcome.
- Hyperparameters are never tuned on it.

### Splitting

Splits are by **scenario**, never by time window within a run. An automated check in
`infrastructure/validation/` fails if any run identifier appears on both sides of a split.

---

## 4. Metric philosophy

Ordered by weight:

1. **Expected decision cost** — the quantity that actually matters, reported over a range of cost
   ratios rather than a single arbitrary matrix.
2. **Proper scoring rules** (NLL, Brier) — for probabilistic quality.
3. **Task metrics** (FAR, MDR, detection latency, isolation accuracy conditioned on structural
   isolability) — for comparability with the FDI literature.
4. **ECE and reliability diagrams** — secondary, always labelled, never a headline. ECE is not a
   proper scoring rule (LIT-0010, LIT-0011).

**Coverage matching is mandatory** for any comparison involving abstention or escalation.

---

## 5. Statistical practice

- Stochastic results are reported as distributions over ≥30 seeds. Single runs are never evidence.
- Paired comparisons at scenario level with bias-corrected bootstrap CIs (≥1000 resamples).
- **Equivalence claims require equivalence tests** (TOST, margin δ = 2% of baseline cost), because
  a non-significant difference is not evidence of no difference.
- Confirmatory claims across multiple methods and axes are corrected (Holm–Bonferroni).
- Effect sizes are reported alongside p-values, and preferred to them.

---

## 6. Handling negative results

A negative result is an outcome, not a failure. Concretely:

- If H1 is falsified, the report's headline is the falsification, not a search for a subgroup where
  it holds.
- Subgroup analyses after a negative primary result are **exploratory** and labelled as such.
- Failed experiments are recorded with `FAIL-####` IDs and retained (see
  `infrastructure/experiment_management.md`).
- The distinction between *software failure*, *numerical failure*, *experimental invalidity*, and
  *scientific negative result* is maintained. Only the fourth is evidence.

---

## 7. Reproducibility standard

Every significant run records: Git commit, configuration file hash, dataset IDs, random seeds,
software environment (lockfile), execution date, and hardware/runtime information. Details in
`infrastructure/reproducibility.md`.

Parameters live in version-controlled configuration files, not in code.

---

## 8. Review

After every significant assignment, a self-contained **Research Handoff Report** is produced
(`handoffs/`) that can be pasted into an independent AI or human reviewer without attachments. Its
purpose is **criticism, not confirmation**. Reviewers are explicitly asked to attack novelty,
methodology, simulation bias, leakage, test-set contamination, calibration claims, and any
conclusion that outruns its evidence.
