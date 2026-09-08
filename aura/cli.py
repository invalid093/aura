"""Command-line interface.

A polished CLI is the deliverable; there is deliberately no dashboard
(portfolio specification §29 — a GUI over weak infrastructure is worth less than a
clean command-line workflow).

Commands::

    python -m aura registry list
    python -m aura validate <ID|path>
    python -m aura run <ID>
    python -m aura gates
    python -m aura failures
    python -m aura compare <ID_A> <ID_B>
    python -m aura provenance <ID>
    python -m aura verify <ID>
"""

from __future__ import annotations

import argparse
import importlib
import importlib.util
import io
import json
import os
import sys

import yaml
from typing import Any, Dict, List, Optional, Sequence

from . import FRAMEWORK_VERSION
from .compare import compare as compare_specs
from .errors import AuraError
from .failures import FailureRegistry
from .gates import GATE_REGISTRY
from .hashing import verify_checksums
from .registry import Registry
from .runner import run as run_experiment
from .spec import ExperimentSpec
from .validation import validate_spec


def _load_spec(root: str, ident: str) -> ExperimentSpec:
    """Accept either an experiment id or a path to a spec file."""
    if os.path.exists(ident):
        return ExperimentSpec.load(ident)
    return Registry(root).load(ident)


def _load_statistics(root: str, spec: ExperimentSpec) -> Dict[str, Any]:
    path = os.path.join(root, spec.output_dir, "statistics.json")
    if not os.path.exists(path):
        return {}
    with io.open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def load_experiment_module(path: str, *, root: str = ".") -> Any:
    """Load an experiment module by file path.

    Path-based rather than import-based because experiment ids contain hyphens
    (``DEMO-0001``), which are not valid Python identifiers. The repository root is put
    on ``sys.path`` so experiments can import shared models.
    """
    root_abs = os.path.abspath(root)
    if root_abs not in sys.path:
        sys.path.insert(0, root_abs)
    if not os.path.exists(path):
        raise OSError(f"no such experiment module: {path}")
    name = "aura_experiment_" + os.path.basename(os.path.dirname(os.path.abspath(path))).replace("-", "_")
    module_spec = importlib.util.spec_from_file_location(name, path)
    if module_spec is None or module_spec.loader is None:
        raise ImportError(f"cannot build a module spec for {path}")
    module = importlib.util.module_from_spec(module_spec)
    sys.modules[name] = module
    module_spec.loader.exec_module(module)
    return module


# --------------------------------------------------------------------------- commands
def cmd_registry(args: argparse.Namespace) -> int:
    reg = Registry(args.root)
    entries = reg.entries()
    if args.json:
        print(json.dumps([e.to_dict() for e in entries], indent=2))
        return 0
    if not entries:
        print("No experiments registered.")
        return 0
    width = max(len(e.experiment_id) for e in entries)
    print(f"{'ID'.ljust(width)}  {'STATUS'.ljust(13)} {'KIND'.ljust(14)} TITLE")
    for e in entries:
        legacy = "  (legacy record)" if e.legacy else ""
        print(f"{e.experiment_id.ljust(width)}  {e.status.ljust(13)} {e.kind.ljust(14)} {e.title}{legacy}")
    s = reg.summary()
    print(f"\n{s['total']} experiment(s): {s['by_status']}")
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    spec = _load_spec(args.root, args.experiment)
    reg = Registry(args.root)
    known = [i for i in reg.ids() if i != spec.experiment_id]
    report = validate_spec(
        spec, root=args.root, known_experiment_ids=known,
        allow_existing_output=args.allow_existing_output,
    )
    if args.json:
        print(json.dumps(report.to_dict(), indent=2))
    else:
        print(f"{spec.experiment_id}: {'VALID' if report.ok else 'REJECTED'}")
        for p in report.problems:
            print(f"  {p}")
        if report.ok and not report.problems:
            print("  no problems found")
    return 0 if report.ok else 1


