"""Exception hierarchy for AURA.

Principle: **no silent failure.** Every recoverable-but-meaningful condition raises a
typed exception carrying enough context to be recorded in a failure record.
"""

from __future__ import annotations

from typing import Any, Optional


class AuraError(Exception):
    """Base class for every AURA error."""


class SpecificationError(AuraError):
    """The experiment specification is malformed or incomplete.

    Raised during preflight validation, before any computation is performed.
    """

    def __init__(self, message: str, field: Optional[str] = None) -> None:
        super().__init__(message if field is None else f"{field}: {message}")
        self.field = field


class RegistryError(AuraError):
    """The experiment registry is inconsistent, or an illegal operation was attempted."""


class StatusTransitionError(RegistryError):
    """An illegal experiment status transition was attempted."""

    def __init__(self, current: Any, requested: Any) -> None:
        super().__init__(
            f"illegal status transition {current} -> {requested}; "
            "see aura.status.LEGAL_TRANSITIONS"
        )
        self.current = current
        self.requested = requested


class ProvenanceError(AuraError):
    """Provenance could not be established or is internally inconsistent."""


class GateError(AuraError):
    """A validity gate could not be evaluated.

    Distinct from a gate *failing*: a gate that fails returns a ``GateResult`` with a
    FAIL/INVALID outcome. This exception means the gate itself could not run, which is
    an engineering fault and must never be reported as a passing gate.
    """


class ImmutabilityError(AuraError):
    """An attempt was made to overwrite immutable raw data or a finalised artefact."""


class FrozenTestError(AuraError):
    """An operation would have touched the frozen test set."""


class ReproducibilityError(AuraError):
    """A repeat execution did not satisfy the declared reproducibility criterion."""


class StatisticalError(AuraError):
    """A statistical computation was requested outside its stated validity."""
