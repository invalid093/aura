# AURA — Phase 0 Research Report

**Project:** AURA — Autonomous Uncertainty & Reliability Architecture
**Phase:** 0 — Research reconnaissance, scientific definition, computational infrastructure
**Date:** 2026-09-08
**Status:** Complete, with unresolved items explicitly marked
**Recommendation:** Proceed to **Phase 1a only** (three gates). Do not begin implementation beyond them.

Evidence classes used throughout: `FACT` / `CALCULATION` / `OBSERVATION` / `INTERPRETATION` /
`HYPOTHESIS` / `ASSUMPTION` / `LIMITATION` (`docs/methodology.md` §2).

---

## Executive summary

Phase 0 concludes that **AURA is worth building — in a substantially narrower form than originally
proposed, and only after three cheap gates that could each end it.**

The original research question was too broad to be testable. It has been replaced by a question
with an analytic ground truth, a pre-registered falsification condition, and a specific
previously-unmeasured quantity at its centre.

The most important finding of Phase 0 is uncomfortable: **there is direct published evidence
against AURA's central hypothesis.** A 2026 study of confidence-gated autonomy found that seven
different uncertainty estimators produced essentially identical act/defer decisions, and that the
threshold mattered far more than the estimator. AURA's stated reason for expecting a different
result is an argument, not evidence. The design has therefore been built so that reproducing that
negative result is itself a publishable outcome.

**On current evidence the most likely outcome is that the primary hypothesis (H1) is falsified and
the secondary one (H3) is supported.** That combination is a good result and is planned for.

---

## 1. What problem is AURA investigating?

An autonomous aircraft that detects an anomaly must decide what to do. That decision depends on how
much it can trust its own diagnosis — and there are two structurally different reasons a diagnosis
may be untrustworthy:

- **Evidential ambiguity ($A$):** two or more fault hypotheses explain the measurements equally
  well. The information is simply not present in the available sensors at this flight condition.
- **Competence loss ($N$):** the operating point lies outside the conditions the diagnostic system
  was developed for, so its outputs are unreliable even when they look clean.

These call for **different responses**. Ambiguity calls for acting on what the candidate hypotheses
share. Competence loss calls for escalation. A single scalar confidence cannot separate them.

AURA investigates whether representing them separately changes what the aircraft actually does.

## 2. Why does the problem matter?

`FACT.` Air data sensor faults — pitot blockage, static obstruction, AoA vane sticking — have
caused transport-category accidents and are a documented, physically-modelled failure class
(LIT-0033, LIT-0034).

`FACT.` Run-time assurance is the standardised architecture (ASTM F3269, LIT-0052) for bounding
functions that cannot be conventionally verified. It switches control based on a monitor's output.

`OBSERVATION.` That architecture assumes the monitor is trustworthy. The reliability of the monitor
*under conditions it was not developed for* is the assumption nobody has tested.

`INTERPRETATION.` A false escalation costs mission capability; an unsafe continuation costs the
aircraft. Getting the distinction right is where the safety value lies — and it is precisely where
a scalar confidence is weakest.

## 3. What has already been done?

Four mature but weakly connected literatures. Full treatment in `LITERATURE_REVIEW.md`.

- **Aircraft FDI** — analytical redundancy, geometric decoupling, integrity monitoring, MMAE /
  Kalman-filter banks. Deterministic or probabilistic, rarely evaluated as *calibrated*.
- **Structural diagnosability** — isolability matrices, MSO sets, sensor placement, mode-dependent
  test selection. Used at design time only.
- **Deep UQ under distribution shift** — thoroughly benchmarked, almost entirely on rotating
  machinery.
- **Uncertainty-gated autonomy** — RTA, simplex, competence-aware systems; and a strong recent
  negative result on estimator choice.

## 4. What does the literature establish?

1. Calibration degrades under shift; in-distribution calibration does not transfer (LIT-0009, LIT-0005).
2. Deep ensembles are the most robust practical UQ method under shift (LIT-0005, LIT-0006).
3. ECE is not a proper scoring rule and can be trivially gamed (LIT-0010, LIT-0011).
4. Structural analysis determines isolability from equation structure, and isolability is
   mode-dependent (LIT-0001, LIT-0068).
