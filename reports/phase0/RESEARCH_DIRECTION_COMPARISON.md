# Research Direction Comparison — Phase 0

**Date:** 2026-09-08
**Purpose:** Compare serious candidate research directions for AURA and select one.
**Inputs:** `research/gaps/GAP_MATRIX.md`, `research/literature/literature_index.csv`.

---

## 1. Candidate directions

Six candidates were developed. Each is stated as a question, with its strongest supporting
evidence and — more importantly — its strongest *objection*.

---

### RD-A — Uncertainty-aware fault diagnosis under distribution shift

> *Does explicitly modelling diagnostic uncertainty improve fault-management decisions when flight
> conditions differ from development conditions?*

- **Supporting:** G1, G2. Cross-condition degradation is documented in aircraft subsystems (LIT-0051).
- **Objection (severe):** This is essentially LIT-0004 and LIT-0005 with an aircraft attached.
  Answering "yes, uncertainty helps" would replicate known results in a new domain — publishable
  as an application paper, weak as research. Also, LIT-0012 predicts the answer may be "barely".
- **Verdict:** Necessary background, insufficient as the primary question.

---

### RD-B — Physics/data hybrid fault diagnosis

> *Can physics-based residuals combined with data-driven methods improve diagnosis robustness
> under model mismatch and unseen conditions?*

- **Supporting:** G3, mature precedent (LIT-0046, LIT-0047, LIT-0048).
- **Objection:** The hybrid-vs-pure comparison has been run many times. The expected answer
  ("hybrid generalises better") is close to a foregone conclusion, and the interesting part —
  *how much* and *why* — is highly implementation-dependent, which weakens external validity.
- **Verdict:** A useful *design choice* for AURA, not a research question.

---

### RD-C — Diagnosability limits

> *Under what sensor configurations, flight conditions and fault combinations are different
> failure hypotheses fundamentally indistinguishable?*

- **Supporting:** G4. Strong theory available (LIT-0001–0003, LIT-0068). Mode-dependent isolability
  is an established concept and maps directly onto "flight condition".
- **Objection:** Pure structural analysis is largely a *computation*, not an experiment. Done
  alone, it produces a table, not a finding. Its value is as ground truth for something else.
- **Verdict:** Not standalone — but the key enabling asset for RD-D/F.

---

### RD-D — Diagnostic abstention

> *Can an autonomous aircraft determine when the available evidence is insufficient to make a
> reliable diagnosis?*

- **Supporting:** G7. Abstention theory is mature and unapplied here; the S-07 null result suggests
  aircraft applications are genuinely sparse.
- **Objection:** "Add a reject option and report a risk–coverage curve" is a thin contribution on
  its own. Also LIT-0004 already issues warnings instead of diagnoses under high epistemic
  uncertainty — abstention *per se* is done.
- **Verdict:** Strong, but must be sharpened by *what kind* of insufficiency is being detected.

---

### RD-E — Uncertainty-aware degraded-mode selection

> *Does diagnostic uncertainty improve autonomous selection between continued operation, degraded
> operation, and escalation?*

- **Supporting:** G5. Directly aerospace-relevant; maps onto the RTA/F3269 architecture (LIT-0052).
- **Objection (severe):** LIT-0012 is a direct, recent, adversarial prior. It found that the choice
  of uncertainty estimator barely changes act/defer decisions and that the threshold dominates. A
  study that finds the same thing has replicated someone else's negative result; a study that finds
  the opposite must explain why, or be suspected of a confound.
- **Verdict:** Only viable if the *reason* aerospace might differ is stated in advance and tested.

---

### RD-F — Self-aware health management

> *Can an aircraft detect degradation in the reliability of its own diagnostic process, not just in
> the vehicle?*

- **Supporting:** G5, G6, G7. Conceptually the most interesting; matches the project's stated
  philosophical aim.
- **Objection:** As phrased it is not falsifiable. "Self-awareness" has no measurable definition,
  and without one the work degenerates into building an architecture and asserting it works.
- **Verdict:** The right *motivation*; unusable as a literal research question.

---

## 2. Scoring

