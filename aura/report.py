"""Research report generation.

The single editorial rule this module enforces mechanically:

> **A numerical result is never automatically converted into a scientific conclusion.**

The generator can state what was measured, with what precision, under which assumptions,
and whether the gates permitted interpretation at all. It cannot state what the result
*means*: that is an ``INTERPRETATION``, and interpretations must be supplied by the
researcher and are rendered in a separate section, clearly attributed.

If the gates blocked interpretation, the report says so and emits **no** conclusion
section, whatever interpretations were supplied.
"""

from __future__ import annotations

import io
import os
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence

from .evidence import EvidenceClass, Statement, check_statements, partition
from .gates import Outcome
from .provenance import Provenance, trace
from .spec import ExperimentSpec
from .status import Status, is_interpretable


def _fmt_interval(iv: Mapping[str, Any] | None) -> str:
    if not iv:
        return "not computed"
    return (
        f"{iv['point']:.6g} "
        f"[{iv['low']:.6g}, {iv['high']:.6g}] "
        f"({iv['confidence']:.0%} {iv['method']}, n={iv['n']}, "
        f"half-width {iv['half_width']:.4g})"
    )


def _section(title: str, body: str) -> str:
    return f"## {title}\n\n{body.rstrip()}\n\n"


def generate(
    spec: ExperimentSpec,
    *,
    provenance: Provenance,
    status: Status,
    gate_summary: Mapping[str, Any],
    statistics: Mapping[str, Any],
    interpretations: Sequence[Statement] = (),
    deviations: Sequence[str] = (),
    failures: Sequence[str] = (),
    limitations: Sequence[str] = (),
) -> str:
    """Render a complete research report as Markdown.

    Parameters
    ----------
    interpretations:
        Researcher-supplied statements. Any statement whose class *is measured*
        (FACT/CALCULATION/OBSERVATION) is rejected here — measured content must come
        from the recorded artefacts, not from prose, or the report would launder an
        assertion into a measurement.
    deviations:
        Differences between what was pre-registered and what was run. An empty list is
        rendered explicitly as "none recorded" rather than omitted.
    """
    bad = [s for s in interpretations if s.evidence.is_measured]
    if bad:
        raise ValueError(
            "researcher statements may not claim measured evidence classes "
            f"({[s.evidence.value for s in bad]}); measured content comes from the "
            "recorded artefacts, not from supplied prose"
        )
    problems = check_statements(interpretations)

    blocked = bool(gate_summary.get("blocks_conclusion")) or not is_interpretable(status)
    out: List[str] = []

    out.append(f"# {spec.experiment_id} — {spec.title}\n\n")
    out.append(
        f"**Status:** `{status.value}` · **Kind:** {spec.kind} · "
        f"**Gates:** `{gate_summary.get('overall', 'UNKNOWN')}` · "
        f"**Run:** `{provenance.run_id}` · **Generated:** {provenance.finished_utc or provenance.started_utc}\n\n"
    )
    if blocked:
        out.append(
            "> ### No scientific conclusion is emitted for this experiment.\n"
            f"> The run finished with status `{status.value}` and overall gate outcome "
            f"`{gate_summary.get('overall')}`. Its numbers are recorded below as evidence of "
            "*what the run did*, not as evidence about the research question. "
            "Interpreting them would mean drawing a conclusion from a run the framework "
            "rejected.\n\n"
        )
    out.append("---\n\n")

    out.append(_section("Research question", spec.research_question))
    out.append(_section("Hypothesis", spec.hypothesis))
    out.append(_section("Prediction", f"Pre-registered before execution:\n\n> {spec.prediction}"))

    # ------------------------------------------------------------------ design
    design = ["| Role | Variable | Value |", "|---|---|---|"]
    for k, v in sorted(spec.variables.independent.items()):
        design.append(f"| independent | `{k}` | {v} |")
    for d in spec.variables.dependent:
        design.append(f"| dependent | `{d}` | measured |")
    for k, v in sorted(spec.variables.controlled.items()):
        design.append(f"| controlled | `{k}` | {v} |")
    out.append(_section("Experimental design", "\n".join(design)))

    out.append(
        _section(
            "Assumptions",
            "The results below are conditional on every one of these.\n\n"
            + "\n".join(f"- **`ASSUMPTION`** {a}" for a in spec.assumptions),
        )
    )

    # ------------------------------------------------------------------ configuration
    cfg = ["| Item | Value |", "|---|---|",
           f"| model | `{spec.model.identifier}` @ `{spec.model.version}` |"]
    for key, bounds in sorted(spec.model.validity_envelope.items()):
        cfg.append(f"| validity envelope `{key}` | {bounds} |")
    for d in spec.datasets:
        cfg.append(f"| dataset ({d.role}) | `{d.identifier}` @ `{d.version}` |")
    for name, digest in sorted(provenance.config_hashes.items()):
        cfg.append(f"| config `{name}` | `sha256:{digest[:16]}…` |")
    if spec.randomisation.enabled:
        cfg.append(f"| seed policy | base `{spec.randomisation.base_seed}` "
                   f"over `{spec.randomisation.label_fields}` |")
    out.append(_section("Configuration", "\n".join(cfg)))

    # ------------------------------------------------------------------ gates
    rows = ["| Gate | Phase | Outcome | Detail |", "|---|---|---|---|"]
    for r in gate_summary.get("results", []):
        mark = "✅" if r["outcome"] == Outcome.PASS.value else "❌"
        rows.append(f"| `{r['name']}` | {r['phase']} | {mark} **{r['outcome']}** | {r['detail']} |")
    rows.append("")
    rows.append(f"**Overall: `{gate_summary.get('overall')}`**")
    out.append(_section("Validation gates", "\n".join(rows)))

    # ------------------------------------------------------------------ execution
    exec_rows = [
        "| Item | Value |", "|---|---|",
        f"| started (UTC) | {provenance.started_utc} |",
        f"| finished (UTC) | {provenance.finished_utc or 'n/a'} |",
        f"| runtime (s) | {provenance.runtime_seconds if provenance.runtime_seconds is not None else 'n/a'} |",
        f"| code | `{(provenance.code.git_commit or 'UNKNOWN')[:12]}`"
        f"{' **(dirty tree)**' if provenance.code.git_dirty else ''} |",
        f"| framework | `{provenance.code.framework_version}` |",
        f"| python | {provenance.environment.python_version} on "
        f"{provenance.environment.platform_system}/{provenance.environment.platform_machine} |",
        f"| numpy | {provenance.environment.numpy_version} |",
    ]
    out.append(_section("Execution", "\n".join(exec_rows)))

    # ------------------------------------------------------------------ results
    res: List[str] = []
    for metric, payload in sorted(statistics.items()):
        res.append(f"### `{metric}`\n")
        if isinstance(payload, Mapping) and "interval" in payload:
            res.append(f"- **`CALCULATION`** estimate: {_fmt_interval(payload['interval'])}")
            res.append(f"- trials: requested {payload.get('n_requested')}, "
                       f"completed {payload.get('n_completed')}, failed {payload.get('n_failed')}")
            if payload.get("required_n") is not None:
                res.append(f"- required N for the declared precision: {payload['required_n']}")
        else:
            res.append(f"- **`CALCULATION`** value: `{payload}`")
        res.append("")
    out.append(_section("Results", "\n".join(res) if res else "No metrics were recorded."))

    # ------------------------------------------------------------------ uncertainty
    unc: List[str] = []
    sp = spec.statistical_precision
    if sp:
        unc.append(
            f"Pre-declared target: **{sp.metric}**, half-width ≤ {sp.half_width:g} "
            f"at {sp.confidence:.0%} confidence."
        )
    for metric, payload in sorted(statistics.items()):
        if isinstance(payload, Mapping) and payload.get("convergence"):
            t = payload["convergence"]
            unc.append(
                f"\n`{metric}` convergence — half-width "
                f"{t[0]['half_width']:.4g} at n={t[0]['n']} → "
                f"{t[-1]['half_width']:.4g} at n={t[-1]['n']}."
            )
    unc.append(
        "\n**`LIMITATION`** These intervals describe sampling precision under the stated "
        "assumptions only. They do not establish that the modelled system is the right one, "
        "and a satisfied precision target is not a validated result."
    )
    out.append(_section("Statistical uncertainty", "\n".join(unc)))

    out.append(
        _section(
            "Failures",
            "\n".join(f"- {f}" for f in failures) if failures else "None recorded for this run.",
        )
    )
    out.append(
        _section(
            "Deviations from preregistration",
            "\n".join(f"- {d}" for d in deviations)
            if deviations
            else f"None recorded. Specification hash `{spec.content_hash[:16]}…` "
                 "matches the pre-registered content.",
        )
    )

    # ------------------------------------------------------------------ evidence split
    measured, inferred = partition(interpretations)
    ev = [
        "AURA separates what the system measured from what a researcher inferred. "
        "The two are never rendered in the same section.\n",
        "### What the system measured\n",
    ]
    ev.append(
        "\n".join(
            f"- **`CALCULATION`** `{m}` = {_fmt_interval(p['interval']) if isinstance(p, Mapping) and 'interval' in p else p}"
            for m, p in sorted(statistics.items())
        )
        or "- (no metrics recorded)"
    )
    ev.append("\n### What the researcher inferred\n")
    if inferred:
        ev.append("\n".join(f"- {s.render()}" for s in inferred))
    else:
        ev.append("- None supplied. The report therefore asserts no interpretation.")
    if problems:
        ev.append("\n**Editorial problems detected:**\n" + "\n".join(f"- {p}" for p in problems))
    out.append(_section("Evidence classification", "\n".join(ev)))

    # ------------------------------------------------------------------ support / not
    if blocked:
        out.append(
            _section(
                "What the evidence supports",
                "**Nothing.** The gates rejected this run, so it supports no claim about the "
                "research question. This section is deliberately empty rather than omitted, so "
                "that its emptiness is visible.",
            )
        )
    else:
        supports = [
            f"- **`CALCULATION`** `{m}` was measured as {_fmt_interval(p['interval'])}"
            for m, p in sorted(statistics.items())
            if isinstance(p, Mapping) and "interval" in p
        ]
        out.append(
            _section(
                "What the evidence supports",
                "Under the assumptions listed above, and at the stated precision:\n\n"
                + ("\n".join(supports) or "- (no interval-valued metric was recorded)")
                + "\n\n**`LIMITATION`** These are measurements, not conclusions. "
                "Whether they support the hypothesis is an interpretation, and appears "
                "only where a researcher has supplied one.",
            )
        )

    not_supported = [
        "- Any claim beyond the declared validity envelope of the model.",
        "- Any claim about a system, condition or fault not present in this configuration.",
        "- Any causal claim: this experiment measures association under a fixed design.",
    ]
    if not interpretations:
        not_supported.append(
            "- Any statement of what the numbers *mean*: no interpretation was supplied."
        )
    out.append(_section("What the evidence does not support", "\n".join(not_supported)))

    lim = list(limitations)
    if provenance.code.git_dirty:
        lim.append(
            "The working tree was dirty at execution time, so the recorded commit alone "
            "does not reproduce this run."
        )
    out.append(
        _section(
            "Limitations",
            "\n".join(f"- **`LIMITATION`** {x}" for x in lim) if lim else "None recorded.",
        )
    )

    # ------------------------------------------------------------------ reproducibility
    repro = ["To reproduce this run:", "", "```bash",
             f"python -m aura run {spec.experiment_id}", "```", "",
             "Provenance chain for any reported metric:", ""]
    repro += [f"{i + 1}. {link}" for i, link in enumerate(trace(provenance, "<metric>"))]
    out.append(_section("Reproducibility information", "\n".join(repro)))

    # ------------------------------------------------------------------ decision
    if blocked:
        decision = (
            f"**`{status.value}` — no scientific conclusion.** "
            f"Overall gate outcome `{gate_summary.get('overall')}`. "
            "The correct next action is to address the gate failure recorded above, not to "
            "reinterpret these numbers."
        )
    else:
        decision = (
            f"**`{status.value}`** — the run was valid and achieved its declared precision. "
            "What it implies for the hypothesis is a researcher judgement and is not "
            "generated automatically; see *What the researcher inferred*."
        )
    out.append(_section("Final decision", decision))

    return "".join(out)


def write(path: str | os.PathLike[str], content: str) -> str:
    """Write a report, creating parent directories. Returns the path."""
    os.makedirs(os.path.dirname(os.fspath(path)) or ".", exist_ok=True)
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(content)
    return os.fspath(path).replace(os.sep, "/")
