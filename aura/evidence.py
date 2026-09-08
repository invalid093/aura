"""Evidence classification.

AURA's central editorial rule: **a number is not a conclusion.** Every statement in a
generated report carries an evidence class, and the report generator refuses to place a
measured value and an inference in the same structural slot.

The seven classes are those used throughout the AURA research record
(``docs/methodology.md`` §2) and are frozen — adding a class changes the meaning of
every historical document, so it requires an ADR.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable, List


class EvidenceClass(str, Enum):
    """What kind of claim a statement is."""

    FACT = "FACT"
    """Established by definition, algebra, or direct inspection of an artefact.
    Does not depend on this experiment's numbers."""

    CALCULATION = "CALCULATION"
    """A value produced by a documented computation from recorded inputs.
    Reproducible from the provenance record."""

    OBSERVATION = "OBSERVATION"
    """Something seen in the results that is not itself a designed measurement,
    and whose generality is not established."""

    INTERPRETATION = "INTERPRETATION"
    """The researcher's reading of what the evidence means. Not measured."""

    HYPOTHESIS = "HYPOTHESIS"
    """A proposition offered for future test. Carries no evidential weight."""

    ASSUMPTION = "ASSUMPTION"
    """Taken as true without being tested here; the result is conditional on it."""

    LIMITATION = "LIMITATION"
    """A stated boundary on what the evidence can support."""

    @property
    def is_measured(self) -> bool:
        """True for classes the *system* produced, false for classes a *person* asserted.

        This is the distinction the report generator enforces structurally
        (§12 of the portfolio specification).
        """
        return self in (EvidenceClass.FACT, EvidenceClass.CALCULATION, EvidenceClass.OBSERVATION)


#: Classes that may appear in the "what the evidence supports" section of a report.
SUPPORTING_CLASSES = (EvidenceClass.FACT, EvidenceClass.CALCULATION, EvidenceClass.OBSERVATION)


@dataclass(frozen=True)
class Statement:
    """One classified claim.

    Parameters
    ----------
    evidence:
        What kind of claim this is.
    text:
        The claim itself, in prose.
    provenance_ref:
        Optional pointer to the artefact that supports it — a metric name, a figure id,
        a file path. Required for CALCULATION statements by
        :func:`check_statements`, because an unsourced number is not auditable.
    """

    evidence: EvidenceClass
    text: str
    provenance_ref: str | None = None

    def render(self) -> str:
        """Markdown rendering: class badge, then the claim."""
        ref = f" *(source: {self.provenance_ref})*" if self.provenance_ref else ""
        return f"**`{self.evidence.value}`** {self.text}{ref}"


def check_statements(statements: Iterable[Statement]) -> List[str]:
    """Return a list of editorial problems; empty means the set is well formed.

    Enforced rules:

    1. every ``CALCULATION`` cites a provenance reference;
    2. the set is not composed solely of ``INTERPRETATION`` — a report with no measured
       content must not read like a result.

    Returns problems rather than raising, so a report generator can surface all of them
    at once.
    """
    statements = list(statements)
    problems: List[str] = []

    for s in statements:
        if s.evidence is EvidenceClass.CALCULATION and not s.provenance_ref:
            problems.append(f"CALCULATION without provenance_ref: {s.text[:70]!r}")

    if statements and not any(s.evidence.is_measured for s in statements):
        problems.append(
            "statement set contains no measured evidence "
            "(FACT/CALCULATION/OBSERVATION) — this is commentary, not a result"
        )
    return problems


def partition(statements: Iterable[Statement]) -> tuple[List[Statement], List[Statement]]:
    """Split into (measured, inferred).

    Used by the report generator to keep *what the system measured* and *what the
    researcher inferred* in physically separate sections of the document.
    """
    measured, inferred = [], []
    for s in statements:
        (measured if s.evidence.is_measured else inferred).append(s)
    return measured, inferred
