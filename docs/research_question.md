# AURA — Research Question

**Status:** SELECTED (provisional pending a systematic literature search — see TV-N1)
**Date selected:** 2026-09-08
**Supersedes:** the original framing (recorded in §3 below)
**Decision record:** `docs/decisions/ADR-0002-research-question.md`

---

## 1. Primary research question (RQ-1)

> **When an autonomous aircraft's operating regime departs from the conditions under which its
> diagnostic system was developed, does representing *evidential ambiguity* separately from
> *competence loss* produce better act / abstain / escalate decisions than a single scalar
> confidence — and does that separation survive when regime shift and fault onset occur
> simultaneously?**

### The two quantities, defined precisely

These definitions are binding. If they change, the change is an ADR, not an edit.

| Term | Definition | Physical origin | Ground truth available? |
|---|---|---|---|
| **Evidential ambiguity** $A$ | The degree to which two or more fault hypotheses explain the observed evidence equally well | Residual likelihood structure; bounded below by structural isolability at the current flight condition | **Yes** — structural isolability matrix computed per flight condition (LIT-0001, LIT-0002, LIT-0068) |
| **Competence loss** $N$ | The degree to which the current operating point lies outside the conditions represented in development data | Position of the flight condition in the development envelope | **Yes** — by construction of the shift generator |

The critical property: **$A$ and $N$ have different correct responses.**

- High $A$, low $N$: the aircraft is inside its competence but the evidence genuinely cannot
  separate the hypotheses. Correct response: **return a fault set, act on what all members share.**
  Escalating here is a false escalation — the human has no more information than the aircraft.
- Low $A$, high $N$: the evidence looks clean but the system is outside its validated envelope.
  Correct response: **escalate / degrade.** Acting confidently here is the dangerous case.
- High $A$, high $N$: escalate.
- Low $A$, low $N$: act.

A single scalar confidence cannot distinguish the first two rows. That is the entire claim.

---

## 2. Secondary questions

These are answerable *from the same experiment* — they do not require new infrastructure. Any
question that would require its own experimental apparatus was cut.

- **RQ-2 (identifiability).** Are $A$ and $N$ empirically separable, or do they collapse to a
  single scalar? Measured by their rank correlation and by whether $A$ tracks structural
  isolability better than $N$ does.
- **RQ-3 (confounding).** As regime-shift magnitude increases, does novelty-based gating
  progressively suppress genuine fault detections? This quantifies the failure mode that LIT-0004
  states as a limitation but does not measure.
- **RQ-4 (classical baseline calibration).** Is the fault posterior from a classical
  multiple-model / Kalman-filter-bank diagnoser calibrated, and how does its calibration degrade
  under shift compared with learned methods?
- **RQ-5 (does any of it matter).** Do differences in $A$/$N$ representation produce *different
  decisions*, or only different numbers? Measured by act/defer/escalate agreement at matched
  coverage — the LIT-0012 test, applied to ourselves.

---

## 3. Relationship to the original framing

The project's original overarching question was:

> *How can an autonomous high-performance aircraft detect, isolate, and respond to sensor and
> system degradation when human intervention is delayed or unavailable?*

**Assessment: too broad to be testable as stated.** It contains at least four separable research
programmes (detection, isolation, response selection, human-interaction timing), it does not
specify a comparison, and it has no falsification condition. "How can X" questions are engineering
prompts, not hypotheses.

RQ-1 preserves the *motivation* — an aircraft that knows how much it can trust itself — while
being answerable by a single experiment with a defined negative outcome.

**What was deliberately dropped from the original scope:**

- Human–autonomy interaction timing and workload. Not measurable without human subjects.
- Fault-tolerant *control* / reconfiguration. A separate discipline; not required to answer RQ-1.
- Prognostics / remaining useful life. Different problem, different literature.
- "High-performance" as a requirement in itself. The F-16 model is chosen for its *documented
  nonlinearity and wide envelope* (which make regime shift physically meaningful), not for
  its military association. See `reports/phase0/AIRCRAFT_MODEL_SURVEY.md`.

---

## 4. Scientific distinctions this question depends on

Per §5 of the Phase 0 brief, these must not be conflated:

**Abnormality ≠ fault.** An abnormal residual may arise from a sensor fault, an actuator fault, a
disturbance, an unmodelled but valid flight regime, model mismatch, or a parameter error. AURA's
$N$ component exists precisely because the "unusual but valid regime" and "model mismatch" causes
must be separable from the fault causes. A system that maps every anomaly to a hardware fault is
the specific failure AURA is testing against.

**Confidence ≠ uncertainty.** A softmax maximum is a confidence *score*; it is not a calibrated
probability and it is not decomposed. AURA uses "confidence" only when referring to baselines that
literally use a softmax score, and never as a synonym for uncertainty.

---

## 5. Falsification

Stated in full in `docs/hypotheses.md`. In brief: if the two-component representation's
act/abstain/escalate decisions agree with the best scalar baseline above 95% at matched coverage,
**and** the expected-decision-cost difference has a bootstrap confidence interval containing zero,
RQ-1 is answered **negatively** and that is the reported result.

---

## 6. Open issues on the question itself

- **TV-N1 (open):** Novelty rests on a non-systematic search. A systematic database search is a
  Phase 1 gate before any novelty claim.
- **Open:** Whether $A$ should be defined over *fault modes* or over *fault-mode-plus-magnitude*.
  Currently: fault modes only, with magnitude as an independent variable. Revisit if pilot results
  show magnitude dominates ambiguity.