5. MMAE produces a principled fault posterior with a known lock-in failure mode (LIT-0043, LIT-0044).
6. Threshold-gated deferral works, but the *threshold* dominates the *estimator* (LIT-0012).
7. Aircraft sensor faults have well-documented physical models (LIT-0034).

## 5. What remains unresolved?

1. Whether UQ-under-shift results transfer to flight dynamics with a state estimator in the loop.
2. **Whether classical MMAE fault posteriors are calibrated.** No retrieved source has checked.
3. **How much novelty gating suppresses genuine fault detection when shift and fault co-occur.**
   Stated as a limitation by the closest prior work (LIT-0004); left unmeasured.
4. Whether learned uncertainty agrees with analytically-derived indistinguishability.
5. Whether the estimator-equivalence result survives when estimators read structurally different
   evidence.
6. Whether abstention should be decomposed by *reason*.

## 6. What candidate research questions exist?

Six were developed and scored (`RESEARCH_DIRECTION_COMPARISON.md`): RD-A uncertainty under shift;
RD-B physics/data hybrids; RD-C diagnosability limits; RD-D abstention; RD-E degraded-mode
selection; RD-F self-aware health management. All are retained in
`research/hypotheses/CANDIDATE_RESEARCH_QUESTIONS.md`.

## 7. Which question is strongest?

**RD-G**, a synthesis of RD-C, RD-D and RD-F, sharpened against the RD-E objection:

> When an autonomous aircraft's operating regime departs from the conditions under which its
> diagnostic system was developed, does representing evidential ambiguity separately from
> competence loss produce better act / abstain / escalate decisions than a single scalar
> confidence — and does that separation survive when regime shift and fault onset occur
> simultaneously?

## 8. Why is it strongest?

Three reasons, in order of weight:

1. **There is ground truth for the uncertainty itself.** Structural isolability, computed per flight
   condition, provides an analytic reference for what the ambiguity component *should* say. UQ
   research is normally handicapped by having no such reference.
2. **There is a specific, pre-registered way to fail.** LIT-0012's equivalence result is adopted as
   the falsification condition rather than argued away.
3. **It measures a quantity the closest prior work explicitly declined to measure** (LIT-0004's
   stated limitation → H3), and that quantity is method-independent, so it yields a result whether
   or not AURA's own method works.

The rejected alternatives, and why, are recorded in `ADR-0002`.

## 9. What hypothesis should be tested?

**H1 (primary).** A decision policy over $(A, N)$ achieves lower expected decision cost at matched
autonomy coverage than the best single-scalar confidence gate, under combined regime-and-fault shift.

Secondary: **H2** identifiability of the decomposition (a *gate on interpreting H1*); **H3**
shift/fault confounding; **H4** MMAE posterior calibration; **H5** ambiguity-set coverage.
Full statements: `docs/hypotheses.md`.

## 10. What would falsify it?

H1 is falsified if **either**:
- the 95% bias-corrected bootstrap CI on the paired expected-cost difference contains zero, **or**
- act/abstain/escalate decisions agree with the best scalar baseline at >95% at matched coverage.

Equivalence is tested explicitly (TOST, pre-declared margin δ = 2% of baseline cost), because a
non-significant difference is not evidence of equivalence.

AURA is **abandoned** if H2 and H3 are both falsified, if a systematic search closes gaps G4 and G6,
or if EXP-0002 shows flight-condition-invariant isolability.

## 11. What aircraft model is required?

`AeroBenchVVPython` — the open Python F-16 built on NASA TP-1538 aerodynamics. Seven options were
surveyed (`AIRCRAFT_MODEL_SURVEY.md`, `ADR-0003`).

The governing requirement is **analysable equations**, not fidelity. The model is not chosen because
it is an F-16; a small-UAS model would have won on structural analysability but its narrow envelope
makes regime shift physically meaningless. NASA's GTM has the best fault-research heritage but
requires MATLAB.

`ASSUMPTION A-SIM-01:` this is a *representative* nonlinear high-performance aircraft, **not** a
validated F-16. No result licenses a claim about a real aircraft.

## 12. What sensors are required?

Thirteen channels: body rates, body specific forces, air data ($V_t, \alpha, \beta$), barometric
altitude, attitude. **GPS and magnetometer are excluded.**

