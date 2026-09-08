# Candidate Research Questions — Retained Record

**Date:** 2026-09-08
**Status:** RD-G selected (`docs/decisions/ADR-0002-research-question.md`). The others are retained
here, not deleted, so that a re-scope has somewhere to start.

Scored comparison: `reports/phase0/RESEARCH_DIRECTION_COMPARISON.md`.

---

## Selected

### RD-G — Ambiguity vs competence loss under combined shift *(SELECTED)*

> When an autonomous aircraft's operating regime departs from the conditions under which its
> diagnostic system was developed, does representing evidential ambiguity separately from
> competence loss produce better act / abstain / escalate decisions than a single scalar
> confidence — and does that separation survive when regime shift and fault onset occur
> simultaneously?

Full statement and definitions: `docs/research_question.md`.

---

## Retained alternatives

### RD-A — Uncertainty-aware fault diagnosis under distribution shift
> Does explicitly modelling diagnostic uncertainty improve fault-management decisions when flight
> conditions differ from development conditions?

**Revisit if:** RD-G's decomposition is falsified (H2) but the shift-calibration question remains
open in the aerospace domain. RD-A then becomes a legitimate, if less novel, application study.

### RD-B — Physics/data hybrid fault diagnosis
> Can physics-based residuals combined with data-driven methods improve diagnosis robustness under
> model mismatch and unseen conditions?

**Status:** absorbed as a *design choice* in RD-G's residual generation rather than a question.
**Revisit if:** pilot results show the hybrid-vs-pure distinction dominates every other effect —
in which case it is the real research question and RD-G is a detail.

### RD-C — Diagnosability limits
> Under what sensor configurations, flight conditions and fault combinations are different failure
> hypotheses fundamentally indistinguishable?

**Status:** absorbed as RD-G's ground-truth mechanism (EXP-0002).
**Revisit if:** EXP-0002 turns out to be unexpectedly rich — e.g. isolability varies with flight
condition in a structured, previously undocumented way. That would be a standalone contribution to
the structural-analysis literature independent of any learning component, and would be worth
reporting on its own.

### RD-D — Diagnostic abstention
> Can an autonomous aircraft determine when the available evidence is insufficient to make a
> reliable diagnosis?

**Status:** absorbed into RD-G, sharpened into *what kind* of insufficiency.
**Revisit if:** the two-component decomposition fails but abstention still outperforms forced
classification — a narrower result that would still be worth reporting.

### RD-E — Uncertainty-aware degraded-mode selection
> Does diagnostic uncertainty improve autonomous selection between continued operation, degraded
> operation, and escalation?

**Status:** this is RD-G's decision layer. Kept separate because it carries the strongest
adversarial prior (LIT-0012) and could be studied on its own with a simpler diagnostic front end.
**Revisit if:** the diagnosis side proves intractable but the decision side is still interesting.

### RD-F — Self-aware autonomous health management
> Can an aircraft detect not only vehicle degradation but also degradation in the reliability of
> its own diagnostic process?

**Status:** retained as *motivation only*. Not falsifiable as phrased — "self-awareness" has no
measurable definition, so a study framed this way degenerates into building an architecture and
asserting it works.
**Revisit if:** a measurable operationalisation is found. RD-G's competence-loss component $N$ is
one narrow instance of it, and the honest framing is that RD-G tests a *sliver* of RD-F.

---

## Rejected outright

| Direction | Why rejected |
|---|---|
| End-to-end learned fault-tolerant control | Confounds diagnosis quality with control quality; two literatures, one experiment |
| Prognostics / remaining useful life | Different question, different data requirements, different community |
| Anomaly detection on real operational flight data (DASHlink/NGAFID) | Labels are operational anomalies, not faults; no isolation ground truth (`DATASET_SURVEY.md`) |
| Adversarial robustness of aircraft diagnostics | Different threat model; not within RQ-1 |
| A "better architecture" for vehicle health management | Not a research question. No falsification condition exists for an architecture |
