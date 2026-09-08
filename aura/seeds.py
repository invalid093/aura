"""Deterministic seed derivation.

Requirement (§6): a rerun with the same deterministic inputs produces equivalent
results. That is impossible if any component draws from a global RNG, so AURA never
uses ``numpy.random`` module-level state. Every stochastic component receives an
explicit seed derived here.

Derivation
----------
``seed = int(SHA-256(base_seed || label_1 || ... || label_n)) mod 2**63``

Properties this buys:

* **order independence** — a cell's seed depends only on its own labels, so adding
  conditions to a sweep does not change any existing cell's stream;
* **resumability** — an interrupted run recomputes identical seeds;
* **auditability** — the labels are recorded, so any single cell can be reproduced in
  isolation without replaying the sweep.

This generalises the ad-hoc scheme used in EXP-0012, where per-cell seeds were derived
by hashing ``(base, condition, window, fault, magnitude, eta)``.
"""

from __future__ import annotations

import hashlib
from typing import Any, Iterable, Sequence

import numpy as np

#: numpy accepts seeds in [0, 2**63). We reduce the digest into that range.
_MODULUS = 1 << 63

#: Separator that cannot appear in a stringified label component, so that
#: ("a", "bc") and ("ab", "c") cannot collide.
_SEP = b"\x1f"


def derive_seed(base_seed: int, *labels: Any) -> int:
    """Derive a reproducible seed from ``base_seed`` and a tuple of labels.

    Labels are stringified with ``repr`` so that ``1`` and ``1.0`` and ``"1"`` are
    distinct — a silent conflation would give two different experimental cells the same
    random stream.

    >>> derive_seed(20261210, "FC-1", 2.0) == derive_seed(20261210, "FC-1", 2.0)
    True
    >>> derive_seed(20261210, "FC-1", 2.0) == derive_seed(20261210, "FC-1", 2)
    False
    """
    if not isinstance(base_seed, int) or isinstance(base_seed, bool):
        raise TypeError(f"base_seed must be int, got {type(base_seed).__name__}")
    if base_seed < 0:
        raise ValueError("base_seed must be non-negative")

    h = hashlib.sha256()
    h.update(repr(base_seed).encode("utf-8"))
    for label in labels:
        h.update(_SEP)
        h.update(repr(label).encode("utf-8"))
    return int.from_bytes(h.digest(), "big") % _MODULUS


def generator(base_seed: int, *labels: Any) -> np.random.Generator:
    """A ``numpy`` Generator seeded by :func:`derive_seed`.

    Always use this rather than ``np.random.default_rng()`` with an implicit seed, and
    never ``np.random.seed`` — global RNG state is the classic source of results that
    cannot be reproduced.
    """
    return np.random.default_rng(derive_seed(base_seed, *labels))


def seed_table(base_seed: int, cells: Iterable[Sequence[Any]]) -> dict[str, int]:
    """Map a stringified cell key -> derived seed, for the provenance record.

    Recording the whole table is only practical for modest sweeps; for large ones record
    ``base_seed`` and the seed *policy* instead (see :func:`describe_policy`), which is
    sufficient to regenerate every seed.
    """
    out: dict[str, int] = {}
    for cell in cells:
        out["|".join(repr(c) for c in cell)] = derive_seed(base_seed, *cell)
    return out


def describe_policy(base_seed: int, label_fields: Sequence[str]) -> dict[str, Any]:
    """A machine-readable description of the seed policy, for provenance.

    Sufficient, with the configuration, to regenerate every seed in the experiment
    without storing them individually.
    """
    return {
        "scheme": "sha256(repr(base_seed) || 0x1f || repr(label)...) mod 2**63",
        "base_seed": base_seed,
        "label_fields": list(label_fields),
        "global_rng_used": False,
    }
