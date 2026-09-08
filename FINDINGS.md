# AURA — Current State

*Kept short by design. Updated whenever any line below changes.*
*Last updated: 2026-09-08 (EXP-0012 complete)*

---

**CURRENT RQ:**
When an autonomous aircraft's operating regime departs from its diagnostic development envelope,
does representing *evidential ambiguity* (A) separately from *competence loss* (N) produce better
act / abstain / escalate decisions than a single scalar confidence?
→ `docs/research_question.md`

**CURRENT HYPOTHESIS:**
H1 — a decision policy over (A, N) achieves lower expected decision cost at matched autonomy
coverage than the best single-scalar confidence gate. Untested; gated on H2.
H2's ground-truth premise has now been tested by EXP-0002.
→ `docs/hypotheses.md`

**TV-N1 NOVELTY GATE (2026-09-08): FAIL. This supersedes every open question below.**
The blocking literature audit Phase 0 required has now been performed, and AURA did not pass it.
Every substantive finding has established prior art: confident misdiagnosis when the true fault is
outside the hypothesis set is **Berk (1966)**; the χ² residual is the classical model-based FDI
consistency test (**Massoumnia et al. 1989** characterised undetectable faults geometrically in
1989); the detectability threshold is the classical *minimum detectable fault* — a named research
object with its own paper title (**Xu 2023, IEEE TAC**); quantitative noise-aware distinguishability
is **Eriksson, Frisk & Krysander (2013)**, the same construct as AURA's deflection coefficient;
near-class rejection failure is the *expected* result of open-set recognition; and excitation-limited
diagnosability with active input design as the remedy is **Scott et al. (2014)** and
**Kong, McMahon & Lahijanian (2025)** — the latter anticipating AURA's entire post-EXP-0012
direction, with theorems, in an aerospace department.

**AURA's own strongest result is the strongest evidence against its novelty:** a closed-form
classical threshold predicts its blind spots in 1502 of 1512 cells (99.3%). A phenomenon predicted
that well by a textbook expression is not an open question.

`NOVELTY GATE: FAIL` · `EXP-0013: CANCEL` · `ML PHASE: NOT JUSTIFIED`
→ `research/literature/TV-N1_LITERATURE_AUDIT.md`

**CUMULATIVE REVIEW (EXP-0002 → EXP-0012) — the most important entry in this file:**
**AURA's original premise is UNSUPPORTED, and the programme was substantially goalpost-shifting.**
Four experiments looked for diagnostic ambiguity under progressively weaker assumptions and did not
find it. The replacement phenomenon — confident misdiagnosis under hypothesis-space mismatch — is
real but its three components are close to textbook, and the **systematic literature search that
Phase 0 declared a blocking gate on any novelty claim has still never been performed (TV-N1)**.
Two of this project's own published claims were corrected by the review: the χ² residual did **not**
pre-exist EXP-0012, and the "23 persistent cells" figure ranges **14–32** across defensible
thresholds.
`EXP-0013 DECISION: DEFER` · `ML PHASE: NOT JUSTIFIED`
→ `research/cumulative_review/EXP_0002_0012_CUMULATIVE_REVIEW.md`

**BEST VALIDATED RESULT:**
**EXP-0012 — a reliability problem finally appears, and it is not the one AURA was designed
around.** When the true fault is absent from the diagnostic library, the system is *confidently
wrong and the goodness-of-fit test stays silent* in **5.8% of all cells and 16.7% at full
observation**. **23 cells remain confidently wrong at the full 18 s window** (range **14–32** across
defensible thresholds), covering all six
unseen faults; **12 of them diagnose a genuinely faulted aircraft as healthy.** Sharpest case: a
partially blocked pitot line is diagnosed as "no fault" with confidence rising **0.133 -> 0.993**
as more data arrives.

**But a simple non-learning test catches most of it.** A chi-square residual, *added to the
framework in EXP-0012* rather than inherited from EXP-0010/0011, 
catches 47-83% of mismatch, and does so **exactly when a closed-form threshold predicts -- 1502 of
1512 cells (99.3%)**, from a prediction registered before the run and not refitted. Control: 56/56
known faults correct, normalised residual 1.000.
Decision gate: **A and D simultaneously.**
-> `reports/technical/EXP-0012_UNSEEN_FAULTS.md`

