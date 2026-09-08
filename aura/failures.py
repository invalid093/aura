"""The failure registry.

Formalises the ``FAIL-####`` records the AURA research record already used. A failed or
invalidated experiment stays in the record permanently: deleting it would remove the
evidence that the framework works.

The fields below are those that turned out to matter in the real cases — FAIL-0001 (a
flight condition that departed controlled flight while producing the most favourable
numbers in the study), a silent patch failure that produced duplicate templates, and an
integration step that did not divide the sample interval.
"""

from __future__ import annotations

import io
import os
import re
from dataclasses import dataclass, asdict, field
from enum import Enum
from typing import Any, Dict, List, Optional

import yaml

from .errors import RegistryError
from .status import utc_now

FAIL_ID = re.compile(r"^FAIL-\d{4}$")


class FailureStatus(str, Enum):
    """Disposition of a recorded failure."""

    OPEN = "OPEN"
    """Known, not yet corrected."""

    RESOLVED = "RESOLVED"
    """Corrected and the correction verified."""

    ACCEPTED = "ACCEPTED"
    """Understood, not corrected, and the consequence is documented and tolerated."""

    NON_ISSUE = "NON_ISSUE"
    """Investigated and found not to be a defect. Retained so the investigation is not
    repeated."""

    INVALIDATING = "INVALIDATING"
    """Invalidates one or more results. Those results must not be interpreted."""


@dataclass
class FailureRecord:
    """One failure."""

    failure_id: str
    experiment_id: str
    title: str
    discovered_utc: str
    detection_mechanism: str
    description: str
    scientific_impact: str
    computational_impact: str
    root_cause: str
    correction: str
    verification: str
    affected_results: List[str] = field(default_factory=list)
    status: str = FailureStatus.OPEN.value
    became_test: Optional[str] = None
    """Name of the regression test that now prevents recurrence, if any.

    This field is the point of the registry: a research failure that becomes a
    permanent engineering test cannot happen twice."""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def validate(self) -> None:
        """Raise :class:`RegistryError` if the record is not usable as evidence."""
        if not FAIL_ID.match(self.failure_id):
            raise RegistryError(f"{self.failure_id!r} does not match FAIL-####")
        try:
            FailureStatus(self.status)
        except ValueError as exc:
            raise RegistryError(f"invalid failure status {self.status!r}") from exc
        for name in ("detection_mechanism", "description", "root_cause"):
            if not getattr(self, name).strip():
                raise RegistryError(f"FailureRecord.{name} may not be empty")
        if self.status == FailureStatus.RESOLVED.value and not self.verification.strip():
            raise RegistryError(
                f"{self.failure_id} is RESOLVED but records no verification; "
                "an unverified correction is a claim, not a fix"
            )


class FailureRegistry:
    """A directory of ``FAIL-####.yaml`` records."""

    def __init__(self, directory: str | os.PathLike[str]) -> None:
        self.directory = os.fspath(directory)

    # ------------------------------------------------------------------------ access
    def load_all(self) -> List[FailureRecord]:
        """Every record, sorted by id."""
        records: List[FailureRecord] = []
        if not os.path.isdir(self.directory):
            return records
        for name in sorted(os.listdir(self.directory)):
            if not name.endswith((".yaml", ".yml")):
                continue
            with io.open(os.path.join(self.directory, name), "r", encoding="utf-8") as fh:
                data = yaml.safe_load(fh) or {}
            records.append(FailureRecord(**data))
        return records

    def used_ids(self) -> set[str]:
        """Every ``FAIL-####`` identifier already claimed in this directory.

        Scans **all** file types, not just the YAML records this class writes. The
        historical research-phase failures are hand-written Markdown (``FAIL-0001.md``),
        and an id-allocation scheme that ignored them would re-issue an identifier that
        already refers to a different failure -- silently overwriting the research
        record's reference to it. Caught by DEMO-0002 during framework bring-up.
        """
        used: set[str] = set()
        if not os.path.isdir(self.directory):
            return used
        for name in os.listdir(self.directory):
            stem = os.path.splitext(name)[0]
            if FAIL_ID.match(stem):
                used.add(stem)
        return used

    def next_id(self) -> str:
        """The next free ``FAIL-####`` identifier, across every record format."""
        used = self.used_ids() | {r.failure_id for r in self.load_all()}
        i = 1
        while f"FAIL-{i:04d}" in used:
            i += 1
        return f"FAIL-{i:04d}"

    # ------------------------------------------------------------------------ writing
    def record(self, failure: FailureRecord, *, overwrite: bool = False) -> str:
        """Persist a failure record; returns the path written.

        Refuses to overwrite an existing record unless asked explicitly — the registry
        is append-oriented, because editing history is how failures disappear.
        """
        failure.validate()
        os.makedirs(self.directory, exist_ok=True)
        path = os.path.join(self.directory, f"{failure.failure_id}.yaml")
        # Check the identifier, not just this exact filename: a Markdown record with the
        # same id is still that id being taken.
        if failure.failure_id in self.used_ids() and not overwrite:
            raise RegistryError(
                f"{failure.failure_id} already exists (in any record format); refusing to overwrite"
            )
        with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
            yaml.safe_dump(failure.to_dict(), fh, sort_keys=True, allow_unicode=True)
        return path.replace(os.sep, "/")

    def from_gate_failure(
        self,
        experiment_id: str,
        gate_result: Any,
        *,
        detection_mechanism: str = "automatic validity gate",
    ) -> FailureRecord:
        """Build a failure record from a gate that rejected a run.

        Used by the runner so that an INVALID experiment automatically leaves a
        permanent record rather than depending on the researcher to write one.
        """
        return FailureRecord(
            failure_id=self.next_id(),
            experiment_id=experiment_id,
            title=f"{gate_result.name} returned {gate_result.outcome}",
            discovered_utc=utc_now(),
            detection_mechanism=f"{detection_mechanism}: {gate_result.name} "
                                f"({gate_result.phase} phase)",
            description=gate_result.detail,
            scientific_impact=(
                "Results from this run must not be interpreted."
                if gate_result.outcome in ("INVALID", "FAIL")
                else "Run completed but did not meet a declared criterion."
            ),
            computational_impact="Run completed; outputs retained as evidence of the rejection.",
            root_cause="TO BE DETERMINED — recorded automatically at detection time.",
            correction="TO BE DETERMINED",
            verification="",
            affected_results=[experiment_id],
            status=(
                FailureStatus.INVALIDATING.value
                if gate_result.outcome == "INVALID"
                else FailureStatus.OPEN.value
            ),
        )

    # ------------------------------------------------------------------------ summary
    def summary(self) -> Dict[str, Any]:
        """Counts by status, plus how many failures became regression tests."""
        records = self.load_all()
        counts: Dict[str, int] = {}
        for r in records:
            counts[r.status] = counts.get(r.status, 0) + 1
        return {
            "total": len(records),
            "by_status": counts,
            "became_tests": sum(1 for r in records if r.became_test),
            "open": [r.failure_id for r in records if r.status == FailureStatus.OPEN.value],
        }
