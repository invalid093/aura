# AURA — Validity gates

**Question this document answers:** *what is checked automatically, when, and what does
each outcome mean for the reader?*

A gate converts *"the researcher should remember to check X"* into *"the run cannot be
reported as valid unless X was checked"*. Gates are AURA's defining feature.

List them at any time with `python -m aura gates`.

---

## The cardinal rule

> **A gate that cannot be evaluated raises. It never returns PASS.**

If `model_validity_envelope` is declared but no observation was recorded for an envelope
variable, the gate raises `GateError` rather than passing. The absence of evidence is
never treated as evidence of validity.

A **false PASS** is the one outcome that would make the entire framework worthless — it
converts an unchecked run into a certified one. Everything else in the design is
negotiable; this is not.

## Outcomes

| Outcome | Meaning | Blocks a conclusion? |
|---|---|---|
| `PASS` | The check succeeded | no |
| `FAIL` | The check failed | **yes** |
| `INVALID` | The run's *preconditions* did not hold; results must not be interpreted | **yes** |
| `INCONCLUSIVE` | Validly run, but did not establish what it set out to | no (but the status becomes `INCONCLUSIVE`) |
| `SUPERSEDED` | Replaced by a later result | no |

`FAIL` vs `INVALID`: a FAIL means the check itself failed (a repeat run was not
reproducible). An INVALID means the run was outside the conditions under which its numbers
mean anything (an envelope excursion). Both block interpretation; they are distinguished
because they call for different corrective action.

`INCONCLUSIVE` is deliberately *not* a failure. An under-powered run that missed its
precision target was validly executed — reporting it as a failure would let it be quietly
recast as a negative result.

**Precedence:** `INVALID > FAIL > INCONCLUSIVE > PASS`. One INVALID gate makes the whole
run uninterpretable regardless of how many gates passed.

## Phases

```
specification → PREFLIGHT → execution → RUNTIME → POST → STATISTICAL → evidence package
```

A PREFLIGHT rejection costs nothing: no computation has been performed.

---

## The ten built-in gates

### PREFLIGHT

#### `provenance_complete`
Every always-recordable link in the result → seed chain is present.

- Missing `spec_hash` or `model.identifier` ⇒ **FAIL**.
- No git commit available (not a working copy) ⇒ **INCONCLUSIVE**. Not a FAIL: refusing to
  run outside a git checkout would make the framework unusable rather than rigorous. Not a
  PASS either: the chain genuinely has a hole.
- Dirty working tree ⇒ **PASS with a recorded warning**, propagated into the report's
  Limitations section. Blocking development would be worse than recording the risk.

#### `seed_policy_declared`
A stochastic experiment derives seeds deterministically from a base seed and label fields,
and uses no global RNG. Deterministic experiments pass as *not applicable* — recorded, so a
reader can see the question was asked.

#### `frozen_test_integrity`
The declared frozen test set is byte-identical to its recorded checksums. Any modification
⇒ **INVALID**. A frozen test declared without a checksum file ⇒ **raises**: integrity
cannot be asserted without a record to compare against.

### RUNTIME

#### `model_validity_envelope`
**The FAIL-0001 gate.** Every observation stayed inside the envelope declared in the
specification. Any excursion ⇒ **INVALID**; a missing observation for a declared envelope
variable ⇒ **raises**.

> In EXP-0002, flight condition FC-4 departed controlled flight — angle of attack reached
> 31.5°, 353 m of altitude lost — while producing the **most favourable-looking**
> distinguishability matrix in the study. Nothing about the numbers signalled the problem.
> That is why this gate is unconditional and why its rejection is `INVALID` rather than a
> warning. `DEMO-0002` reproduces the failure mode deliberately.

#### `numerical_validity`
No non-finite values, and integration timing is self-consistent: if `dt` and `sample_dt`
are both reported, `sample_dt` must be an integer multiple of `dt`. A `dt` of 0.004 s does
not divide a 100 Hz sample interval and sampling drifts silently — a real defect caught
during EXP-0010 pilot verification.

### POST

#### `data_completeness`
Planned trials equal recorded trials ⇒ otherwise **INVALID**, because the reported N is
not the run N. Any failed trials ⇒ **INCONCLUSIVE**: the sample is not the intended one.
Catches the EXP-0002 defect where a label claimed 72 runs while 90 were checked.

#### `reproducibility`
A repeat execution satisfied the declared criterion. `mode: bitwise` requires exact
identity (deterministic experiments); `mode: tolerance` compares `max_abs_diff` against a
declared `tolerance`. No repeat performed ⇒ **INCONCLUSIVE**, never PASS.

#### `raw_data_immutable`
No pre-existing raw artefact was modified. Any modification ⇒ **INVALID**.

### STATISTICAL

#### `statistical_precision`
Achieved half-width vs the pre-registered target. A miss ⇒ **INCONCLUSIVE**, not FAIL. The
gate's own evidence carries the caveat:

> *Precision only; says nothing about whether the modelled system is correct.*

#### `convergence`
If the interval half-width was still shrinking by more than `max_final_shrink` (default
25%) over the final checkpoint, the estimate had not settled ⇒ **INCONCLUSIVE**.

---

## Reading a gate table

Every report and handoff contains one:

| Gate | Phase | Outcome | Detail |
|---|---|---|---|
| `model_validity_envelope` | RUNTIME | ❌ **INVALID** | 1 envelope violation(s); results must not be interpreted |

When any gate blocks, the report replaces its conclusion with:

> **No scientific conclusion is emitted for this experiment.**

and its "what the evidence supports" section reads **Nothing.** — present but empty, so
that the emptiness is visible rather than inferred from an omission.

## Adding a gate

```python
from aura.gates import Phase, register, GateResult, Outcome

@register("my_gate", Phase.POST, "What it checks.", required_context=("my_data",))
def _my_gate(ctx):
    ...
```

Declare it in the specification's `gates:` list and return `my_data` from the experiment's
`ExecutionResult`. Naming an unregistered gate is a **validation error**, so a typo cannot
silently disable a check.

Two rules for new gates:

1. If it cannot evaluate, **raise** — never return PASS.
2. Put the reason a reader would need in `detail`, and the numbers they would want in
   `evidence`. Both are published in `gates.json`.