The binding constraint is unusual: the suite must be *small enough that some faults are genuinely
indistinguishable*, because H2 requires a non-trivial ambiguity structure.

`ASSUMPTION A-SEN-01` — this is the most questionable choice in the design, and is recorded as such.
A GPS-included sensitivity run (EXP-0009) is **mandatory and declared in advance** (`ADR-0005`). If
AURA's advantage disappears with GPS, the honest finding is that the decomposition matters only in
under-determined suites, and that becomes the headline.

## 13. What faults are required?

Seven modes: nominal (F0); sensor bias (F1), scale-factor error (F2), drift (F3), stuck (F4),
increased noise (F5); elevator effectiveness loss (F6).

F6 exists specifically to form a physically-motivated ambiguity pair with F2 on the pitch-rate
channel. `ASSUMPTION A-FLT-03` — that this pair is *flight-condition-dependent* — is critical and is
tested by EXP-0002.

Intermittent faults, cascades, icing, structural damage and multi-fault combinations are excluded:
they enlarge the hypothesis space without sharpening RQ-1 and would confound H2's ground truth.

## 14. What baselines are required?

B0 fixed-threshold $\chi^2$ residual detector; B1 MMAE / Kalman-filter bank; B2 deterministic NN +
softmax gate; B3 deep ensemble + entropy gate; **B4 ensemble PNN + epistemic OOD gate (the closest
prior work)**; B5 conformal prediction sets; plus Chow's rule with an oracle posterior as a
reference bound.

**B4 is decisive. Any H1 result reported without B4 is not a result.** Equal tuning budgets are
logged, and if AURA wins only against an untuned B4 the result is void (TV-D2).

## 15. What metrics are required?

Primary: **expected decision cost at matched coverage**, reported as curves over the cost ratio
$\rho = c_{\text{unsafe}}/c_{\text{escalate}} \in \{5,10,30,100\}$. A method that wins at only one
$\rho$ has not won — declared before results exist.

Then: proper scoring rules (NLL, Brier); act/defer/escalate agreement; $\rho(A,N)$ and each
component's association with its ground truth; MDR-vs-shift gap; standard FDI metrics (FAR, MDR,
detection latency, isolation accuracy *conditioned on structural isolability*); risk–coverage
curves. **ECE is secondary and always labelled.**

## 16. How should OOD / distribution shift be tested?

Six axes: S1 flight regime, S2 parameter, S3 sensor, S4 model structure, S5 fault, **S6 combined**.
S6 is primary — it is where H3 lives.

S4 is the strongest axis because it introduces *unmodelled structure* (an alternate aerodynamic
representation, or an independent implementation) rather than mis-specified parameters. Parameter
randomisation alone is a weak OOD test — a criticism AURA applies to itself.

**A measured shift magnitude is reported alongside every nominal axis level. If measured shift is
small, the OOD claim is dropped regardless of the design** (TV-M3).

## 17. What experimental design should be used?

Full factorial over fault mode × magnitude × onset × flight condition × shift axis × method ×
≥30 seeds, with strict development / validation / **frozen test** separation, splits by scenario
(never by time window), and exactly **one** primary confirmatory comparison. Details in
`EXPERIMENTAL_DESIGN_PRELIMINARY.md`.

Staged execution: EXP-0001 → EXP-0002 → … → EXP-0009, each gating the next. **No learning code is
written before EXP-0002 passes.**

## 18. What are the major threats to validity?

Twenty-three catalogued in `THREATS_TO_VALIDITY.md`. The three that remain **unmitigated**:

- **TV-N1** — the novelty claim rests on a non-systematic search.
- **TV-D1** — residual simulation bias. Even the strongest OOD axis stays within one aerodynamic
  data lineage; real unmodelled dynamics are not represented.
- **TV-D9** — one airframe, one sensor suite, seven fault modes.

All three must appear in the limitations section of any output.

## 19. What datasets are available?

`DATASET_SURVEY.md`. ALFA (LIT-0027) is the only open real fixed-wing set with labelled fault type
and onset — but its faults are actuator/engine, not sensor, and post-fault flight totals ~13 minutes.
DASHlink and NGAFID label operational anomalies and maintenance events, neither of which supports
fault isolation. BASiC is sensor-focused but multirotor and simulation-dominant. UAV-SEAD is
unverified and must be checked early (A-7).

