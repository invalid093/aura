# Experiment Registry

Index of all AURA experiments. One YAML file per experiment: `experiments/EXP-XXXX.yaml`.
Policy: `infrastructure/experiment_management.md`.

**A registry entry is created with status `PLANNED` before the experiment runs.**

| ID | Title | Type | Hypothesis | Status | Gate? | Results |
|----|-------|------|-----------|--------|-------|---------|
| EXP-0001 | Single-run instrumentation: runtime, storage, determinism, step-size convergence | exploratory | — | `PLANNED` | **Yes** | — |
| EXP-0002 | Response-based fault distinguishability at >=3 flight conditions | exploratory | H2 (ground-truth premise) | **`COMPLETED` — PASS** | **Yes — was the design gate** | `results/validation/EXP-0002/` · [report](../reports/technical/EXP-0002_STRUCTURAL_ISOLABILITY.md) |
| EXP-0003 | Fault-injection verification: each mode produces its expected residual signature | exploratory | — | `PLANNED` | Yes | — |
| EXP-0004 | Metric implementation verification on the LTI model against known answers | exploratory | — | `PLANNED` | Yes | — |
| EXP-0005 | Pilot (~200 runs, B0/B1/AURA): is diagnosis neither trivial nor impossible? | exploratory | — | `PLANNED` | Yes | — |
| EXP-0006 | Medium (~5,000 runs, all baselines, dev + validation) | exploratory | — | `PLANNED` | Yes | — |
| EXP-0007 | **Primary confirmatory**: H1 at shift axis S6 on the frozen test set | **confirmatory** | H1 (with H2, H4, H5 secondary) | `PLANNED` | — | — |
| EXP-0008 | ALFA external validity check (detection sub-problem only) | exploratory | — | `PLANNED` | — | — |
| EXP-0009 | Sensitivity: GPS included; cost-ratio sweep; independent-implementation test | exploratory | — | `PLANNED` | — | — |
| EXP-0010 | **Practical diagnosability under measurement uncertainty** | exploratory | H2, prerequisite for H3 | **`COMPLETED`** | Decision gate | `results/validation/EXP-0010/` · [report](../reports/technical/EXP-0010_MEASUREMENT_UNCERTAINTY.md) |
| EXP-0011 | **Isolation with unknown fault magnitude (composite hypotheses)** | exploratory | H2 | **`COMPLETED`** | Decision gate | `results/validation/EXP-0011/` · [report](../reports/technical/EXP-0011_UNKNOWN_FAULT_MAGNITUDE.md) |
| EXP-0012 | **Unmodelled fault class (support misspecification of the taxonomy)** | exploratory | H2 | `PLANNED` | **Yes — next** | — |
| EXP-0013 | Characterise the pre-isolation transient (first ~5 s) | exploratory | — | `PLANNED` | — | — |

Note: H3 (shift/fault confounding) is evaluated from EXP-0007 data but is **method-independent** —
it is a property of novelty gating in general, and its result stands whether or not H1 holds.

**Sequencing changed after EXP-0002.** EXP-0010 was inserted before EXP-0003 onward, because
EXP-0002 was noise-free and its distances were upper bounds.

**Sequencing changed again after EXP-0010.** EXP-0010 found that at realistic sensor noise there is
*no* ambiguity to be uncertain about ($P_{iso} = 1.000$) — the motivating problem is absent under its
assumptions. Two assumptions must be relaxed before any estimator or decision layer is justified,
because both can only increase ambiguity: **unknown fault magnitude** (EXP-0011) and template/model
error. EXP-0012 characterises the ~5 s transient during which isolation is impossible even with
perfect sensors, which is where EXP-0010 relocated the problem.

## Failures

| ID | Experiment | Category | Summary |
|----|-----------|----------|---------|
| [FAIL-0001](failures/FAIL-0001.md) | EXP-0002 | `EXPERIMENTAL_INVALIDITY` | Flight condition FC-4 departs controlled flight; its perfect-diagonal matrix was divergence amplification and was excluded. It had produced the most favourable-looking numbers in the experiment. |

## Statuses

`PLANNED` | `RUNNING` | `COMPLETED` | `FAILED` | `INVALID` | `SUPERSEDED` | `ARCHIVED`

Nothing is deleted. `FAILED` and `INVALID` entries are retained with reasons.
