# AURA — Current State

*Kept short by design. Updated whenever any line below changes.*
*Last updated: 2026-09-08 (EXP-0010 complete)*

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

**KEY CORRECTION MADE TO OUR OWN WORK:**
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
**EXP-0011 — how much ambiguity does *unknown fault magnitude* create?** EXP-0010 assumed the
diagnoser knows both the fault templates and the fault magnitude exactly, so every probability it
reports is an upper bound. With free magnitude, a bias fault and a scale fault on one channel
intersect *exactly* at the crossover airspeed — the classes genuinely overlap. This is the largest
untested assumption and can only increase ambiguity.

Still no learning component, uncertainty estimator or decision layer. EXP-0010 has just shown the
motivating ambiguity is **absent** at realistic sensor noise under its assumptions; building the
architecture now would build it on the weakest version of its own case.

**AWAITING RESEARCHER DECISION:**
- **Licensing (ADR-0007):** accept GPL-3.0 and use AeroBench, source a permissive airframe, or keep
  GFW-1 and accept TV-D10 permanently.
- **Design scope:** is one verdict flip in 153 pairs enough condition-dependence to justify a
  condition-dependent ambiguity model, rather than a single condition-independent ambiguity group?
