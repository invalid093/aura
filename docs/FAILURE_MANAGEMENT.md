# AURA — Failure management

**Question this document answers:** *what happens when something goes wrong, and how does
a failure stop being able to happen again?*

---

## Principle

> **A failed experiment must remain part of the research record.**

Nothing is deleted. `INVALID` and `SUPERSEDED` entries stay in the registry; failure
records are append-oriented; a rejected run keeps its evidence package as proof of the
rejection.

The reason is simple: a research record containing only successes is not evidence that the
method works, it is evidence that failures were removed.

## The failure record

```yaml
failure_id: FAIL-0002
experiment_id: DEMO-0002
title: DEMO-0002 rejected - operating point outside the model validity envelope
discovered_utc: 2026-09-08T...
detection_mechanism: automatic validity gate: model_validity_envelope (RUNTIME phase)
description: 1 envelope violation(s); results must not be interpreted
scientific_impact: None. No claim is drawn from this run...
computational_impact: Run completed; outputs retained as evidence of the rejection.
root_cause: Deliberate. DEMO-0002 specifies a deflection of 9.0...
correction: None required. This record IS the intended output...
verification: Verified two ways: metadata.json records status INVALID...
affected_results: [DEMO-0002]
status: ACCEPTED
became_test: tests/test_pipeline.py::TestRunLifecycle::test_envelope_violation_...
```

`detection_mechanism`, `description` and `root_cause` may not be empty. A record whose
status is `RESOLVED` **must** carry a verification — *an unverified correction is a claim,
not a fix*.

## Statuses

| Status | Meaning |
|---|---|
| `OPEN` | Known, not yet corrected |
| `RESOLVED` | Corrected, and the correction verified |
| `ACCEPTED` | Understood, not corrected, consequence documented and tolerated |
| `NON_ISSUE` | Investigated and found not to be a defect — retained so the investigation is not repeated |
| `INVALIDATING` | Invalidates one or more results, which must not be interpreted |

## Automatic recording

When a gate rejects a run, the runner writes a failure record **without human
intervention**, pre-filled with the detection mechanism, the gate's detail, and a scientific
impact statement. `root_cause` and `correction` are stamped `TO BE DETERMINED`: the
framework records *that* something failed and *how it was detected*, and leaves diagnosis
to the researcher rather than inventing one.

```bash
python -m aura failures
```

```
FAIL-0002  ACCEPTED  DEMO-0002  DEMO-0002 rejected: operating point outside the model
                                validity envelope
                                -> regression test: tests/test_pipeline.py::...

{"total": 1, "by_status": {"ACCEPTED": 1}, "became_tests": 1, "open": []}
```

## Identifier allocation

Identifiers are allocated across **every** record format in the directory, not just the
YAML files the registry writes.

This is itself a bug found during framework bring-up: the allocator initially scanned only
`.yaml`, and issued `FAIL-0001` to an automatically-recorded demo failure — while
`FAIL-0001.md`, the hand-written record of the FC-4 departure, already existed. Re-issuing
an identifier would have silently broken every reference to the historical failure.

Regression test: `tests/test_core.py::TestFailureRegistry::test_id_allocation_respects_other_formats`.

---

## Research failures that became engineering tests

This is the point of the registry. Each row is a real defect from the EXP-0002 → EXP-0012
record that is now impossible to repeat silently.

| Research failure | What it was | Now prevented by |
|---|---|---|
| **FAIL-0001** | Flight condition FC-4 departed controlled flight (α = 31.5°, 353 m lost) while producing the **most favourable-looking** matrix in the study | `model_validity_envelope` gate; required `validity_envelope` field; `test_envelope_violation_is_invalid`, `test_envelope_missing_observation_raises`, `test_envelope_violation_invalidates_and_records_failure`; live demo `DEMO-0002` |
| Silent patch failure | A whitespace mismatch made a substitution match nothing; it reported success and left **nine duplicate nominal templates** | `integrity.assert_distinct`, `integrity.assert_patch_applied`; `test_duplicate_templates_detected`, `test_no_op_patch_detected` |
| Mismatched reported N | A determinism label hard-coded "72 runs" while 90 were checked | `integrity.assert_reported_n`; `data_completeness` gate; `test_reported_n_mismatch_detected`, `test_data_completeness_detects_count_mismatch` |
| Non-dividing timestep | `dt = 0.004` does not divide a 100 Hz sample interval; sampling drifts | `integrity.assert_divides`; `numerical_validity` gate; `test_dt_divisibility`, `test_numerical_dt_divisibility` |
| Asymmetric admissible sets | EXP-0011 Case A could select a hypothesis Cases B/C could not — the central comparison was between differently-shaped hypothesis spaces | `integrity.assert_symmetric_sets`; `aura.compare` blocking differences; `test_asymmetric_admissible_sets_detected`, `test_different_controlled_variables_block_comparison` |
| Framework bug: id collision | Failure-id allocator ignored Markdown records | `FailureRegistry.used_ids`; `test_id_allocation_respects_other_formats` |
| Framework bug: false conclusion | A crashed run reported `conclusion_emitted: true` because its preflight gates had passed | Status is now required to be interpretable; `test_execution_exception_becomes_failed_not_crash` |

**`OBSERVATION`** Two of these are bugs in the framework itself, found by its own tests
during this conversion. They are listed alongside the research failures rather than
quietly fixed, because a failure registry that excludes the tool's own failures is exactly
the selective record it exists to prevent.

## Using the integrity helpers

```python
from aura.integrity import assert_distinct, assert_patch_applied, assert_divides

assert_distinct(template_ids, "hypothesis templates")
assert_divides(dt, sample_dt, "integration step")

after = text.replace(old, new)
assert_patch_applied(text, after, "threshold update")
```

They raise `IntegrityError`, which is always a defect and never a research outcome. Use
them in experiment code freely: they are cheap, and each one encodes an error somebody has
already made.