Scored 1–5 (5 best). `Portfolio value` is recorded but is explicitly **not** allowed to break ties
in favour of a scientifically weaker option (§10 of the Phase 0 brief).

| Criterion | RD-A | RD-B | RD-C | RD-D | RD-E | **RD-G (selected, §3)** |
|---|---|---|---|---|---|---|
| Scientific novelty | 2 | 2 | 3 | 3 | 2 | **4** |
| Aerospace relevance | 4 | 4 | 4 | 4 | 5 | **5** |
| Feasibility (solo, open tools) | 4 | 3 | 5 | 4 | 3 | **4** |
| Reproducibility | 4 | 3 | 5 | 4 | 3 | **5** |
| Public data/lit availability | 4 | 4 | 5 | 3 | 3 | **4** |
| Quantitative evaluability | 4 | 3 | 5 | 4 | 3 | **5** |
| Negative-result value | 2 | 2 | 3 | 3 | **5** | **5** |
| Independence from proprietary info | 5 | 5 | 5 | 5 | 5 | **5** |
| Technical depth | 3 | 4 | 4 | 3 | 3 | **4** |
| Scope control | 3 | 2 | 5 | 4 | 3 | **4** |
| Falsifiability | 3 | 3 | 4 | 4 | 4 | **5** |
| *(Portfolio value — not decisive)* | *4* | *4* | *2* | *3* | *5* | *5* |
| **Total (excl. portfolio)** | **38** | **35** | **48** | **41** | **39** | **50** |

**OBSERVATION:** RD-C scores highly because it is cheap, certain and reproducible — but it is a
computation, not a discovery. This is exactly the failure mode the scoring rubric can produce, and
it is why the rubric is not applied mechanically.

---

## 3. Selected direction — RD-G

RD-G is a synthesis of RD-C, RD-D and RD-F, sharpened against the RD-E objection. It is the only
formulation found in which:

1. there is **ground truth for the uncertainty itself** (from RD-C's structural analysis),
2. the hypothesis has a **specific, pre-registered way to fail** (the LIT-0012 equivalence result), and
3. the quantity measured is one the closest prior work (LIT-0004) **explicitly declined to measure**.

> **RD-G (primary research question):**
> When an autonomous aircraft's operating regime departs from its diagnostic development envelope,
> does a diagnostic system that represents **evidential ambiguity** (which faults are
> indistinguishable given the current sensors and flight condition) *separately from*
> **competence loss** (the current condition lies outside development conditions) make better
> act / abstain / escalate decisions than a single scalar confidence — and does that separation
> survive when regime shift and fault onset occur simultaneously?

### Why RD-G survives the RD-E objection

LIT-0012 compared seven estimators that all read the **same** evidence — a softmax head over a
learned representation. Their near-identical behaviour is then unsurprising: they are monotone
transformations of one another's inputs.

AURA's two components are **not** derived from the same evidence:

- *Ambiguity* comes from the **residual likelihood structure** — which fault hypotheses can explain
  the observed residual pattern. It is bounded below by structural isolability, which is
  analytically computable and **mode-dependent**.
- *Novelty* comes from the **position of the operating point relative to development conditions** —
  a quantity that is independent of which fault is present.

**HYPOTHESIS (falsifiable):** because these read different evidence, they will not collapse into a
single scalar, and the LIT-0012 equivalence result will *not* reproduce.
**If it does reproduce, that is the finding** — and it is a stronger, more general result than
LIT-0012 because it would show the equivalence holds even when the estimators are given
structurally different evidence.

Either outcome is publishable. That is the property a research question should have.

---

## 4. What was rejected and why (recorded for the archive)

| Rejected | Reason |
|---|---|
| RD-A as primary | Replication of LIT-0004/0005 with an aircraft attached |
| RD-B as primary | Expected answer known; implementation-dependent |
| RD-C as primary | A computation, not an experiment |
| RD-D as primary | Too thin alone; abstention already exists in LIT-0004 |
| RD-E as primary | Direct adversarial prior; no stated reason aerospace would differ |
| RD-F as literally phrased | Not falsifiable |

All six remain in `research/hypotheses/` and may be revisited if RD-G is invalidated.
