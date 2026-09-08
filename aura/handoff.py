"""Cross-AI / independent-review handoff generation.

A handoff is written for a reader with **no access to the repository**. Its purpose is
adversarial: it should give an independent reviewer everything needed to attack the
work, and it ends by naming what the reviewer should try to prove wrong.

This formalises the handoff practice used throughout AURA's research phase, where each
experiment produced a self-contained document that a different model or person could
critique without replaying the conversation that produced it.
"""

from __future__ import annotations

import io
import os
from typing import Any, List, Mapping, Sequence

from .evidence import Statement
from .provenance import Provenance
from .spec import ExperimentSpec
from .status import Status, is_interpretable


def _fmt_interval(iv: Mapping[str, Any] | None) -> str:
    if not iv:
        return "not computed"
    return (
        f"{iv['point']:.6g} [{iv['low']:.6g}, {iv['high']:.6g}] "
        f"({iv['confidence']:.0%}, {iv['method']}, n={iv['n']})"
    )


def generate(
    spec: ExperimentSpec,
    *,
    provenance: Provenance,
    status: Status,
    gate_summary: Mapping[str, Any],
    statistics: Mapping[str, Any],
    interpretations: Sequence[Statement] = (),
    corrections: Sequence[str] = (),
    failures: Sequence[str] = (),
    limitations: Sequence[str] = (),
    review_questions: Sequence[str] = (),
) -> str:
    """Render a self-contained handoff document."""
    blocked = bool(gate_summary.get("blocks_conclusion")) or not is_interpretable(status)
    o: List[str] = []

    o.append(f"# HANDOFF — {spec.experiment_id}: {spec.title}\n\n")
    o.append(
        "**This document is self-contained.** It assumes no access to the repository and no "
        "memory of the session that produced it. It is written to be attacked.\n\n"
    )
    o.append(
        f"**Status:** `{status.value}` · **Gates:** `{gate_summary.get('overall')}` · "
        f"**Run:** `{provenance.run_id}` · "
        f"**Code:** `{(provenance.code.git_commit or 'UNKNOWN')[:12]}`"
        f"{' (dirty)' if provenance.code.git_dirty else ''}\n\n---\n\n"
    )

    if blocked:
        o.append(
            "## ⚠ This experiment produced no scientific conclusion\n\n"
            f"The run ended `{status.value}` with overall gate outcome "
            f"`{gate_summary.get('overall')}`. The numbers below describe what the run did. "
            "They are **not** evidence about the research question, and a reviewer should treat "
            "any interpretation of them as unsupported.\n\n"
        )

    o.append(f"## Objective\n\n{spec.research_question}\n\n")
    o.append(f"## Hypothesis\n\n{spec.hypothesis}\n\n")
    o.append(f"## Prediction (pre-registered)\n\n> {spec.prediction}\n\n")

    o.append("## Setup\n\n")
    o.append(f"- **Model:** `{spec.model.identifier}` version `{spec.model.version}`\n")
    if spec.model.validity_envelope:
        o.append("- **Declared validity envelope:**\n")
        for k, v in sorted(spec.model.validity_envelope.items()):
            o.append(f"  - `{k}` ∈ {v}\n")
    for d in spec.datasets:
        o.append(f"- **Dataset ({d.role}):** `{d.identifier}` @ `{d.version}`\n")
    if spec.randomisation.enabled:
        o.append(
            f"- **Randomisation:** base seed `{spec.randomisation.base_seed}`, "
            f"per-cell seeds derived by SHA-256 over `{spec.randomisation.label_fields}`; "
            "no global RNG state is used.\n"
        )
    else:
        o.append("- **Randomisation:** none; this is a deterministic experiment.\n")
    o.append("\n")

    o.append("## Assumptions\n\nEvery result below is conditional on these.\n\n")
    o.extend(f"- **`ASSUMPTION`** {a}\n" for a in spec.assumptions)
    o.append("\n")

    o.append("## Methods\n\n")
    o.append("| Role | Variable | Value |\n|---|---|---|\n")
    for k, v in sorted(spec.variables.independent.items()):
        o.append(f"| independent | `{k}` | {v} |\n")
    for d in spec.variables.dependent:
        o.append(f"| dependent | `{d}` | measured |\n")
    for k, v in sorted(spec.variables.controlled.items()):
        o.append(f"| controlled | `{k}` | {v} |\n")
    o.append(f"\nMetrics: {', '.join('`' + m + '`' for m in spec.metrics)}\n\n")

    o.append("## Data\n\n")
    o.append(
        f"- Specification hash: `sha256:{spec.content_hash[:32]}…`\n"
        f"- Configuration hashes: "
        + (", ".join(f"`{k}`=`{v[:12]}…`" for k, v in sorted(provenance.config_hashes.items()))
           or "none recorded")
        + "\n"
        f"- Environment: python {provenance.environment.python_version}, "
        f"numpy {provenance.environment.numpy_version}, "
        f"{provenance.environment.platform_system}/{provenance.environment.platform_machine}\n\n"
    )

    o.append("## Results\n\n")
    for metric, payload in sorted(statistics.items()):
        if isinstance(payload, Mapping) and "interval" in payload:
            o.append(
                f"- **`CALCULATION`** `{metric}` = {_fmt_interval(payload['interval'])}; "
                f"trials completed {payload.get('n_completed')}/{payload.get('n_requested')}"
                f", failed {payload.get('n_failed')}\n"
            )
        else:
            o.append(f"- **`CALCULATION`** `{metric}` = `{payload}`\n")
    o.append("\n")

    o.append("## Validation gates\n\n| Gate | Phase | Outcome |\n|---|---|---|\n")
    for r in gate_summary.get("results", []):
        o.append(f"| `{r['name']}` | {r['phase']} | **{r['outcome']}** — {r['detail']} |\n")
    o.append(f"\n**Overall: `{gate_summary.get('overall')}`**\n\n")

    o.append("## Failures\n\n")
    o.extend(f"- {f}\n" for f in failures) if failures else o.append("None recorded for this run.\n")
    o.append("\n## Corrections\n\n")
    o.extend(f"- {c}\n" for c in corrections) if corrections else o.append("None recorded.\n")

    o.append("\n## Evidence classification\n\n")
    o.append("**Measured by the system:**\n\n")
    for metric in sorted(statistics):
        o.append(f"- `CALCULATION` — `{metric}`\n")
    o.append("\n**Inferred by the researcher:**\n\n")
    if interpretations:
        o.extend(f"- {s.render()}\n" for s in interpretations)
    else:
        o.append("- None supplied. No interpretation is asserted anywhere in this document.\n")

    o.append("\n## Limitations\n\n")
    lim = list(limitations)
    if provenance.code.git_dirty:
        lim.append("Working tree was dirty; the recorded commit alone does not reproduce this run.")
    if not spec.model.validity_envelope:
        lim.append("No validity envelope was declared, so envelope conformance was not checked.")
    o.extend(f"- **`LIMITATION`** {x}\n" for x in lim) if lim else o.append("None recorded.\n")

    o.append("\n## Claims that are NOT supported\n\n")
    o.append(
        "- Any claim outside the declared validity envelope.\n"
        "- Any claim of operational, real-aircraft, or safety-critical applicability.\n"
        "- Any causal claim; the design measures association under fixed conditions.\n"
    )
    if blocked:
        o.append("- **Any claim at all about the research question**: the gates rejected this run.\n")

    o.append("\n## Conclusion\n\n")
    if blocked:
        o.append(
            f"`{status.value}`. No conclusion is drawn. The framework rejected the run and the "
            "correct next action is to address the recorded gate failure.\n"
        )
    else:
        o.append(
            f"`{status.value}`. The run was valid and met its declared precision. "
            "What that implies for the hypothesis is a researcher judgement, recorded above "
            "under *inferred*, and is not generated by the framework.\n"
        )

    o.append("\n## Questions for independent review\n\n")
    o.append("**What should another researcher try to prove wrong?**\n\n")
    default_questions = [
        "Is the declared validity envelope actually the right one, or does it merely bound "
        "what this configuration happens to produce?",
        "Is the pre-registered prediction falsifiable as written, or could any outcome be "
        "read as consistent with it?",
        "Does the precision target address the question being asked, or only the one that is "
        "cheap to measure?",
        "Are the assumptions listed above complete — what is being assumed silently?",
        "Would the same specification, run by someone else from the recorded configuration, "
        "produce these numbers?",
    ]
    for q in list(review_questions) + default_questions:
        o.append(f"- {q}\n")

    return "".join(o)


def write(path: str | os.PathLike[str], content: str) -> str:
    """Write a handoff, creating parent directories. Returns the path."""
    os.makedirs(os.path.dirname(os.fspath(path)) or ".", exist_ok=True)
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(content)
    return os.fspath(path).replace(os.sep, "/")