def cmd_run(args: argparse.Namespace) -> int:
    spec = _load_spec(args.root, args.experiment)
    module_path = args.module or os.path.join(
        args.root, "experiments", spec.experiment_id, "experiment.py"
    )
    try:
        module = load_experiment_module(module_path, root=args.root)
    except (OSError, ImportError) as exc:
        print(f"error: cannot load experiment module {module_path!r}: {exc}", file=sys.stderr)
        return 2
    if not hasattr(module, "execute"):
        print(f"error: {module_path} defines no execute(context) function", file=sys.stderr)
        return 2

    outcome = run_experiment(spec, module.execute, root=args.root)
    print(f"{outcome.experiment_id}: status {outcome.status.value}, "
          f"gates {outcome.gate_summary['overall']}")
    for r in outcome.gate_summary["results"]:
        mark = "PASS" if r["outcome"] == "PASS" else r["outcome"]
        print(f"  [{mark:12}] {r['name']} ({r['phase']}): {r['detail']}")
    if outcome.failure_id:
        print(f"  failure recorded: {outcome.failure_id}")
    print(f"  evidence package: {outcome.package_dir}")
    print(f"  scientific conclusion emitted: {outcome.conclusion_emitted}")
    # A rejected experiment is a successful *framework* outcome, so exit 0 unless the
    # run failed outright. Callers wanting the scientific status should read metadata.
    return 0 if outcome.status.value != "FAILED" else 1


def cmd_gates(args: argparse.Namespace) -> int:
    rows = sorted(GATE_REGISTRY.values(), key=lambda g: (g.phase.value, g.name))
    if args.json:
        print(json.dumps(
            [{"name": g.name, "phase": g.phase.value, "description": g.description,
              "required_context": list(g.required_context)} for g in rows], indent=2))
        return 0
    width = max(len(g.name) for g in rows)
    for g in rows:
        print(f"{g.phase.value.ljust(12)} {g.name.ljust(width)}  {g.description}")
    return 0


def cmd_failures(args: argparse.Namespace) -> int:
    reg = FailureRegistry(os.path.join(args.root, "experiments", "failures"))
    records = reg.load_all()
    if args.json:
        print(json.dumps([r.to_dict() for r in records], indent=2))
        return 0
    if not records:
        print("No failure records.")
        return 0
    for r in records:
        test = f"  -> regression test: {r.became_test}" if r.became_test else ""
        print(f"{r.failure_id}  {r.status.ljust(12)} {r.experiment_id.ljust(10)} {r.title}{test}")
    print(f"\n{json.dumps(reg.summary(), indent=2)}")
    return 0


def cmd_compare(args: argparse.Namespace) -> int:
    left = _load_spec(args.root, args.left)
    right = _load_spec(args.root, args.right)
    result = compare_specs(
        left, right,
        left_stats=_load_statistics(args.root, left),
        right_stats=_load_statistics(args.root, right),
    )
    if args.json:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print(result.render())
    return 0 if result.comparable else 1