**PRIOR RESULT:**
**EXP-0011 — being *wrong* about a fault is far worse than being *uncertain* about it, and
uniquely gets worse with more data.** Not knowing the fault magnitude (a 16x range) costs at most
3.3 points of class-isolation accuracy and **0.0001** at the full window. A prior that *excludes*
the true magnitude costs 6.5-13.3 points, and the penalty **grows monotonically** with observation
length (-0.065 at 0.25 s to -0.133 at 18 s). Every other effect measured in this project shrinks
with more data; this one does not, because a sharpening likelihood over a wrong support cannot
self-correct.
All magnitude-induced ambiguity is **transient**: every overlapping class pair resolves by 18 s.
Where overlap exists it is always bias-vs-scale on the same channel, at chance (P = 0.52-0.57),
and only before the aircraft manoeuvres. Closed-form prediction confirmed at r = 0.973, not refitted.
-> `reports/technical/EXP-0011_UNKNOWN_FAULT_MAGNITUDE.md`

**PRIOR RESULT:**
**EXP-0010 — at realistic sensor noise there is no ambiguity to be uncertain about.** With an
optimal classifier and the full observation window, probability of correct 18-way fault isolation is
**1.000** at every valid flight condition, and **zero** of 153 fault pairs are practically ambiguous.
EXP-0002's five-member ambiguity group dissolves: its threshold was conservative by a factor of
sqrt(K*N) ~ 153.
**But isolation takes about 5 seconds.** Even with perfect sensors, P_iso = 0.45 at 0.05 s and does
not reach 0.95 until ~5 s. **The binding constraint on isolation here is time, not noise** — an
outcome none of the five pre-declared decision-gate categories anticipated.
Ambiguity needs 10-19x the reference uncertainty to appear; condition dependence is real but modest
(1.83x spread, fixed ordering, robust to fault magnitude). Temporally correlated noise costs a
further 21%, quantitatively predicted by sqrt((1+rho)/(1-rho)) at r = 0.9993.
-> `reports/technical/EXP-0010_MEASUREMENT_UNCERTAINTY.md`

**PRIOR RESULT (superseded in interpretation, not in substance):**
**EXP-0002 — PASS (thin margin).** In a nonlinear 6-DOF fixed-wing model, deterministic and
noise-free, fault distinguishability is non-trivial and does depend on operating condition:
- A stable five-member ambiguity group {F0, F2_q, F2_α, F4_α, F4_Vt} persists at **all four** valid
  flight conditions (10–11 indistinguishable pairs of 153).
- Cross-condition Spearman correlation of the pairwise distances runs 0.984 (designed control pair,
  matched dynamic pressure) down to 0.658 (extreme pair), **perfectly monotone in
  operating-point separation** — 6 of 6 pairs in rank order.
- One ambiguity was predicted in closed form before simulation and confirmed at **r = 0.979**: a
  bias fault and a scale fault on a regulated channel coincide at V* = b/(k−1) = 50 m/s.
- Robust to step size (ρ ≥ 0.9992), fault magnitude, and run duration. All 90 runs bitwise
  reproducible.
→ `reports/technical/EXP-0002_STRUCTURAL_ISOLABILITY.md`

**KEY CORRECTIONS MADE TO OUR OWN WORK:**
EXP-0011: three defects found by testing and corrected. A code bug excluded the nominal class F0
from the admissible set, biasing precisely the known-vs-unknown-magnitude comparison the experiment
exists to make -- the first run was discarded and the experiment re-run. The pre-registered
detectability floor conflates non-detection with mis-isolation at short windows. Case B as
pre-registered measures prior *misspecification* rather than bounded knowledge; it was kept and
reported, because it produced the experiment's most important finding.
Also: a discrete magnitude grid overstates near-intersection separation by up to 19.9x, so the
primary manifold measure is the continuous minimum over magnitude.