**No open dataset combines fixed-wing dynamics, sensor-fault ground truth, and a controlled shift
axis.** AURA must generate its primary data — and the resulting benchmark has value independent of
the hypothesis.

## 20. How should data be stored?

Four layers (RAW → PROCESSED → DERIVED → RESULTS), each dataset with a manifest, checksum and a
parent chain that must resolve back to RAW. Parquet + zstd, `float32`. Git holds code,
configuration, manifests and metrics; the disk holds the data.
`infrastructure/data_management.md`, `ADR-0004`.

## 21. How much storage is expected?

`CALCULATION` (assumptions stated so it can be corrected after measurement): 30 s runs at 100 Hz,
~48 channels, float32 → 576 kB/run uncompressed; ~190 kB/run at an assumed 3× compression.

| Stage | Runs | With derived artefacts |
|---|---|---|
| Pilot | 200 | 57 MB |
| Medium | 5,000 | 1.4 GB |
| Full dev+val | 50,000 | 14 GB |
| Frozen test | 10,000 | 2.9 GB |
| **Project total (×1.5 repeats)** | — | **≈ 28 GB** |

**Decision: local disk only. No Git LFS, no cloud, no database.** Revisit above 100 GB.
Runtime assumption (2 s/run → ~28 core-hours for the full set) is `A-INF-02` and **must be measured
in EXP-0001**; if runtime exceeds 10 s/run the experiment is re-scoped rather than run anyway.

## 22. How should experiments be reproduced?

Parameters in version-controlled configuration, never in code. Every run records commit,
configuration hash, dataset IDs, hierarchical per-component seeds, environment lockfile, BLAS and
thread count, runtime and output size. **Determinism is verified bitwise, not assumed.** Figures are
generated by committed scripts and never hand-edited. A validation suite (manifests, leakage,
determinism, frozen-set integrity, metric correctness, label-shuffle control) blocks any
confirmatory experiment that fails it. `infrastructure/reproducibility.md`.

## 23. What should be built next?

**Phase 1a — three gates only.** Each is cheap and each can end the project.

| Order | Action | Can it end the project? |
|---|---|---|
| 1 | **Systematic literature search** (Scopus/WoS/IEEE/AIAA) + citation sweep from LIT-0004 and LIT-0005; read LIT-0033 manually | **Yes** — if G4/G6 are closed |
| 2 | Verify licences: AeroBenchVVPython (A-1), Fault Diagnosis Toolbox, ALFA (A-6) | Yes — blocks the model choice |
| 3 | **EXP-0001** — runtime, storage, determinism, step-size convergence, float32 check | Yes — forces re-scope |
| 4 | **EXP-0002** — structural model + isolability matrix at ≥3 flight conditions | **Yes — the decisive gate** |

Only if all four pass: EXP-0003/0004 verification, then the pilot.

## 24. What should explicitly **not** be built?

`docs/scope.md` gives the full list with reasons. The most important exclusions:

- **Fault-tolerant control / reconfiguration** — confounds diagnosis quality with control quality.
- **Prognostics / RUL** — a different question and literature.
- **Human-subject studies** — escalation is treated as a cost, not a human process.
- **Real-time / embedded implementation** — computational cost is not a variable in RQ-1.
- **Reinforcement learning for the decision policy** — three actions and an explicit cost model;
  a learned policy would confound uncertainty quality with policy-learning quality.
- **Large sequence or foundation models** — no evidence they would change the answer.
- **Higher-fidelity aerodynamics** — fidelity is a cost; AURA needs analysable equations.
- **Any dashboard or UI** — no scientific information.
- **Anything on DASHlink / NGAFID** — their labels cannot support fault isolation.

---

## Is AURA worth building?

**Yes, conditionally.** The reasoning, stated so it can be attacked:

**For.** The question has an analytic ground truth, which is rare in UQ research. It has a
pre-registered falsification condition drawn from a published adversarial result rather than
invented to be beatable. Its central secondary hypothesis (H3) measures a quantity the closest
prior work stated and declined to measure, is method-independent, and therefore yields a result
regardless of whether AURA's own method succeeds. The benchmark itself fills a documented gap.
Every gate is cheap and comes before the expense.