def cmd_provenance(args: argparse.Namespace) -> int:
    spec = _load_spec(args.root, args.experiment)
    path = os.path.join(args.root, spec.output_dir, "provenance.json")
    if not os.path.exists(path):
        print(f"no provenance record at {spec.output_dir}/provenance.json "
              f"(has {spec.experiment_id} been run?)", file=sys.stderr)
        return 1
    with io.open(path, "r", encoding="utf-8") as fh:
        prov = json.load(fh)
    if args.json:
        print(json.dumps(prov, indent=2))
        return 0
    print(f"Provenance for {spec.experiment_id} (run {prov['run_id']})\n")
    print(f"  result        <- {args.metric}")
    print(f"  experiment    <- {prov['experiment_id']}")
    print(f"  specification <- {prov['spec_path']}  sha256:{prov['spec_hash'][:16]}")
    for name, digest in sorted(prov.get("config_hashes", {}).items()):
        print(f"  configuration <- {name}  sha256:{digest[:16]}")
    for ident, version in sorted(prov.get("dataset_versions", {}).items()):
        print(f"  dataset       <- {ident} @ {version}")
    m = prov.get("model", {})
    print(f"  model         <- {m.get('identifier')} @ {m.get('version')}")
    c = prov.get("code", {})
    print(f"  code          <- {c.get('git_commit')} (dirty={c.get('git_dirty')}) "
          f"framework={c.get('framework_version')}")
    s = prov.get("seed_policy", {})
    print(f"  seed          <- base={s.get('base_seed')} labels={s.get('label_fields')}")
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    """Re-verify a finalised evidence package against its recorded checksums."""
    spec = _load_spec(args.root, args.experiment)
    out_dir = os.path.join(args.root, spec.output_dir)
    checks = os.path.join(out_dir, "checksums.txt")
    if not os.path.exists(checks):
        print(f"no checksums.txt in {spec.output_dir}", file=sys.stderr)
        return 1
    problems = verify_checksums(checks, root=out_dir)
    if problems:
        print(f"{spec.experiment_id}: EVIDENCE PACKAGE MODIFIED")
        for p in problems:
            print(f"  {p}")
        return 1
    print(f"{spec.experiment_id}: evidence package verified — all artefacts unchanged")
    return 0


# ------------------------------------------------------------------------------ parser
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="aura",
        description="Auditable computational research infrastructure for aerospace engineering.",
    )
    p.add_argument("--version", action="version", version=f"aura {FRAMEWORK_VERSION}")
    p.add_argument("--root", default=".", help="repository root (default: current directory)")
    sub = p.add_subparsers(dest="command", required=True)

    r = sub.add_parser("registry", help="list registered experiments")
    r.add_argument("action", nargs="?", default="list", choices=["list"])
    r.add_argument("--json", action="store_true")
    r.set_defaults(func=cmd_registry)

    v = sub.add_parser("validate", help="validate an experiment specification")
    v.add_argument("experiment", help="experiment id or path to spec.yaml")
    v.add_argument("--json", action="store_true")
    v.add_argument("--allow-existing-output", action="store_true")
    v.set_defaults(func=cmd_validate)

    ru = sub.add_parser("run", help="execute an experiment through the full lifecycle")
    ru.add_argument("experiment")
    ru.add_argument("--module", help="override the experiment module import path")
    ru.set_defaults(func=cmd_run)

    g = sub.add_parser("gates", help="list registered validity gates")
    g.add_argument("--json", action="store_true")
    g.set_defaults(func=cmd_gates)

    f = sub.add_parser("failures", help="list failure records")
    f.add_argument("--json", action="store_true")
    f.set_defaults(func=cmd_failures)

    c = sub.add_parser("compare", help="compare two experiments for commensurability")
    c.add_argument("left")
    c.add_argument("right")
    c.add_argument("--json", action="store_true")
    c.set_defaults(func=cmd_compare)

    pr = sub.add_parser("provenance", help="trace where a result came from")
    pr.add_argument("experiment")
    pr.add_argument("--metric", default="<metric>")
    pr.add_argument("--json", action="store_true")
    pr.set_defaults(func=cmd_provenance)

    ve = sub.add_parser("verify", help="verify a finalised evidence package")
    ve.add_argument("experiment")
    ve.set_defaults(func=cmd_verify)
    return p


def _force_utf8_stdout() -> None:
    """Make stdout UTF-8 where possible.

    Windows consoles default to a legacy codepage (cp1252) that cannot encode characters
    used in generated documents. Reconfiguring avoids a crash that would otherwise depend
    on which terminal the researcher happens to be using.
    """
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            try:
                reconfigure(encoding="utf-8", errors="replace")
            except (ValueError, OSError):
                pass


def main(argv: Optional[Sequence[str]] = None) -> int:
    _force_utf8_stdout()
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except AuraError as exc:
        print(f"error: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    except yaml.YAMLError as exc:
        # A malformed specification is a user error, not a framework crash. Report it
        # as such -- a traceback here would obscure which file is at fault.
        print(f"error: malformed YAML in specification: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
