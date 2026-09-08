# AURA — Research workflow

**Question this document answers:** *I have a question I want to investigate. What do I
actually do, step by step?*

---

## The whole loop

```
 1. write experiments/<ID>/spec.yaml         (pre-register)
 2. python -m aura validate <ID>             (reject before computing)
 3. write experiments/<ID>/experiment.py     (execute(context) -> ExecutionResult)
 4. python -m aura run <ID>                  (gates, provenance, packaging)
 5. read results/<ID>/report.md              (what was measured)
 6. read results/<ID>/handoff.md             (what to attack)
 7. python -m aura verify <ID>               (confirm nothing moved)
```

## 1. Pre-register

Create `experiments/<ID>/spec.yaml`. Field-by-field rationale is in
[`EXPERIMENT_SCHEMA.md`](EXPERIMENT_SCHEMA.md); start from
`experiments/DEMO-0001/spec.yaml`.

Write the **prediction before running anything**. It costs nothing at this stage and is
the only thing that later distinguishes a confirmed prediction from a rationalised result.
If a numerical prediction can be derived in closed form, put the number in the
specification — every AURA experiment that did this could then test it unrefitted.

Declare a `validity_envelope`. If you cannot say what regime your model is valid in, that
is worth discovering now rather than after a run.

## 2. Validate

```bash
python -m aura validate DEMO-0001
```

Every problem is listed at once; exit 0 means valid. This runs before any computation, so
a malformed specification costs a second rather than an afternoon.

## 3. Write the experiment

```python
# experiments/<ID>/experiment.py
from typing import Any, Mapping
from aura.evidence import EvidenceClass, Statement
from aura.montecarlo import plan_sample_size, run as mc_run
from aura.runner import ExecutionResult

def execute(context: Mapping[str, Any]) -> ExecutionResult:
    spec = context["spec"]
    ...
    return ExecutionResult(
        statistics={...},                       # what you measured
        envelope_observations={"alpha": [lo, hi]},   # feeds the envelope gate
        numerical={"n_nonfinite": 0, "dt": dt, "sample_dt": sample_dt},
        data={"planned": n, "actual": completed, "failed_trials": failed},
        achieved={"half_width": iv.half_width, "required_n": n, "actual_n": completed},
        convergence={"trace": trace, "max_final_shrink": 0.25},
        interpretations=[Statement(EvidenceClass.INTERPRETATION, "...")],
        limitations=["..."],
        deviations=[],
    )
```

**Report observations honestly and let the gates judge them.** `DEMO-0002` is deliberately
not defensive: it does not check its own envelope, reports what it saw, and is rejected by
the framework. That is the intended division of labour — the researcher's code should not
have to remember.

Every field of `ExecutionResult` feeds a gate. An experiment that cannot report its
envelope observations cannot pass the envelope gate, by design.

## 4. Run

```bash
python -m aura run DEMO-0001
```

The runner validates, captures provenance, runs preflight gates, executes, runs runtime /
post / statistical gates, writes the evidence package, transitions the registry status
with a recorded reason, and writes a failure record if any gate rejected the run.

**Possible outcomes:**

| Status | Meaning | Conclusion emitted? |
|---|---|---|
| `COMPLETED` | Valid, precise enough | yes |
| `INCONCLUSIVE` | Valid, but did not reach its declared precision | yes, with the shortfall stated |
| `INVALID` | Preconditions did not hold | **no** |
| `FAILED` | Execution did not complete, or a check failed | **no** |

## 5. Read the report

`results/<ID>/report.md` has a fixed structure: research question, hypothesis, prediction,
design, assumptions, configuration, gates, execution, results, statistical uncertainty,
failures, deviations from pre-registration, evidence classification, what the evidence
supports, what it does **not** support, limitations, reproducibility, final decision.

Two things it will never do:

- **convert a number into a conclusion** — it renders what was measured and separates that
  from what a researcher inferred;
- **emit a conclusion from a rejected run** — instead it says so, and its "what the
  evidence supports" section reads **Nothing.**

Supply interpretations from your experiment via `Statement(EvidenceClass.INTERPRETATION,
...)`. Supplying one with a *measured* class (FACT / CALCULATION / OBSERVATION) raises:
measured content must come from recorded artefacts, not from prose.

## 6. Get it reviewed

`results/<ID>/handoff.md` is self-contained — no repository access needed — and ends with
**"What should another researcher try to prove wrong?"** Send it to a colleague or another
model with the instruction to attack it.

The default review questions it always asks:

- Is the declared validity envelope the right one, or just a bound on what this
  configuration happens to produce?
- Is the prediction falsifiable as written, or could any outcome be read as consistent?
- Does the precision target address the question being asked, or the one cheap to measure?
- What is being assumed silently?
- Would someone else, from the recorded configuration, get these numbers?

## 7. Compare — carefully

```bash
python -m aura compare EXP-0010 EXP-0011
```

Differences in model identifier, model version, datasets or controlled variables are
**blocking**: the metrics are different quantities and comparing them is an error. The tool
says `NOT COMPARABLE` and still shows the values, labelled as uninterpretable.

This exists because EXP-0011 compared cases with differently-shaped admissible hypothesis
sets and nothing noticed.

---

## Conventions

- Parameters live in configuration, never inline in code.
- Every stochastic component takes an explicit seed; global RNG state is never used.
- Before an expensive run: the registry entry exists, the validation suite passes, and the
  runtime/storage forecast is grounded in a *measurement* — run a pilot.
- Prefer the simplest method that answers the question. If a χ² threshold matches the
  sophisticated method, **that is the finding**.
- Write documents a critic could use against you. That is what they are for.

## When something goes wrong

Record it. `python -m aura failures` lists the registry; a gate rejection writes a record
automatically. Fill in `root_cause`, `correction` and `verification`, and — where the
failure represents a class of mistake — add a regression test and name it in
`became_test`. See [`FAILURE_MANAGEMENT.md`](FAILURE_MANAGEMENT.md).

## Stopping

The workflow includes stopping. `INVALID` and `INCONCLUSIVE` are first-class outcomes, and
the historical record in this repository ends with a cancelled experiment and a failed
novelty gate. If the evidence says the line of work is finished, recording that is a
result — see
[`CASE_STUDY_AURA_RESEARCH_TERMINATION.md`](CASE_STUDY_AURA_RESEARCH_TERMINATION.md).
