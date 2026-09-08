# TV-N1 — Novelty Matrix

**Date:** 2026-09-08 · Companion to [`TV-N1_LITERATURE_AUDIT.md`](TV-N1_LITERATURE_AUDIT.md).

Classification scale (from the audit specification §14):

| Class | Meaning |
|---|---|
| **N0** | Established — the literature already demonstrates essentially the same phenomenon |
| **N1** | Known principle, new implementation — **not strong novelty** |
| **N2** | Combination gap — components known individually, interaction understudied |
| **N3** | Specific scientific gap — literature identifies the issue and leaves a defined open question |
| **N4** | Potentially novel phenomenon — requires exceptional evidence; **never claimed from absence of search hits** |

---

## Every candidate claim AURA could make

| # | Candidate claim | Class | Justification |
|---|---|---|---|
| 1 | A Bayesian classifier over a known fault library becomes confidently wrong when the true fault is absent from the library | **N0** | Berk 1966 proves the asymptotic form; Lu et al. 2015 document it for MMAE on real flight data; the open-set FD literature states it in nearly AURA's words |
| 2 | The posterior softmax is structurally incapable of expressing hypothesis-space mismatch | **N0** | An algebraic identity — a uniform misfit cancels in the softmax. This is the standard motivation for the entire OOD-detection field |
| 3 | A χ² goodness-of-fit residual catches most hypothesis-space mismatch without learning | **N0** | This is the classical model-based FDI consistency test. Established since the 1970s–80s |
| 4 | The residual's blind spot is predicted by a closed-form threshold $\sqrt{z_\alpha}(2KN)^{1/4}$ | **N0** | Elementary non-central χ² detectability; the classical *minimum detectable fault*. Xu 2023 (IEEE TAC) computes minimal detectable and isolable faults for active diagnosis |
| 5 | Unknown faults lying near the known-fault manifold are the dangerous ones | **N0** | Open-set recognition establishes that rejection degrades with proximity of unknowns to known classes — a measured, expected relationship |
| 6 | Fault distinguishability is quantifiable under noise and depends on operating condition | **N0** | Eriksson, Frisk & Krysander 2013 (KL divergence); Liu et al. 2022 (Bhattacharyya); nonlinear diagnosability literature on input/operating-point dependence |
| 7 | Unknown fault magnitude costs little at full observation | **N0** | Fault-size analysis within the same quantitative diagnosability frameworks; Lundgren & Jung 2022 estimate fault size explicitly |
| 8 | A prior excluding the true magnitude worsens with more data | **N0** | Direct consequence of Berk 1966 — concentration on the KL-nearest admissible point sharpens with sample size |
| 9 | Near-manifold detectability is excitation-limited, not observation-time-limited | **N0** | Scott et al. 2014 open by stating faults "cannot be diagnosed without exciting the system"; Kong et al. 2025 Definition 3 formalises "fundamentally limited by the given control sequence" |
| 10 | Excitation design could resolve the near-manifold residue | **N0** | Kong et al. 2025 Lemma 1 proves optimal controls over a non-degenerate admissible set guarantee positive separation; Scott et al. 2014 compute guaranteed separating inputs |
| 11 | Design-time enumeration of a fault library's undetectable blind spots | **N0/N1** | The construct exists for modelled faults (Xu 2023) and, for unmodelled faults, is covered by Kong et al. 2025 §III-C. AURA's version is the same geometry on a different airframe → **N1 at best**, per the closest-paper test |
| 12 | **Empirical characterisation of how often unmodelled-fault rejection actually fails** (Kong et al.'s Assumption 2 measured rather than assumed) | **N2** | The genuine seam — Kong et al. *assume* the unmodelled fault is diagnosable. But: the qualitative answer is known (row 5); the quantitative answer is the classical threshold, which **AURA's own data confirms predicts blindness in 99.3% of cells**; and AURA's rate depends entirely on a fault set it authored. Does not support a programme |
| 13 | Separating evidential ambiguity from competence loss improves act/abstain/escalate decisions (**original RQ-1**) | **Untested, and premise unsupported** | AURA never built a decision layer, and the cumulative review found the motivating premise unsupported. This claim has no evidence in either direction |

---

## Nothing is classified N3 or N4

**`INTERPRETATION`** No candidate reaches N3. The closest — row 12 — is N2, and it fails the standard
the audit specification sets for N2 ("potentially publishable, but requires strong justification").
The justification is not available: AURA's headline rate is an artefact of its own fault selection,
and its own strongest quantitative result demonstrates that classical theory already predicts the
phenomenon.

**`LIMITATION`** No N4 is claimed anywhere. Per §14, absence of a search hit is not evidence of
novelty, and this audit's search was narrower than the Phase 0 protocol requires (no institutional
database access). The FAIL verdict rests entirely on **positive** prior-art hits, never on gaps.

---

## The distinction AURA must stop blurring

**`INTERPRETATION`** Three things were repeatedly conflated in AURA's own documents, and the
literature separates them cleanly:

- **Statistical uncertainty** — uncertainty under a correctly specified probabilistic model. AURA
  measured this in EXP-0010/0011 and found it small.
- **Model/hypothesis uncertainty** — the possibility that the truth is unrepresented. This is what
  EXP-0012 measured, it is the M-open problem, and it is **not** a form of statistical uncertainty.
- **Rigour of execution** — pre-registration, closed-form prediction before simulation, honest
  reporting of falsification. AURA has this in unusual measure. **It is not a scientific
  contribution.**

The third is the one most at risk of being mistaken for novelty in future documents.
