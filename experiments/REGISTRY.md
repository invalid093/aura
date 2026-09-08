# Experiment Registry

Index of all AURA experiments. One YAML file per experiment: `experiments/EXP-XXXX.yaml`.
Policy: `infrastructure/experiment_management.md`.

**A registry entry is created with status `PLANNED` before the experiment runs.**

| ID | Title | Type | Hypothesis | Status | Gate? | Results |
|----|-------|------|-----------|--------|-------|---------|
| EXP-0001 | Single-run instrumentation: runtime, storage, determinism, step-size convergence | exploratory | — | `PLANNED` | **Yes** | — |
| EXP-0002 | Structural model + isolability matrix at >=3 flight conditions | exploratory | H2 (ground truth existence) | `PLANNED` | **Yes — can invalidate the design** | — |
| EXP-0003 | Fault-injection verification: each mode produces its expected residual signature | exploratory | — | `PLANNED` | Yes | — |
| EXP-0004 | Metric implementation verification on the LTI model against known answers | exploratory | — | `PLANNED` | Yes | — |
| EXP-0005 | Pilot (~200 runs, B0/B1/AURA): is diagnosis neither trivial nor impossible? | exploratory | — | `PLANNED` | Yes | — |
| EXP-0006 | Medium (~5,000 runs, all baselines, dev + validation) | exploratory | — | `PLANNED` | Yes | — |
| EXP-0007 | **Primary confirmatory**: H1 at shift axis S6 on the frozen test set | **confirmatory** | H1 (with H2, H4, H5 secondary) | `PLANNED` | — | — |
| EXP-0008 | ALFA external validity check (detection sub-problem only) | exploratory | — | `PLANNED` | — | — |
| EXP-0009 | Sensitivity: GPS included; cost-ratio sweep; independent-implementation test | exploratory | — | `PLANNED` | — | — |

Note: H3 (shift/fault confounding) is evaluated from EXP-0007 data but is **method-independent** —
it is a property of novelty gating in general, and its result stands whether or not H1 holds.

## Statuses

`PLANNED` | `RUNNING` | `COMPLETED` | `FAILED` | `INVALID` | `SUPERSEDED` | `ARCHIVED`

Nothing is deleted. `FAILED` and `INVALID` entries are retained with reasons.
