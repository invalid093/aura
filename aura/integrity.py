"""Integrity assertions distilled from real AURA research failures.

Each helper here exists because a specific defect in the EXP-0002 → EXP-0012 record was
caused by its absence. They are cheap, they are called from experiment code, and they
turn a class of silent corruption into a loud, immediate error.

* :func:`assert_distinct` — a silent patch failure once produced nine duplicate copies
  of the nominal template in EXP-0011. Nothing noticed until a downstream result looked
  strange, because a hypothesis set with duplicates is still a valid list.
* :func:`assert_patch_applied` — the same incident: a string replacement that matched
  nothing left the file unchanged and reported success. Every subsequent patch in the
  project was assertion-checked; this makes that permanent.
* :func:`assert_reported_n` — an EXP-0002 determinism check hard-coded a label claiming
  72 runs while actually checking 90. Label-only, but a reader had no way to tell.
* :func:`assert_divides` — an integration step of 0.004 s does not divide a 100 Hz
  sample interval; sampling drifts silently.
"""

from __future__ import annotations

from typing import Any, Callable, Hashable, Iterable, Sequence

from .errors import AuraError


class IntegrityError(AuraError):
    """An integrity assertion failed. Always a defect, never a research outcome."""


def assert_distinct(items: Iterable[Any], label: str, *, key: Callable[[Any], Hashable] | None = None) -> None:
    """Raise unless every item is distinct.

    Use for hypothesis libraries, template sets, fault definitions and seed labels —
    anywhere a duplicate would silently bias a result rather than crash.

    >>> assert_distinct(["F0", "F1"], "templates")
    >>> assert_distinct(["F0", "F0"], "templates")
    Traceback (most recent call last):
    aura.integrity.IntegrityError: templates contains 1 duplicate(s): ['F0']
    """
    seen: dict[Hashable, int] = {}
    for item in items:
        k = key(item) if key else (item if isinstance(item, Hashable) else repr(item))
        seen[k] = seen.get(k, 0) + 1
    dupes = sorted(repr(k) for k, n in seen.items() if n > 1)
    if dupes:
        raise IntegrityError(f"{label} contains {len(dupes)} duplicate(s): {dupes}")


def assert_patch_applied(before: Any, after: Any, description: str) -> None:
    """Raise if a transformation left its input unchanged.

    A patch, substitution or filter that silently matches nothing is indistinguishable
    from one that succeeded, unless something checks.
    """
    if before == after:
        raise IntegrityError(
            f"{description}: the operation produced no change. "
            "A patch that matches nothing must not be reported as applied."
        )


def assert_reported_n(reported: int, actual: int, label: str) -> None:
    """Raise unless a reported sample count equals the actual one.

    Guards the class of defect where a summary line is written by hand and drifts away
    from the loop that produced it.
    """
    if int(reported) != int(actual):
        raise IntegrityError(
            f"{label}: reported N ({reported}) does not equal actual N ({actual}). "
            "A reported count must be derived from the data, not written by hand."
        )


def assert_divides(step: float, interval: float, label: str, *, tol: float = 1e-9) -> None:
    """Raise unless ``interval`` is an integer multiple of ``step``.

    An integration step that does not divide the sampling interval makes sample times
    drift relative to the intended grid — a defect that produces plausible-looking data.
    """
    if step <= 0 or interval <= 0:
        raise IntegrityError(f"{label}: step and interval must both be positive")
    ratio = interval / step
    if abs(ratio - round(ratio)) > tol:
        raise IntegrityError(
            f"{label}: step {step} does not divide interval {interval} "
            f"(ratio {ratio:.9f}); sampling would drift"
        )


def assert_symmetric_sets(left: Sequence[Any], right: Sequence[Any], label: str) -> None:
    """Raise unless two admissible sets contain the same elements.

    From EXP-0011, where one experimental case could select a hypothesis that the case
    it was being compared against could not. The comparison was therefore between
    differently-shaped hypothesis spaces, and nothing in the tooling noticed.
    """
    ls, rs = set(map(repr, left)), set(map(repr, right))
    if ls != rs:
        only_left = sorted(ls - rs)
        only_right = sorted(rs - ls)
        raise IntegrityError(
            f"{label}: admissible sets differ and are therefore not comparable. "
            f"Only in left: {only_left}; only in right: {only_right}"
        )
