"""Experiment status and its legal transitions.

Status is not a free-text field. An experiment that silently moves from ``INVALID``
back to ``COMPLETED`` has erased a research failure, so transitions are enumerated and
every one is recorded with a timestamp and a reason.

The transition graph deliberately has **no edge back into ``PLANNED``** and no edge out
of ``ARCHIVED``: a run that happened cannot be un-happened, and an archived record is
closed. Re-running an experiment creates a new run, not a rewind.
"""

from __future__ import annotations

import datetime as _dt
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Any, Dict, List, Mapping

from .errors import StatusTransitionError


class Status(str, Enum):
    """Lifecycle state of an experiment."""

    PLANNED = "PLANNED"
    """Specified and pre-registered; not yet executed."""

    RUNNING = "RUNNING"
    """Execution in progress."""

    COMPLETED = "COMPLETED"
    """Ran to completion and passed its gates. Says nothing about the hypothesis."""

    FAILED = "FAILED"
    """Execution did not complete — a crash, a timeout, an unrecoverable error."""

    INVALID = "INVALID"
    """Ran, but a validity gate rejected it. **The results must not be interpreted.**
    Distinct from FAILED: the computation finished, but its preconditions did not hold.
    This is the status FC-4 would have received (FAIL-0001)."""

    INCONCLUSIVE = "INCONCLUSIVE"
    """Ran and was valid, but did not achieve the precision needed to decide its
    pre-registered question. Not a failure; an honest non-answer."""

    SUPERSEDED = "SUPERSEDED"
    """Correct as run, but replaced by a later experiment. Retained, never deleted."""

    ARCHIVED = "ARCHIVED"
    """Closed. No further transitions."""


#: Legal transitions. Anything absent here raises StatusTransitionError.
LEGAL_TRANSITIONS: Mapping[Status, frozenset[Status]] = {
    Status.PLANNED: frozenset({Status.RUNNING, Status.ARCHIVED}),
    Status.RUNNING: frozenset(
        {Status.COMPLETED, Status.FAILED, Status.INVALID, Status.INCONCLUSIVE}
    ),
    # A completed run may later be invalidated by a discovered defect — that is how
    # FAIL-0001 propagated — so COMPLETED -> INVALID is legal and must stay legal.
    Status.COMPLETED: frozenset({Status.SUPERSEDED, Status.ARCHIVED, Status.INVALID}),
    Status.INCONCLUSIVE: frozenset({Status.SUPERSEDED, Status.ARCHIVED, Status.INVALID}),
    Status.FAILED: frozenset({Status.ARCHIVED, Status.RUNNING}),
    Status.INVALID: frozenset({Status.ARCHIVED, Status.RUNNING}),
    Status.SUPERSEDED: frozenset({Status.ARCHIVED}),
    Status.ARCHIVED: frozenset(),
}

#: Statuses from which a scientific conclusion may be drawn at all.
INTERPRETABLE = frozenset({Status.COMPLETED, Status.INCONCLUSIVE, Status.SUPERSEDED})


@dataclass(frozen=True)
class Transition:
    """One recorded status change."""

    from_status: str
    to_status: str
    timestamp_utc: str
    reason: str
    actor: str = "aura"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def utc_now() -> str:
    """ISO-8601 UTC timestamp. Centralised so every artefact stamps time identically."""
    return _dt.datetime.now(_dt.timezone.utc).isoformat()


def check_transition(current: Status, requested: Status) -> None:
    """Raise :class:`StatusTransitionError` unless the transition is legal."""
    if requested not in LEGAL_TRANSITIONS[current]:
        raise StatusTransitionError(current.value, requested.value)


def transition(
    current: Status,
    requested: Status,
    reason: str,
    history: List[Transition] | None = None,
    actor: str = "aura",
) -> tuple[Status, List[Transition]]:
    """Validate and record a transition.

    A ``reason`` is mandatory. An unexplained status change is exactly the "silent
    methodological change" the framework exists to prevent.
    """
    if not reason or not reason.strip():
        raise ValueError("a status transition requires a non-empty reason")
    check_transition(current, requested)
    record = Transition(current.value, requested.value, utc_now(), reason.strip(), actor)
    return requested, list(history or []) + [record]


def is_interpretable(status: Status) -> bool:
    """Whether results under this status may be used to support a conclusion.

    The report generator consults this: an INVALID experiment produces a report that
    documents the invalidity and **emits no scientific conclusion**.
    """
    return status in INTERPRETABLE
