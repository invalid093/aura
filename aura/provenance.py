"""Provenance capture.

AURA must be able to answer *"where did this number come from?"* by walking

``result -> analysis -> experiment -> dataset -> configuration -> model -> code -> seed``

Everything recorded here is machine-independent by construction: no absolute paths, no
usernames, no hostnames. That is both a reproducibility requirement and a public
repository policy requirement — provenance is published, so it must contain nothing
private.
"""

from __future__ import annotations

import os
import platform
import subprocess
import sys
from dataclasses import dataclass, asdict, field
from typing import Any, Dict, List, Optional

from . import FRAMEWORK_VERSION
from .errors import ProvenanceError
from .hashing import hash_file, hash_object
from .status import utc_now


def _git(*args: str, root: str = ".") -> Optional[str]:
    """Run a git command, returning stripped stdout or ``None`` if unavailable.

    Never raises: a repository copied without ``.git`` must still be able to run
    experiments, it simply records that the code version is unknown.
    """
    try:
        out = subprocess.run(
            ["git", *args],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if out.returncode != 0:
        return None
    return out.stdout.strip() or None


@dataclass(frozen=True)
class CodeVersion:
    """Identity of the code that produced a result."""

    git_commit: Optional[str]
    git_dirty: Optional[bool]
    framework_version: str = FRAMEWORK_VERSION

    @property
    def trustworthy(self) -> bool:
        """A dirty or unknown tree cannot be reproduced from the commit alone.

        Reported rather than enforced: refusing to run on a dirty tree would make
        development impossible. The *gate* decides whether that matters.
        """
        return bool(self.git_commit) and self.git_dirty is False


@dataclass(frozen=True)
class Environment:
    """Machine-independent environment description.

    Deliberately excludes hostname, username, CPU model and absolute paths. Python
    version and platform *family* are recorded because they can change floating-point
    behaviour; anything finer would leak the machine without aiding reproduction.
    """

    python_version: str
    platform_system: str
    platform_machine: str
    numpy_version: str

    @staticmethod
    def capture() -> "Environment":
        import numpy as np

        return Environment(
            python_version=".".join(str(v) for v in sys.version_info[:3]),
            platform_system=platform.system(),
            platform_machine=platform.machine(),
            numpy_version=np.__version__,
        )


@dataclass
class Provenance:
    """The complete provenance record for one experiment run."""

    experiment_id: str
    run_id: str
    started_utc: str
    code: CodeVersion
    environment: Environment
    spec_hash: str
    spec_path: Optional[str]
    config_hashes: Dict[str, str] = field(default_factory=dict)
    dataset_versions: Dict[str, str] = field(default_factory=dict)
    model: Dict[str, Any] = field(default_factory=dict)
    seed_policy: Dict[str, Any] = field(default_factory=dict)
    inputs: Dict[str, str] = field(default_factory=dict)
    outputs: Dict[str, str] = field(default_factory=dict)
    finished_utc: Optional[str] = None
    runtime_seconds: Optional[float] = None
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["code"]["trustworthy"] = self.code.trustworthy
        return d

    @property
    def chain_complete(self) -> bool:
        """Whether the full result→seed chain can be walked.

        A missing link is a *reported* provenance defect, not a silent one; the
        provenance gate turns this into a gate outcome.
        """
        return bool(
            self.experiment_id
            and self.spec_hash
            and self.code.git_commit
            and self.model.get("identifier")
        )

    def missing_links(self) -> List[str]:
        """Links that are always recordable but are absent — genuine provenance defects.

        ``code.git_commit`` is deliberately excluded: a repository exported without
        ``.git`` cannot supply one, and refusing to run there would make the framework
        unusable rather than rigorous. It is reported separately by
        :meth:`code_version_certifiable` and downgrades the gate to INCONCLUSIVE, so it
        is never silently ignored either.

        ``config_hashes`` is also excluded: a specification constructed in memory has no
        file to hash, and ``spec_hash`` already covers its scientific content.
        """
        missing = []
        if not self.spec_hash:
            missing.append("spec_hash")
        if not self.model.get("identifier"):
            missing.append("model.identifier")
        return missing

    @property
    def code_version_certifiable(self) -> bool:
        """Whether the code that produced this run can be identified from the record."""
        return bool(self.code.git_commit)


def capture(
    spec: Any,
    *,
    root: str = ".",
    run_id: Optional[str] = None,
    config_paths: Dict[str, str] | None = None,
) -> Provenance:
    """Build a :class:`Provenance` record for a run of ``spec``.

    ``run_id`` defaults to a deterministic function of the experiment id, the
    specification hash and the start timestamp, so two runs of the same specification
    are distinguishable while remaining traceable to it.
    """
    started = utc_now()
    commit = _git("rev-parse", "HEAD", root=root)
    dirty: Optional[bool] = None
    if commit is not None:
        porcelain = _git("status", "--porcelain", root=root)
        dirty = bool(porcelain)

    code = CodeVersion(git_commit=commit, git_dirty=dirty)
    env = Environment.capture()

    config_hashes: Dict[str, str] = {}
    for name, rel in (config_paths or {}).items():
        target = os.path.join(root, rel)
        if not os.path.exists(target):
            raise ProvenanceError(f"configuration referenced but not found: {rel}")
        # Text-normalised: a config must hash identically on Windows and Linux.
        config_hashes[name] = hash_file(target, normalise_text=True)

    if spec.source_path:
        config_hashes.setdefault("specification", hash_file(os.path.join(root, spec.source_path),
                                                           normalise_text=True))

    rid = run_id or hash_object(
        {"id": spec.experiment_id, "spec": spec.content_hash, "t": started}
    )[:16]

    return Provenance(
        experiment_id=spec.experiment_id,
        run_id=rid,
        started_utc=started,
        code=code,
        environment=env,
        spec_hash=spec.content_hash,
        spec_path=spec.source_path,
        config_hashes=config_hashes,
        dataset_versions={d.identifier: d.version for d in spec.datasets},
        model={
            "identifier": spec.model.identifier,
            "version": spec.model.version,
            "validity_envelope": dict(spec.model.validity_envelope),
        },
        seed_policy=(
            {
                "scheme": "sha256(repr(base_seed) || 0x1f || repr(label)...) mod 2**63",
                "base_seed": spec.randomisation.base_seed,
                "label_fields": list(spec.randomisation.label_fields),
                "repetitions": spec.randomisation.repetitions,
                "global_rng_used": False,
            }
            if spec.randomisation.enabled
            else {"enabled": False}
        ),
    )


def trace(provenance: Provenance, metric: str) -> List[str]:
    """Human-readable provenance chain for a reported metric.

    Answers "where did this number come from?" as an ordered list of links, each of
    which names a recorded artefact rather than a description of one.
    """
    chain = [
        f"result: {metric}",
        f"experiment: {provenance.experiment_id} (run {provenance.run_id})",
        f"specification: {provenance.spec_path or '<unsaved>'} sha256={provenance.spec_hash[:16]}",
    ]
    for name, digest in sorted(provenance.config_hashes.items()):
        chain.append(f"configuration[{name}]: sha256={digest[:16]}")
    for ident, version in sorted(provenance.dataset_versions.items()):
        chain.append(f"dataset: {ident} @ {version}")
    chain.append(
        f"model: {provenance.model.get('identifier')} @ {provenance.model.get('version')}"
    )
    chain.append(
        f"code: {provenance.code.git_commit or 'UNKNOWN'}"
        f"{' (dirty)' if provenance.code.git_dirty else ''}"
        f" framework={provenance.code.framework_version}"
    )
    seed = provenance.seed_policy
    chain.append(
        f"seed: base={seed.get('base_seed')} labels={seed.get('label_fields')}"
        if seed.get("base_seed") is not None
        else "seed: deterministic experiment (no randomisation)"
    )
    return chain
