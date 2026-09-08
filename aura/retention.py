"""Storage-aware retention.

Every generated artefact is assigned a retention class. Nothing is ever deleted
automatically unless its class explicitly permits it, and the classes are ordered so
that provenance survives any cleanup.

Data hierarchy (``docs/PROVENANCE.md``)::

    RAW        immutable simulator output; never modified, never regenerated in place
    PROCESSED  cleaned/aligned data derived from RAW by a recorded transformation
    DERIVED    compact analysis surfaces (metrics, matrices) used to make figures
    RESULTS    the evidence package: metadata, provenance, statistics, gates, report
"""

from __future__ import annotations

import os
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Any, Dict, Iterable, List


class RetentionClass(str, Enum):
    """How long an artefact must be kept."""

    RETAIN_PERMANENT = "RETAIN-PERMANENT"
    """Essential evidence or provenance. Never deleted. Small by construction."""

    RETAIN_COMPACT = "RETAIN-COMPACT"
    """Regenerable, but a compact summary must remain so results stay readable
    without a re-run."""

    REGENERABLE = "REGENERABLE"
    """Large intermediates reproducible from the recorded configuration and seeds.
    Safe to delete once the evidence package is finalised and verified."""

    TEMPORARY = "TEMPORARY"
    """Scratch. Safe to delete after successful finalisation."""

    @property
    def deletable(self) -> bool:
        return self in (RetentionClass.REGENERABLE, RetentionClass.TEMPORARY)


class DataTier(str, Enum):
    """Where an artefact sits in the data hierarchy."""

    RAW = "RAW"
    PROCESSED = "PROCESSED"
    DERIVED = "DERIVED"
    RESULTS = "RESULTS"


#: Default retention by tier. RAW is permanent because it cannot be regenerated
#: bit-identically in general (and regenerating it in place would violate immutability).
DEFAULT_RETENTION: Dict[DataTier, RetentionClass] = {
    DataTier.RAW: RetentionClass.REGENERABLE,
    DataTier.PROCESSED: RetentionClass.REGENERABLE,
    DataTier.DERIVED: RetentionClass.RETAIN_COMPACT,
    DataTier.RESULTS: RetentionClass.RETAIN_PERMANENT,
}


@dataclass(frozen=True)
class Artefact:
    """One tracked output."""

    path: str
    tier: str
    retention: str
    bytes: int
    sha256: str
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @property
    def deletable(self) -> bool:
        return RetentionClass(self.retention).deletable


def classify(path: str, tier: DataTier, *, retention: RetentionClass | None = None) -> RetentionClass:
    """Retention class for ``path``; explicit ``retention`` overrides the tier default."""
    return retention or DEFAULT_RETENTION[tier]


def plan_cleanup(artefacts: Iterable[Artefact], *, finalised: bool) -> Dict[str, Any]:
    """What could be deleted, and what must not be.

    Returns a *plan*, never performing deletion. ``finalised`` guards the whole
    operation: nothing is deletable until the evidence package exists and verifies,
    because a REGENERABLE artefact is only safe to lose once the record of how to
    regenerate it is permanent.
    """
    artefacts = list(artefacts)
    if not finalised:
        return {
            "eligible": [],
            "retained": [a.path for a in artefacts],
            "reclaimable_bytes": 0,
            "reason": "experiment not finalised; nothing is eligible for deletion",
        }
    eligible = [a for a in artefacts if a.deletable]
    return {
        "eligible": [a.path for a in eligible],
        "retained": [a.path for a in artefacts if not a.deletable],
        "reclaimable_bytes": sum(a.bytes for a in eligible),
        "reason": "finalised; REGENERABLE and TEMPORARY artefacts may be removed",
    }


def scan(
    directory: str | os.PathLike[str],
    tier: DataTier,
    *,
    root: str = ".",
    retention: RetentionClass | None = None,
) -> List[Artefact]:
    """Inventory a directory as artefacts of ``tier``.

    Paths are recorded relative to ``root`` so the manifest carries no machine-specific
    path.
    """
    from .hashing import hash_file

    out: List[Artefact] = []
    directory = os.fspath(directory)
    if not os.path.isdir(directory):
        return out
    for dirpath, _dirnames, filenames in os.walk(directory):
        for name in sorted(filenames):
            full = os.path.join(dirpath, name)
            rel = os.path.relpath(full, root).replace(os.sep, "/")
            out.append(
                Artefact(
                    path=rel,
                    tier=tier.value,
                    retention=classify(rel, tier, retention=retention).value,
                    bytes=os.path.getsize(full),
                    sha256=hash_file(full),
                )
            )
    return sorted(out, key=lambda a: a.path)
