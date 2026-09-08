# AURA — Project Charter

**Project:** AURA — Autonomous Uncertainty & Reliability Architecture
**Repository:** `aura`
**Phase:** 0 complete (2026-09-08); Phase 1 not started
**Type:** Independent computational research

---

## 1. Purpose

AURA investigates whether an autonomous aircraft can usefully distinguish **"the evidence is
genuinely ambiguous"** from **"I am operating outside what I know"** — and whether that distinction
changes what the aircraft should do.

It is a research programme, not an engineering demonstration. Its output is knowledge about whether
a proposed capability works, including the finding that it does not.

---

## 2. Research question

See `docs/research_question.md` (RQ-1). Hypotheses and falsification criteria in
`docs/hypotheses.md`.

---

## 3. Governing principle

> **Maximise scientific information gained per unit of computation, time, storage and researcher
> attention.**

Practical consequences, in order of how often they will be tested:

1. More simulations do not produce better research. The full experiment runs only after a pilot
   justifies it.
2. Model fidelity is increased only when the research question requires it. AURA needs *analysable*
   equations, not accurate ones.
3. Machine learning is added only where it provides an experimental advantage over a simpler method
   — and B0/B1 exist to detect when it does not.
4. A negative result is a result.

---

## 4. Roles

| Role | Holder | Authority |
|---|---|---|
| Scientific authority | The human researcher | Owns the research question, hypotheses, metrics, interpretation, and any decision to change them |
| Computational research engineer | Claude | Implements, documents, records, challenges. May not silently change any scientific definition — see `CLAUDE.md` |

---

## 5. Phases

| Phase | Content | Status |
|---|---|---|
| **0** | Reconnaissance, scientific definition, computational infrastructure | **Complete 2026-09-08** |
| **1a** | Gates: systematic literature search (TV-N1); EXP-0001 runtime; **EXP-0002 structural isolability** | Not started |
| **1b** | Simulation, fault injection, estimator, residual bank, baselines B0–B4 | Blocked on 1a |
| **1c** | Pilot (EXP-0005) → medium (EXP-0006) → frozen test (EXP-0007) | Blocked on 1b |
| **1d** | External validity (ALFA), sensitivity analyses, reporting | Blocked on 1c |
| **2** | Only if warranted by Phase 1 findings. Not planned in advance | — |

**Phase 1a can end the project.** EXP-0002 or the systematic search can invalidate the design at
low cost. That is the point of running them first.

---

## 6. Deliverables

- A reproducible open benchmark for uncertainty-aware fault diagnosis under flight-regime shift.
- A measured answer to RQ-1, in whichever direction the evidence points.
- The H3 confounding curve — a quantity the literature states as a limitation but has not measured.
- A complete provenance record: every figure traceable to experiment → dataset → configuration →
  commit.

---

## 7. Constraints

| Constraint | Value |
|---|---|
| Compute | Single workstation. No cluster, no cloud |
| Storage | Local disk; ~28 GB forecast, ~100 GB ceiling before infrastructure changes |
| Software | Open source only; Python primary |
| Data | Public/unclassified only |
| Team | One researcher plus an AI research engineer |

---

## 8. Integrity commitments

Binding, and enforced through `CLAUDE.md`:

- The frozen test set is not modified because results are inconvenient.
- Hyperparameters are not tuned on the test set.
- Failed experiments are recorded, not deleted.
- Hypotheses are not presented as findings.
- Assumptions are not hidden in code.
- Negative results are reported as prominently as positive ones.
- Novelty is not claimed until a systematic literature search supports it.

---

## 9. Decision to proceed

**Phase 0 recommendation: proceed to Phase 1a only.**

Justification and the conditions under which AURA should *not* be built are in
`reports/phase0/PHASE0_RESEARCH_REPORT.md` §23–24.
