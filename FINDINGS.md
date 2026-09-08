# AURA — Current State

*Kept short by design. Updated whenever any line below changes.*
*Last updated: 2026-09-08 (EXP-0002 complete)*

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

**KEY FAILURE:**
**FAIL-0001 — flight condition FC-4 departs controlled flight.** Its nominal run stalls (α reaches
31.5°, airspeed changes 27.7 m/s, 353 m of altitude lost). It returned the most favourable numbers
in the experiment — a perfect diagonal and cross-condition correlation of 0.37–0.46 — which was
divergence amplification, not diagnosability. **Excluded; the validity attack turned the
headline result into a discarded artefact.** Root cause was a defect in the pilot, which checked
closed-loop boundedness at one condition only and mistook trim convergence for flyability.

**KEY LIMITATION:**
1. EXP-0002 is **deterministic and noise-free** — its distances are upper bounds on what any
   estimator could achieve from a single noisy realisation.
2. **TV-D10 (HIGH, unmitigated):** the aircraft model is self-implemented and its parameters were
   chosen by the experimenter, after AeroBenchVVPython was found to be GPL-3.0 (ADR-0007).
3. Condition-dependence is **modest at the pre-declared threshold**: only 1 pair of 153 changes
   verdict. The verdict rests on the continuous rank structure, not the binary matrix.
4. Novelty remains unverified (TV-N1) — a systematic literature search is still outstanding.

**NEXT SCIENTIFIC QUESTION:**
**EXP-0010 — how much of the measured distinguishability survives measurement noise on a single
realisation?** This is the largest limitation and a prerequisite for hypothesis H3. No learning
component, uncertainty estimator or decision layer is built until it is answered: EXP-0002 shows the
substrate exists, not that a learned estimate is needed to exploit it.

**AWAITING RESEARCHER DECISION:**
- **Licensing (ADR-0007):** accept GPL-3.0 and use AeroBench, source a permissive airframe, or keep
  GFW-1 and accept TV-D10 permanently.
- **Design scope:** is one verdict flip in 153 pairs enough condition-dependence to justify a
  condition-dependent ambiguity model, rather than a single condition-independent ambiguity group?
