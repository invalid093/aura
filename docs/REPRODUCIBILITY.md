# AURA — Reproducibility

**Question this document answers:** *what exactly does AURA promise when it says a result
is reproducible, and how do I reproduce one?*

---

## Reproducing any recorded result

```bash
python -m aura registry                 # what exists, and its status
python -m aura validate DEMO-0001       # re-check the specification
python -m aura run DEMO-0001            # re-execute
python -m aura verify DEMO-0001         # confirm the package is unmodified
python -m aura provenance DEMO-0001     # where the numbers came from
```

Requirements: Python 3.11+, numpy, PyYAML. Nothing else.

## What "reproducible" means — precisely

AURA distinguishes two regimes and states which applies in every report.

### Deterministic experiments — bitwise identity

An experiment with `randomisation.enabled: false`, or one whose stochastic components are
fully seeded, is expected to reproduce **bit-identically** on the same platform. The
`reproducibility` gate with `mode: bitwise` asserts exact array equality; anything else is
a `FAIL`.

`DEMO-0001` exercises this: it runs its Monte Carlo campaign twice and requires
`np.array_equal` on the raw samples.

### Stochastic experiments — recorded seeds and documented tolerance

Where bitwise identity is not achievable, AURA requires:

1. **deterministic seed generation** — `seed = SHA-256(base_seed ‖ labels) mod 2⁶³`;
2. **recorded seeds** — either the full table, or `base_seed` plus `label_fields`, which
   regenerate every seed;
3. **reproducible aggregation** — estimators are declared in the specification, not chosen
   after seeing the data;
4. **a documented tolerance** — `mode: tolerance` with an explicit `max_abs_diff` bound,
   recorded in the gate evidence.

### What is *not* claimed

**`LIMITATION`** Cross-platform bitwise identity of floating-point results is **not**
claimed. Different numpy builds, BLAS backends and CPU architectures can produce different
last bits. Provenance therefore records python version, platform system, platform machine
and numpy version, so that a difference can be attributed rather than puzzled over.

**`LIMITATION`** A **dirty working tree** means the recorded commit alone does not
reproduce the run. The `provenance_complete` gate records this as a warning and the report
carries it into Limitations. It is not blocked, because blocking every run during
development would make the framework unusable.

**`LIMITATION`** If git is unavailable, the code version cannot be recorded at all. The
gate returns `INCONCLUSIVE` — never PASS.

## Seed derivation

```
seed = int(SHA-256(repr(base_seed) ‖ 0x1f ‖ repr(label₁) ‖ … ‖ repr(labelₙ))) mod 2⁶³
```

Properties this buys:

- **order independence** — a cell's seed depends only on its own labels, so adding
  conditions to a sweep does not change any existing cell's random stream;
- **resumability** — an interrupted run recomputes identical seeds;
- **isolation** — any single cell can be reproduced without replaying the sweep;
- **type distinctness** — labels are stringified with `repr`, so `1`, `1.0` and `"1"` are
  three different cells rather than silently one.

The `0x1f` separator ensures `("a","bc")` and `("ab","c")` cannot collide.

**Global RNG state is never used.** `np.random.seed` and module-level `np.random.*` calls
are absent from the framework; every stochastic component receives an explicit generator.
The `seed_policy_declared` gate records this.

## The provenance chain

`python -m aura provenance <ID>` walks:

```
result → experiment → specification (sha256) → configuration (sha256)
       → dataset (id@version) → model (id@version) → code (commit) → seed (base + labels)
```

Everything recorded is machine-independent: no absolute paths, no usernames, no hostnames.
That is a reproducibility requirement *and* a public-repository requirement, since
provenance is published.

## Hashing

Configuration and specification files are hashed **text-normalised** (line endings
converted to `\n`), so a repository checked out on Windows and on Linux produces identical
hashes. Binary artefacts are hashed byte-exactly, where byte identity is the property being
asserted.

Canonical JSON hashing sorts keys, emits no insignificant whitespace, and **rejects
non-finite values** — a `NaN` in a configuration is nearly always a bug, and silently
hashing it would hide that.

## Verifying a finalised package

```bash
python -m aura verify DEMO-0001
# DEMO-0001: evidence package verified — all artefacts unchanged
```

`checksums.txt` covers every file in the evidence package. If any has changed since
finalisation, `verify` names it and exits 1.

## Reproducibility of the framework itself

```bash
python -m unittest discover -s tests -t .
# Ran 82 tests ... OK
```

The suite uses only the standard library. It includes regression tests derived from real
AURA research failures (see [`FAILURE_MANAGEMENT.md`](FAILURE_MANAGEMENT.md)) and two
tests for bugs found *in the framework* during its own bring-up.

## Known reproducibility limitations

| Limitation | Status |
|---|---|
| Cross-platform floating-point bitwise identity | Not claimed; platform recorded |
| Dirty working tree at run time | Recorded as a warning; surfaced in Limitations |
| Git unavailable | Gate returns INCONCLUSIVE; run proceeds, chain has a documented hole |
| Wall-clock runtime | Recorded but not reproducible; irrelevant to results |
| The historical EXP-0002…EXP-0012 runs | Predate this framework. Their provenance is recorded in their own results JSON (git commit, config sha256, environment, seeds) but they do not carry AURA evidence packages |
