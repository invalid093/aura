# Reporting and Visualisation

**Date:** 2026-09-08

---

## 1. Principle

Every figure answers a specific question. A figure that does not is deleted, not kept "for
completeness". The objective is rapid, honest comprehension — not volume.

---

## 2. Figure hierarchy

### Figure 1 — Executive figure
Communicates the central finding in one image. For AURA this will most likely be
**expected decision cost vs shift magnitude, per method, at matched coverage, over the cost-ratio
family** — because that is exactly the H1 test.

If H1 is falsified, Figure 1 shows the *equivalence*: overlapping cost curves with the equivalence
margin drawn. A falsified hypothesis gets the same prominence as a supported one.

### Scientific figures
- Detection performance (ROC / detection latency vs magnitude)
- Isolation performance, **conditioned on structural isolability**
- Uncertainty behaviour: reliability diagrams and proper-score decomposition
- Distribution shift: metric degradation vs measured shift magnitude
- **H3 confounding curve**: MDR gap (gated − ungated) vs shift magnitude
- Decision quality: risk–coverage curves, act/defer/escalate agreement matrices
- H2 identifiability: joint distribution of $A$ and $N$, coloured by ground-truth ambiguity group

### Diagnostic figures
Residual traces, estimator covariance evolution, individual failure cases, edge cases. These live
in `results/exploratory/` and are not published without a reason.

### Supplementary figures
Detailed evidence supporting the primary conclusions. Full factorial results, per-axis breakdowns.

---

## 3. Conventions

- Naming: `FIG-001-detection-performance.png`
- Every figure has a sidecar `FIG-XXX.json` with experiment IDs, dataset IDs, script path, commit.
- **Uncertainty is shown, not implied.** Every point estimate carries an interval; every curve over
  seeds shows its spread.
- Axes always labelled with units. Log scales marked explicitly.
- Colour choices readable in greyscale and colour-vision-deficiency safe.
- **No manual post-editing.** If a figure needs a change, the script changes.

---

## 4. Honest presentation rules

Binding, and derived from the failure modes this project is most at risk of:

1. **Matched coverage or no comparison.** Any plot comparing methods with abstention must state the
   coverage at which the comparison is made.
2. **Show the baseline that wins.** If a simple threshold matches AURA, that appears in Figure 1,
   not in a supplementary appendix.
3. **No truncated axes** that exaggerate a difference.
4. **No selective shift levels.** If a method wins at some shift magnitudes and loses at others,
   the whole range is shown.
5. **ECE is never the headline.** It appears labelled as a secondary diagnostic (LIT-0010,
   LIT-0011).
6. **Negative results are not relegated.** A falsified hypothesis appears in the abstract, the
   executive figure, and the conclusions.

---

## 5. Current-state record

`FINDINGS.md` at the repository root is maintained continuously and kept short:

```
CURRENT RQ:
CURRENT HYPOTHESIS:
BEST VALIDATED RESULT:
KEY FAILURE:
KEY LIMITATION:
NEXT SCIENTIFIC QUESTION:
```

A reader should be able to answer, in under two minutes: *What did we ask? What did we test? What
happened? How certain are we? What failed? What does it mean? What next?*

No dashboards. No status pages. The value is in brevity.

---

## 6. Report types

| Report | Location | Audience |
|---|---|---|
| Phase reports | `reports/phase0/`, `reports/phase1/` | The researcher; a reviewer |
| Technical notes | `reports/technical/` | Implementation-level detail |
| Research outputs | `reports/research/` | Draft manuscripts |
| **Handoff reports** | `handoffs/` | **Independent AI or human critics** |

---

## 7. Cross-AI scientific review

After every significant assignment, a self-contained **Research Handoff Report** is produced in
`handoffs/`. It must be copy-pasteable into another system with no attachments.

Required sections:

```
TASK / OBJECTIVE / WORK PERFORMED / KEY FINDINGS
FACTS / CALCULATIONS / OBSERVATIONS / INTERPRETATIONS / HYPOTHESES / ASSUMPTIONS
DECISIONS / FILES CREATED / FILES MODIFIED
EXPERIMENTS / RESULTS / FAILURES / LIMITATIONS
OPEN QUESTIONS / RECOMMENDATION / NEXT ACTION
```

The reviewer is explicitly asked to attack: novelty, methodology, assumptions, experimental design,
statistical validity, interpretation, scope, hidden bias, simulation bias, data leakage, test-set
contamination, uncertainty calibration, and unsupported conclusions.

**The purpose is independent criticism, not confirmation.** A handoff report that reads as a
summary of achievements has failed at its job.
