"""AURA — auditable computational research infrastructure for aerospace engineering.

AURA is a framework for designing, executing, validating, analysing and documenting
computational research experiments so that assumptions, failures, uncertainty,
provenance and scientific decisions are explicit rather than implicit.

It is **not** a fault-diagnosis algorithm, an ML system, a flight-control system or a
safety-certification framework. See ``docs/RESEARCH_ENGINEERING_MISSION.md``.

Design constraints (see ``docs/ARCHITECTURE.md``):

* stdlib + numpy only — no scipy, no jsonschema, no pytest requirement;
* no hidden global state; no silent failure;
* every artefact carries provenance; every conclusion carries an evidence class.
"""

__version__ = "0.8.0"

# Framework version is recorded in provenance. Bump on any change that could alter
# recorded results or the meaning of a stored artefact.
FRAMEWORK_VERSION = __version__

__all__ = ["FRAMEWORK_VERSION", "__version__"]
