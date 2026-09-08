# AURA — Architecture

**Question this document answers:** *what are the pieces, why do they exist, and how do
they fit together?*

---

## Dependency policy

The framework depends on **Python 3.11+, numpy, and PyYAML** — nothing else. No scipy, no
jsonschema, no pytest.

This is a deliberate trade. It costs a few hundred lines (a probit, a Wilson interval, a
schema validator, a test runner) and buys the property that anyone can clone the
repository and run the whole suite immediately. Special functions are built on
`math.erf`/`erfc`, which are exact, and the one approximation used (Wilson–Hilferty for
χ² quantiles) **refuses to run** outside the regime where it is accurate rather than
silently returning a wrong critical value.

## Module map

```
aura/
├── __init__.py       FRAMEWORK_VERSION (recorded in every provenance record)
├── errors.py         typed exception hierarchy — no silent failure
├── evidence.py       the seven evidence classes; measured vs inferred
├── hashing.py        canonical hashing; checksum manifests
├── seeds.py          deterministic seed derivation
├── statistics.py     probit, chi2, Wilson/normal/order-statistic intervals, sample sizing
├── integrity.py      assertions distilled from real research failures
├── status.py         experiment lifecycle + legal transitions
├── spec.py           the experiment specification (the central artefact)
├── validation.py     preflight specification validation
├── provenance.py     result -> seed chain capture
├── gates.py          the gate architecture + 10 built-in gates
├── montecarlo.py     reusable Monte Carlo engine
├── retention.py      data tiers and retention classes
├── failures.py       the failure registry
├── registry.py       the experiment registry
├── report.py         research report generation
├── handoff.py        independent-review handoff generation
├── compare.py        commensurability checking between experiments
├── runner.py         the lifecycle, wired together
└── cli.py            command-line interface
```

## Layering

Dependencies point downward only; there are no cycles. (`validation` imports
`gates.GATE_REGISTRY` lazily inside a function for exactly this reason.)

```
                          cli
                           │
                        runner
        ┌──────────┬────────┼────────┬───────────┬──────────┐
     report     handoff  registry  compare   failures   retention
        └──────────┴────────┼────────┴───────────┴──────────┘
                   validation │ gates │ provenance │ montecarlo
                           spec │ status
              evidence │ statistics │ seeds │ hashing │ integrity
                          errors
```

## The lifecycle

```
   specification (YAML, content-hashed)
        │
        ▼
   preflight validation ─────────────► SpecificationError (nothing runs)
        │  aura.validation
        ▼
   PREFLIGHT gates ──────────────────► INVALID, no computation performed
        │  provenance, seed policy, frozen-test integrity
        ▼
   execution  (the experiment's own execute(context))
        │                              └─► exception ⇒ FAILED, recorded
        ▼
   RUNTIME gates ────────────────────► INVALID (e.g. envelope excursion)
        │  validity envelope, numerical validity
        ▼
   POST gates ───────────────────────► INVALID / INCONCLUSIVE
        │  data completeness, reproducibility, raw-data immutability
        ▼
   STATISTICAL gates ────────────────► INCONCLUSIVE (precision not met)
        │  precision target, convergence
        ▼
   evidence package + status transition + failure record if rejected
```

**Outcome precedence** is `INVALID > FAIL > INCONCLUSIVE > PASS`. One INVALID gate makes
the whole run uninterpretable regardless of how many gates passed.

## Key design decisions and their rationale

### A gate that cannot be evaluated raises; it never returns PASS

The single most important property in the framework. If `model_validity_envelope` is
declared but no observation was recorded for an envelope variable, the gate raises
`GateError` rather than passing. A framework whose gates can produce a **false PASS** is
worse than no framework, because it converts an unchecked run into a certified one.

### Gates are pure functions of a context dictionary

They take a mapping and return a `GateResult`. No global state, no filesystem reach-in
beyond what the context names. This makes every gate unit-testable in isolation — see
`tests/test_core.py::TestGates`.

### The specification is content-hashed, excluding `status` and `source_path`

Advancing the lifecycle or moving a file must not look like tampering with a
pre-registration; changing the question, hypothesis, prediction, variables, metrics, gates
or precision target must.

### The report generator cannot draw a conclusion

`aura.report` renders what was measured, at what precision, under which assumptions, and
whether the gates permitted interpretation. Interpretations must be supplied by the
researcher, are rendered in a separate section, and are **rejected** if they claim a
measured evidence class. When the gates block, the report emits an explicitly *empty*
"what the evidence supports" section rather than omitting it — so that its emptiness is
visible.

### Experiments are loaded by file path, not import path

Experiment identifiers contain hyphens (`DEMO-0001`), which are not valid Python
identifiers. `aura.cli.load_experiment_module` loads by path and puts the repository root
on `sys.path`.

### Failed Monte Carlo trials are data

A trial that raises becomes a `TrialFailure` with its index, seed and labels — never a
silent drop, which would bias the estimate toward whatever succeeds. If *every* trial
fails, the engine raises: zero samples is not a weak estimate.

## Extending the framework

**Adding a gate:**

```python
from aura.gates import Phase, register, GateResult, Outcome

@register("my_gate", Phase.POST, "What it checks.", required_context=("my_data",))
def _my_gate(ctx):
    ok = ctx["my_data"]["value"] < 1.0
    return GateResult("my_gate", Phase.POST.value,
                      (Outcome.PASS if ok else Outcome.FAIL).value,
                      "detail for the reader", {"value": ctx["my_data"]["value"]})
```

Then declare `my_gate` in a specification's `gates:` list, and return `my_data` from the
experiment's `ExecutionResult`. `aura.validation` rejects a specification naming an
unregistered gate, so a typo cannot silently disable a check.

**Adding an experiment:** create `experiments/<ID>/spec.yaml` and
`experiments/<ID>/experiment.py` exposing `execute(context) -> ExecutionResult`. See
[`RESEARCH_WORKFLOW.md`](RESEARCH_WORKFLOW.md).

## Performance

Measured on the development machine (Python 3.13, numpy 2.5, Windows), best of three:

| Quantity | Value |
|---|---|
| Framework import overhead | ~155 ms (cold process) |
| Monte Carlo throughput | ~73,000 trials/s (trivial trial function) |
| Full `DEMO-0001` lifecycle (8,851 trials, ×2 for the reproducibility check, gates, packaging) | 0.78 s |
| Evidence package size | 21.5 kB across 8 files |
| Full test suite (82 tests) | ~1.7 s |

No optimisation has been applied, and none is currently justified: the dominant cost in a
real experiment is the experiment's own model evaluation, not framework overhead. These
numbers exist so that a future bottleneck can be identified by measurement rather than
guessed at.

## What is deliberately absent

- **No dashboard or GUI.** A polished command-line workflow over sound infrastructure is
  worth more than a visually impressive interface over weak infrastructure.
- **No machine learning.** Out of scope. AURA may one day *host* an ML experiment as a
  generic experiment type; it does not contain or require one.
- **No parallel execution.** The Monte Carlo engine is deterministic and serial. Parallel
  distribution is compatible with the seed scheme (seeds depend only on labels, not on
  order), but adding it without a measured need would trade auditability for speed nobody
  has asked for.
- **No higher-fidelity aircraft model.** The goal is better research infrastructure, not a
  larger simulation.
