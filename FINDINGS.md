# AURA — Current State

*Kept short by design. Updated whenever any line below changes.*
*Last updated: 2026-09-08 (EXP-0011 complete)*

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

**BEST VALIDATED RESULT:**
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

**NEXT SCIENTIFIC QUESTION:**
**EXP-0012 — does support misspecification generalise from magnitude to the fault *taxonomy*?**
Hold out a fault class the model has never seen, present it, and measure how confidently it is
misassigned as the observation window grows. This is the same mechanism as EXP-0011's headline at a
much larger scale, it is the assumption every diagnostic system in this literature makes, and it is
the first experiment in the sequence whose expected outcome would genuinely support AURA's premise
-- which is a reason to design it adversarially rather than optimistically.

**Three experiments have now failed to find the diagnostic ambiguity AURA was designed around.**
It is absent at realistic sensor noise, absent with unknown magnitude, and transient where it exists
at all. What they *have* repeatedly surfaced is a different and better-evidenced problem: misplaced
confidence. Still no learning component, uncertainty estimator or decision layer.

**AWAITING RESEARCHER DECISION:**
- **Licensing (ADR-0007):** accept GPL-3.0 and use AeroBench, source a permissive airframe, or keep
  GFW-1 and accept TV-D10 permanently.
- **Design scope:** is one verdict flip in 153 pairs enough condition-dependence to justify a
  condition-dependent ambiguity model, rather than a single condition-independent ambiguity group?
