# AURA — Current State

*Kept short by design. Updated whenever any line below changes.*
*Last updated: 2026-09-08 (end of Phase 0)*

---

**CURRENT RQ:**
When an autonomous aircraft's operating regime departs from its diagnostic development envelope,
does representing *evidential ambiguity* (A) separately from *competence loss* (N) produce better
act / abstain / escalate decisions than a single scalar confidence — and does the separation
survive when regime shift and fault onset occur simultaneously?
→ `docs/research_question.md`

**CURRENT HYPOTHESIS:**
H1 — a decision policy over (A, N) achieves lower expected decision cost at matched autonomy
coverage than the best single-scalar confidence gate, under combined shift.
Gated on H2 (are A and N actually separable?). Falsified if decision agreement with the best
scalar baseline exceeds 95% at matched coverage, or the cost-difference CI contains zero.
→ `docs/hypotheses.md`

**BEST VALIDATED RESULT:**
None. No experiment has been run. Phase 0 produced definitions, design and infrastructure only.

**KEY FAILURE:**
None yet (no experiments). One Phase 0 process failure: full-text retrieval of LIT-0033
(DX-2024 air data sensor diagnosis survey) failed; it must be read manually in Phase 1.

**KEY LIMITATION:**
Three, all unmitigated:
1. TV-N1 — the novelty claim rests on a non-systematic search. A systematic database search is a
   hard gate before any novelty claim.
2. TV-D1 — residual simulation bias. Even the strongest OOD axis stays within one aerodynamic
   data lineage; real unmodelled dynamics are not represented.
3. TV-D9 — one airframe, one sensor suite, seven fault modes.

**NEXT SCIENTIFIC QUESTION:**
**EXP-0002: does structural isolability actually vary with flight condition for this model,
sensor suite and fault set?**
If it does not, A has no mode-dependent ground truth, H2 loses its reference, and the design must
change. This costs almost nothing to answer and can invalidate the project — so it runs first,
before any learning code is written.
