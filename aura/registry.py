"""The experiment registry.

The registry is the index of every experiment the project has ever specified, in any
status. Its rules:

* an experiment is registered **before** it runs (status ``PLANNED``);
* status changes go through :mod:`aura.status` and are recorded with a reason;
* nothing is ever removed — ``SUPERSEDED`` and ``INVALID`` entries stay.

Layout::

    experiments/<ID>/spec.yaml            the pre-registered specification
    experiments/<ID>/status_history.yaml  every status transition, with reasons

Legacy entries from the original research phase (``experiments/EXP-####.yaml``) use an
earlier hand-written schema. They are indexed read-only as historical records rather
than rewritten, because rewriting them would falsify the research record.
"""

from __future__ import annotations

import io
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import yaml

from .errors import RegistryError
from .spec import ExperimentSpec
from .status import Status, Transition, transition


@dataclass(frozen=True)
class RegistryEntry:
    """One indexed experiment."""

    experiment_id: str
    title: str
    status: str
    kind: str
    spec_path: Optional[str]
    legacy: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "experiment_id": self.experiment_id,
            "title": self.title,
            "status": self.status,
            "kind": self.kind,
            "spec_path": self.spec_path,
            "legacy": self.legacy,
        }


class Registry:
    """Index of experiment specifications under ``<root>/experiments``."""

    def __init__(self, root: str | os.PathLike[str] = ".") -> None:
        self.root = os.fspath(root)
        self.experiments_dir = os.path.join(self.root, "experiments")

    # ------------------------------------------------------------------------ paths
    def spec_path(self, experiment_id: str) -> str:
        return os.path.join(self.experiments_dir, experiment_id, "spec.yaml")

    def history_path(self, experiment_id: str) -> str:
        return os.path.join(self.experiments_dir, experiment_id, "status_history.yaml")

    # ------------------------------------------------------------------------ reading
    def entries(self, *, include_legacy: bool = True) -> List[RegistryEntry]:
        """Every registered experiment, sorted by id."""
        out: List[RegistryEntry] = []
        if not os.path.isdir(self.experiments_dir):
            return out

        for name in sorted(os.listdir(self.experiments_dir)):
            path = os.path.join(self.experiments_dir, name)
            if os.path.isdir(path):
                sp = self.spec_path(name)
                if os.path.exists(sp):
                    try:
                        spec = ExperimentSpec.load(sp)
                    except Exception as exc:  # noqa: BLE001 - surfaced, never hidden
                        raise RegistryError(f"{name}: unreadable specification: {exc}") from exc
                    out.append(
                        RegistryEntry(
                            spec.experiment_id, spec.title, spec.status, spec.kind,
                            os.path.relpath(sp, self.root).replace(os.sep, "/"),
                        )
                    )
            elif include_legacy and name.endswith(".yaml") and name.startswith("EXP-"):
                with io.open(path, "r", encoding="utf-8") as fh:
                    data = yaml.safe_load(fh) or {}
                out.append(
                    RegistryEntry(
                        str(data.get("experiment_id", name[:-5])),
                        str(data.get("title", "")),
                        str(data.get("status", "UNKNOWN")),
                        str(data.get("type", "unknown")),
                        os.path.relpath(path, self.root).replace(os.sep, "/"),
                        legacy=True,
                    )
                )
        return sorted(out, key=lambda e: e.experiment_id)

    def ids(self) -> List[str]:
        """Every registered experiment id — used to detect id collisions."""
        return [e.experiment_id for e in self.entries()]

    def load(self, experiment_id: str) -> ExperimentSpec:
        """Load a specification, raising if the experiment is unknown or legacy-only."""
        path = self.spec_path(experiment_id)
        if not os.path.exists(path):
            raise RegistryError(
                f"{experiment_id} has no spec.yaml "
                "(legacy research-phase entries are read-only historical records)"
            )
        return ExperimentSpec.load(path)

    def history(self, experiment_id: str) -> List[Transition]:
        """Recorded status transitions, oldest first."""
        path = self.history_path(experiment_id)
        if not os.path.exists(path):
            return []
        with io.open(path, "r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or []
        return [Transition(**t) for t in data]

    # ------------------------------------------------------------------------ writing
    def register(self, spec: ExperimentSpec, *, overwrite: bool = False) -> str:
        """Write a new specification into the registry.

        Refuses to clobber an existing specification: overwriting a pre-registration is
        precisely the manoeuvre pre-registration exists to prevent.
        """
        if spec.experiment_id in self.ids() and not overwrite:
            raise RegistryError(
                f"{spec.experiment_id} is already registered; "
                "use a new id, or overwrite=True only to correct a specification that has not run"
            )
        path = self.spec_path(spec.experiment_id)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        spec.dump(path)
        return os.path.relpath(path, self.root).replace(os.sep, "/")

    def set_status(
        self, experiment_id: str, new_status: Status, reason: str, actor: str = "aura"
    ) -> List[Transition]:
        """Transition an experiment's status, recording the reason.

        Raises :class:`~aura.errors.StatusTransitionError` for an illegal transition, so
        a status cannot be changed silently or arbitrarily.
        """
        spec = self.load(experiment_id)
        current = Status(spec.status)
        history = self.history(experiment_id)
        _new, history = transition(current, new_status, reason, history, actor)

        path = self.spec_path(experiment_id)
        with io.open(path, "r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
        data["status"] = new_status.value
        with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
            yaml.safe_dump(data, fh, sort_keys=True, allow_unicode=True)

        with io.open(self.history_path(experiment_id), "w", encoding="utf-8", newline="\n") as fh:
            yaml.safe_dump([t.to_dict() for t in history], fh, sort_keys=False, allow_unicode=True)
        return history

    # ------------------------------------------------------------------------ summary
    def summary(self) -> Dict[str, Any]:
        """Counts by status, separating framework demos from research experiments."""
        entries = self.entries()
        by_status: Dict[str, int] = {}
        for e in entries:
            by_status[e.status] = by_status.get(e.status, 0) + 1
        return {
            "total": len(entries),
            "by_status": by_status,
            "research": [e.experiment_id for e in entries if e.experiment_id.startswith("EXP-")],
            "demonstrations": [e.experiment_id for e in entries if e.experiment_id.startswith("DEMO-")],
            "legacy_records": [e.experiment_id for e in entries if e.legacy],
        }