EXP-0010: 
The claim that EXP-0002's ambiguity group "predicted" statistical difficulty was **downgraded after
testing it for circularity**. Per-fault difficulty and deterministic nearest-neighbour distance rank
at Spearman 0.77-0.98, not 1.0 — substantially implied, not independent. Deterministic analysis is a
useful *screening* tool, not a predictor.
-> `results/validation/EXP-0010/circularity_test.json`

**KEY FAILURE:**
**FAIL-0001 — flight condition FC-4 departs controlled flight.** Its nominal run stalls (α reaches
31.5°, airspeed changes 27.7 m/s, 353 m of altitude lost). It returned the most favourable numbers
in the experiment — a perfect diagonal and cross-condition correlation of 0.37–0.46 — which was
divergence amplification, not diagnosability. **Excluded; the validity attack turned the
headline result into a discarded artefact.** Root cause was a defect in the pilot, which checked
closed-loop boundedness at one condition only and mistook trim convergence for flyability.

**KEY LIMITATION:**
1. **TV-M5 (HIGH, new):** EXP-0010 assumes the diagnoser knows the fault templates and magnitudes
   exactly. Every probability it reports is an upper bound of unknown tightness. Template error acts
   exactly like elevated noise, so the realistic regime may be where ambiguity *does* appear — this
   threat could restore AURA's motivation rather than undermine it, which is why it must be measured.
2. **TV-D10 (HIGH, unmitigated):** the aircraft model is self-implemented and its parameters were
   chosen by the experimenter, after AeroBenchVVPython was found to be GPL-3.0 (ADR-0007).
3. Condition-dependence is **modest at the pre-declared threshold**: only 1 pair of 153 changes
   verdict. The verdict rests on the continuous rank structure, not the binary matrix.
4. Novelty remains unverified (TV-N1) — a systematic literature search is still outstanding.

**NEXT SCIENTIFIC QUESTION — superseded by TV-N1 (2026-09-08):**
**There is no scientifically justified next experiment in this branch.** The literature audit below
was the recommended next action; it returned FAIL. EXP-0013 is cancelled, ML remains not justified,
and no further experiment should be designed on the assumption that a novelty claim is available.
Continuing would require either a new research question grounded in a gap the literature actually
declares, or a decision by the researcher to continue for reasons other than novelty (for example
as a methods exercise) — which should be recorded explicitly as such.

*The pre-audit statement is preserved below, unedited, as the historical record:*

**NEXT SCIENTIFIC QUESTION — revised by the cumulative review:**
**Not an experiment.** The cumulative review deferred EXP-0013 in favour of the systematic
literature search (TV-N1) that Phase 0 declared a *blocking gate on any novelty claim* and that four
experiments have run past. At least three of AURA's findings are close to textbook, so nothing here
can be claimed as novel until that gate is closed — and no excitation experiment can fix that.

If the gate clears, the evidence *does* support an excitation direction: UF-003's
distance/threshold ratio peaks at 0.80 when the manoeuvre ends and then **declines** to 0.74, which
is direct evidence that near-manifold failure is excitation-limited rather than time-limited. The
right form of that question is analytical identifiability (*can any admissible excitation succeed?*),
not "try another doublet".

**Four experiments in, AURA's original premise remains unsupported.** Diagnostic ambiguity is absent
at realistic noise, absent under unknown magnitude, and transient where it exists. A *different*
problem is now supported by measurement: misplaced confidence from a wrong hypothesis support. Still
no learning component, uncertainty estimator or decision layer -- and EXP-0012 is the reason not to
build one yet, since most of the problem is solved by a simple non-learning residual added in
EXP-0012.

**AWAITING RESEARCHER DECISION:**
- **Licensing (ADR-0007):** accept GPL-3.0 and use AeroBench, source a permissive airframe, or keep
  GFW-1 and accept TV-D10 permanently.
- **Design scope:** is one verdict flip in 153 pairs enough condition-dependence to justify a
  condition-dependent ambiguity model, rather than a single condition-independent ambiguity group?
