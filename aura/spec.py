"""The experiment specification: AURA's central artefact.

A specification is a pre-registration. It states the question, the hypothesis, the
prediction, the variables, the metrics, the gates and the precision target *before*
execution, and it is hashed so that any later divergence is detectable rather than
deniable.

The schema below is derived from four real AURA experiments (EXP-0002, 0010, 0011,
0012) rather than invented: every required field exists because its absence caused a
concrete problem in that record. See ``docs/EXPERIMENT_SCHEMA.md`` for the field-by-field
rationale.
"""

from __future__ import annotations

import io
import os
import re
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Mapping, Optional

import yaml

from .errors import SpecificationError
from .hashing import hash_object
from .status import Status

#: Experiment identifiers. ``DEMO-`` is reserved for framework demonstrations so that
#: they can never be mistaken for research results in the registry.
ID_PATTERN = re.compile(r"^(EXP|DEMO)-\d{4}$")

#: Recognised experiment kinds. ``confirmatory`` additionally requires a frozen test
#: declaration, because that is the mode in which contamination matters.
KINDS = frozenset({"exploratory", "confirmatory", "calibration", "infrastructure"})


@dataclass(frozen=True)
class Variables:
    """Independent, dependent and controlled variables.

    Requiring all three separately prevents the most common specification defect: a
    sweep whose "controlled" variables were never written down, so that a later reader
    cannot tell whether something changed between two compared runs.
    """

    independent: Dict[str, Any] = field(default_factory=dict)
    dependent: List[str] = field(default_factory=list)
    controlled: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ModelRef:
    """The model under study and the envelope inside which it is considered valid.

    ``validity_envelope`` is the direct descendant of FAIL-0001: flight condition FC-4
    produced the most favourable-looking numbers in EXP-0002 while departing controlled
    flight. Numbers from outside a declared envelope are not evidence, and the runtime
    gate enforces this automatically.
    """

    identifier: str
    version: str
    validity_envelope: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class DatasetRef:
    """A dataset the experiment consumes or produces."""

    identifier: str
    version: str
    role: str = "input"  # input | output


@dataclass(frozen=True)
class Randomisation:
    """Stochastic control.

    ``base_seed`` plus ``label_fields`` fully determines every per-cell seed through
    :mod:`aura.seeds`, so seeds need not be stored individually for large sweeps.
    """

    enabled: bool = False
    base_seed: Optional[int] = None
    label_fields: List[str] = field(default_factory=list)
    repetitions: Optional[int] = None


@dataclass(frozen=True)
class StatisticalPrecision:
    """A pre-declared precision target.

    Present so that the number of trials is a *derived* quantity rather than one the
    researcher typed. The framework computes the required N, measures what was
    achieved, and reports both.
    """

    metric: str  # proportion | mean
    confidence: float = 0.95
    half_width: float = 0.01
    planning_value: Optional[float] = None  # p for proportion, sigma for mean


@dataclass(frozen=True)
class FrozenTest:
    """Frozen-test declaration.

    ``enabled: false`` is a legitimate answer, but it must be *stated*. An unstated
    frozen-test policy is how test sets get tuned on by accident.
    """

    enabled: bool = False
    path: Optional[str] = None
    checksum_file: Optional[str] = None


