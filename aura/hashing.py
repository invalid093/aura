"""Canonical hashing for configurations, files and result payloads.

Two artefacts that are scientifically identical must hash identically, and two that
differ in any way that could change a result must not. That requires a *canonical*
serialisation: key order, float formatting and line endings are all normalised.

Rationale for the float rule: ``repr(0.1 + 0.2)`` differs across platforms in principle,
and YAML round-trips can turn ``1.0`` into ``1``. Configuration values are therefore
hashed via ``repr`` of the Python float, which is round-trip exact in CPython, after
normalising ints that are exactly representable as floats *only when they came from a
float field*. We do not silently coerce types — a config that changes ``1`` to ``1.0``
changes the hash, and that is intentional: it is a config change.
"""

from __future__ import annotations

import hashlib
import io
import json
import os
from typing import Any, Iterable, Mapping

#: Read size for file hashing. Chosen to keep memory flat on large derived artefacts.
_CHUNK = 1 << 20


def canonical_json(obj: Any) -> str:
    """Serialise ``obj`` deterministically.

    Sorted keys, no insignificant whitespace, UTF-8, ``NaN``/``Infinity`` rejected —
    a non-finite value in a configuration is almost always a bug, and silently hashing
    it would hide that.
    """
    return json.dumps(
        obj,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def hash_object(obj: Any) -> str:
    """SHA-256 of the canonical serialisation of ``obj``."""
    return hashlib.sha256(canonical_json(obj).encode("utf-8")).hexdigest()


def hash_file(path: str | os.PathLike[str], *, normalise_text: bool = False) -> str:
    """SHA-256 of a file.

    Parameters
    ----------
    normalise_text:
        If true, hash the file as text with line endings normalised to ``\\n``. Use for
        configuration and specification files, which must hash identically when checked
        out on Windows and Linux. Leave false for binary artefacts (``.npz``, images),
        where byte identity is the thing being asserted.
    """
    h = hashlib.sha256()
    if normalise_text:
        with io.open(path, "r", encoding="utf-8", newline="") as fh:
            text = fh.read()
        h.update(text.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8"))
    else:
        with io.open(path, "rb") as fh:
            while True:
                chunk = fh.read(_CHUNK)
                if not chunk:
                    break
                h.update(chunk)
    return h.hexdigest()


def hash_files(paths: Iterable[str | os.PathLike[str]], *, root: str | os.PathLike[str] = ".") -> dict[str, str]:
    """Map repository-relative path -> SHA-256, sorted.

    Paths are stored relative to ``root`` so that a checksum manifest is portable and
    contains no machine-specific path (public repository policy).
    """
    out: dict[str, str] = {}
    for p in paths:
        rel = os.path.relpath(os.fspath(p), os.fspath(root)).replace(os.sep, "/")
        out[rel] = hash_file(p)
    return dict(sorted(out.items()))


def write_checksums(mapping: Mapping[str, str], path: str | os.PathLike[str]) -> None:
    """Write a ``sha256sum``-compatible checksum file (LF endings, sorted)."""
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        for rel, digest in sorted(mapping.items()):
            fh.write(f"{digest}  {rel}\n")


def verify_checksums(path: str | os.PathLike[str], *, root: str | os.PathLike[str] = ".") -> list[str]:
    """Verify a checksum file; return a list of mismatching/missing entries.

    Empty list means every recorded artefact is byte-identical to its record.
    """
    problems: list[str] = []
    with io.open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.rstrip("\n")
            if not line.strip():
                continue
            digest, _, rel = line.partition("  ")
            target = os.path.join(os.fspath(root), rel)
            if not os.path.exists(target):
                problems.append(f"missing: {rel}")
                continue
            if hash_file(target) != digest:
                problems.append(f"changed: {rel}")
    return problems