**Against, and honestly.** The novelty rests on a non-systematic search (TV-N1). The closest prior
group is better placed than AURA to close the same gap (TV-N2). The single most likely outcome is
that the primary hypothesis is falsified. Residual simulation bias cannot be fully removed. The
sensor-suite choice that makes the effect measurable (A-SEN-01) is also the choice most likely to
limit generality.

**Judgement.** The design's value does not depend on H1 being supported, which is the property that
makes it worth starting. What it does depend on is EXP-0002 — and that costs almost nothing to run.

**Proceed to Phase 1a. Do not build beyond the gates.**

---

## Phase 0 stop condition

| Item | Status | Where |
|---|---|---|
| Research problem defined | ✔ | `docs/research_question.md` |
| Research gap investigated | ✔ **provisional (TV-N1)** | `research/gaps/GAP_MATRIX.md` |
| Candidate research questions compared | ✔ | `RESEARCH_DIRECTION_COMPARISON.md` |
| Primary RQ selected | ✔ | `ADR-0002` |
| Hypothesis defined | ✔ | `docs/hypotheses.md` |
| Falsification criteria defined | ✔ | `docs/hypotheses.md` |
| Aircraft model justified | ✔ **blocked on A-1 (licence)** | `AIRCRAFT_MODEL_SURVEY.md`, `ADR-0003` |
| Sensor suite justified | ✔ **with a recorded reservation (A-SEN-01)** | `ADR-0005` |
| Fault taxonomy justified | ✔ **A-FLT-03 pending EXP-0002** | `EXPERIMENTAL_DESIGN_PRELIMINARY.md` §2 |
| Baselines identified | ✔ | §7 |
| Metrics identified | ✔ | §5, §6 |
| Uncertainty definition established | ✔ | §3 |
| OOD / shift framework established | ✔ | §4 |
| Experimental design established | ✔ **preliminary; gated** | `EXPERIMENTAL_DESIGN_PRELIMINARY.md` |
| Threats to validity documented | ✔ **3 unmitigated** | `THREATS_TO_VALIDITY.md` |
| Dataset strategy established | ✔ | `DATASET_SURVEY.md` |
| Storage strategy established | ✔ **forecast unverified (A-INF-02/03)** | `ADR-0004` |
| Repository established | ✔ **local git; not published** | this repository |
| Repository organisation established | ✔ | `ADR-0001` |
| Reproducibility strategy established | ✔ | `infrastructure/reproducibility.md` |
| Archive strategy established | ✔ | `infrastructure/experiment_management.md` §6 |
| Reporting strategy established | ✔ | `infrastructure/reporting.md` |
| Cross-AI handoff established | ✔ | `handoffs/PHASE0_RESEARCH_HANDOFF.md` |
| Phase 0 final report completed | ✔ | this document |
| Phase 0 research handoff completed | ✔ | `handoffs/PHASE0_RESEARCH_HANDOFF.md` |

### Explicitly UNRESOLVED

1. **Novelty is unverified** (TV-N1). Blocks any novelty claim.
2. **Licences unverified** (A-1, A-2, A-6). Blocks adoption of the model, toolbox and dataset.
3. **Runtime and compression are assumptions** (A-INF-02, A-INF-03). Blocks the storage/runtime forecast.
4. **Flight-condition-dependent isolability is unverified** (A-FLT-03). **Blocks the entire design.**
5. **LIT-0033 unread** — retrieval failed; must be read manually.
6. **Determinism unverified** (A-INF-05). Blocks reproducibility claims.
7. **Licensing deliberately undecided** (ADR-0006). The repository carries no licence, so no reuse
   permission is offered. This is not an oversight — outbound licensing cannot be decided before
   the inbound obligations of the model, toolbox and dataset are verified (A-1, A-2, A-6).

### Decided, not unresolved

- **GitHub publication is deferred by researcher decision** (2026-09-08). The repository is local
  only. It is maintained to the project's public repository policy — scientific record rather than
  full laboratory, no personal information, no bulk data, no implied reuse permission — so that it
  is publish-ready whenever that decision changes. The pre-push gate is
  `infrastructure/public_release_checklist.md`.