@dataclass(frozen=True)
class ExperimentSpec:
    """A complete, validated experiment specification."""

    experiment_id: str
    title: str
    kind: str
    research_question: str
    hypothesis: str
    prediction: str
    variables: Variables
    metrics: List[str]
    model: ModelRef
    datasets: List[DatasetRef]
    assumptions: List[str]
    gates: List[str]
    randomisation: Randomisation = field(default_factory=Randomisation)
    statistical_precision: Optional[StatisticalPrecision] = None
    frozen_test: FrozenTest = field(default_factory=FrozenTest)
    output_dir: str = ""
    status: str = Status.PLANNED.value
    notes: str = ""
    source_path: Optional[str] = None

    # ------------------------------------------------------------------ construction
    @staticmethod
    def from_mapping(data: Mapping[str, Any], source_path: str | None = None) -> "ExperimentSpec":
        """Build a spec from a mapping, raising :class:`SpecificationError` on defects.

        Structural problems are raised here; semantic and filesystem problems are the
        job of :mod:`aura.validation`, which runs afterwards and can report several at
        once.
        """
        if not isinstance(data, Mapping):
            raise SpecificationError("specification must be a mapping")

        def req(key: str) -> Any:
            if key not in data or data[key] in (None, "", [], {}):
                raise SpecificationError("required field is missing or empty", field=key)
            return data[key]

        raw_vars = data.get("variables") or {}
        if not isinstance(raw_vars, Mapping):
            raise SpecificationError("must be a mapping", field="variables")
        variables = Variables(
            independent=dict(raw_vars.get("independent") or {}),
            dependent=list(raw_vars.get("dependent") or []),
            controlled=dict(raw_vars.get("controlled") or {}),
        )

        raw_model = req("model")
        if not isinstance(raw_model, Mapping):
            raise SpecificationError("must be a mapping", field="model")
        model = ModelRef(
            identifier=str(raw_model.get("identifier") or ""),
            version=str(raw_model.get("version") or ""),
            validity_envelope=dict(raw_model.get("validity_envelope") or {}),
        )

        datasets = []
        for i, d in enumerate(data.get("datasets") or []):
            if not isinstance(d, Mapping):
                raise SpecificationError(f"entry {i} must be a mapping", field="datasets")
            datasets.append(
                DatasetRef(
                    identifier=str(d.get("identifier") or ""),
                    version=str(d.get("version") or ""),
                    role=str(d.get("role") or "input"),
                )
            )

        raw_rand = data.get("randomisation") or data.get("randomization") or {}
        randomisation = Randomisation(
            enabled=bool(raw_rand.get("enabled", False)),
            base_seed=raw_rand.get("base_seed"),
            label_fields=list(raw_rand.get("label_fields") or []),
            repetitions=raw_rand.get("repetitions"),
        )

        raw_prec = data.get("statistical_precision")
        precision = None
        if raw_prec:
            precision = StatisticalPrecision(
                metric=str(raw_prec.get("metric") or ""),
                confidence=float(raw_prec.get("confidence", 0.95)),
                half_width=float(raw_prec.get("half_width", 0.01)),
                planning_value=raw_prec.get("planning_value"),
            )

        raw_frozen = data.get("frozen_test") or {}
        frozen = FrozenTest(
            enabled=bool(raw_frozen.get("enabled", False)),
            path=raw_frozen.get("path"),
            checksum_file=raw_frozen.get("checksum_file"),
        )

        return ExperimentSpec(
            experiment_id=str(req("experiment_id")),
            title=str(req("title")),
            kind=str(req("kind")),
            research_question=str(req("research_question")),
            hypothesis=str(req("hypothesis")),
            prediction=str(req("prediction")),
            variables=variables,
            metrics=[str(m) for m in req("metrics")],
            model=model,
            datasets=datasets,
            assumptions=[str(a) for a in (data.get("assumptions") or [])],
            gates=[str(g) for g in (data.get("gates") or [])],
            randomisation=randomisation,
            statistical_precision=precision,
            frozen_test=frozen,
            output_dir=str(data.get("output_dir") or ""),
            status=str(data.get("status") or Status.PLANNED.value),
            notes=str(data.get("notes") or ""),
            source_path=source_path,
        )

    @staticmethod
    def load(path: str | os.PathLike[str]) -> "ExperimentSpec":
        """Load and structurally validate a YAML specification."""
        with io.open(path, "r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        rel = os.path.normpath(os.fspath(path)).replace(os.sep, "/")
        # Strip a leading "./" so the recorded path is a clean repository-relative one.
        rel = rel[2:] if rel.startswith("./") else rel
        return ExperimentSpec.from_mapping(data or {}, source_path=rel)

    # ------------------------------------------------------------------- serialisation
    def to_dict(self, *, include_source: bool = True) -> Dict[str, Any]:
        """Plain-data view. ``include_source=False`` gives the hashable content."""
        d = asdict(self)
        if not include_source:
            d.pop("source_path", None)
            # Status is lifecycle metadata, not part of the pre-registered content.
            d.pop("status", None)
        return d

    @property
    def content_hash(self) -> str:
        """SHA-256 of the *scientific content* of the specification.

        Excludes ``status`` and ``source_path`` so that moving a file or advancing the
        lifecycle does not look like a change to the pre-registration — while any edit
        to the question, hypothesis, prediction, variables, metrics, gates or precision
        target does.
        """
        return hash_object(self.to_dict(include_source=False))

    def dump(self, path: str | os.PathLike[str]) -> None:
        """Write the specification back to YAML with stable key order."""
        with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
            yaml.safe_dump(self.to_dict(), fh, sort_keys=True, allow_unicode=True)
