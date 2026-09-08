"""
EXP-0011 trajectory generation: the fault-magnitude grid.

Generates only what EXP-0002 does not already contain. The m = 1.0 slice is reused
from DS-0001 without re-simulation (public repository policy: do not regenerate
identical trajectories).

Applies the pre-declared template-validity rule from the configuration:
  - F4 (stuck) has no magnitude parameter -> one template per channel, not nine
  - a template is excluded if the run diverges or exceeds 25 deg angle of attack,
    where the aero model is extrapolating

Writes DS-0002 to data/derived/EXP-0011/ (git-ignored, regenerable) plus a manifest.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone

import numpy as np
import yaml

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)

from aircraft.gfw1 import GFW1, CHANNELS                        # noqa: E402
from aircraft.trim import trim                                  # noqa: E402
from faults.faults import Fault                                 # noqa: E402
from simulation.simulate import simulate                        # noqa: E402

CFG2P = os.path.join(ROOT, "experiments", "EXP-0002", "config", "exp0002.yaml")
CFG11P = os.path.join(ROOT, "experiments", "EXP-0011", "config", "exp0011.yaml")
OUT = os.path.join(ROOT, "data", "derived", "EXP-0011")


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for c in iter(lambda: fh.read(65536), b""):
            h.update(c)
    return h.hexdigest()


def main():
    t0 = time.perf_counter()
    os.makedirs(OUT, exist_ok=True)
    cfg2 = yaml.safe_load(open(CFG2P, encoding="utf-8"))
    cfg = yaml.safe_load(open(CFG11P, encoding="utf-8"))
    model = GFW1(cfg2)

    grid = [float(x) for x in cfg["magnitude"]["grid"]]
    tv = cfg["template_validity"]
    a_max = float(tv["exclude_if_max_alpha_deg_above"])
    fcmeta = {f["id"]: f for f in cfg2["flight_conditions"]}
    channels = cfg2["faults"]["channels"]

    # Class list: (mode, channel). F4 is magnitude-invariant; F0 needs no generation.
    classes = [(m, ch) for m in ("F1", "F2", "F3") for ch in channels]
    classes += [("F6", None)]
    # F0 (nominal) and F4 (stuck) are magnitude-free. F0 is also the reference
    # against which detectability is measured, so it must be in the template set.
    mag_invariant = [("F0", None)] + [("F4", ch) for ch in channels]

    excluded, generated, reused = [], 0, 0
    index = {}

    for fc_id in cfg["flight_conditions"]:
        fc = fcmeta[fc_id]
        x0, u0, info = trim(model, fc["airspeed_mps"], fc["altitude_m"])

        for mode, ch in classes + mag_invariant:
            cls = mode if ch is None else f"{mode}_{ch}"
            # F0 and F4 are magnitude-free: one template each, not nine.
            mags = [1.0] if mode in ("F0", "F4") else grid
            for m in mags:
                key = f"{fc_id}|{cls}|{m:.8f}"
                # Reuse the EXP-0002 slice where it already exists
                src = os.path.join(ROOT, "data", "derived", "EXP-0002",
                                   f"{fc_id}_{cls}.npz")
                if abs(m - 1.0) < 1e-12 and os.path.exists(src):
                    z = np.load(src)
                    a = np.degrees(z["y"][:, CHANNELS.index("alpha")])
                    ok = np.all(np.isfinite(z["y"])) and float(np.max(np.abs(a))) <= a_max
                    index[key] = {"path": os.path.relpath(src, ROOT).replace(os.sep, "/"), "reused": True,
                                  "max_abs_alpha_deg": float(np.max(np.abs(a))), "valid": bool(ok)}
                    if not ok:
                        excluded.append({**index[key], "key": key})
                    reused += 1
                    continue

                fn_pre = os.path.join(OUT, f"{fc_id}_{cls}_m{m:.6f}.npz")
                if os.path.exists(fn_pre):
                    z = np.load(fn_pre)
                    a = np.degrees(z["y"][:, CHANNELS.index("alpha")])
                    amax = float(np.max(np.abs(a))) if np.all(np.isfinite(a)) else float("inf")
                    ok = np.all(np.isfinite(z["y"])) and amax <= a_max
                    index[key] = {"path": os.path.relpath(fn_pre, ROOT).replace(os.sep, "/"), "reused": True,
                                  "max_abs_alpha_deg": amax, "valid": bool(ok)}
                    if not ok:
                        excluded.append({**index[key], "key": key})
                    reused += 1
                    continue

                f = Fault(mode, ch, cfg2, magnitude_scale=m)
                r = simulate(model, cfg2, x0, u0, info, f)
                a = np.degrees(r["y"][:, CHANNELS.index("alpha")])
                amax = float(np.max(np.abs(a))) if np.all(np.isfinite(a)) else float("inf")
                ok = (not r["diverged"]) and np.all(np.isfinite(r["y"])) and amax <= a_max

                fn = os.path.join(OUT, f"{fc_id}_{cls}_m{m:.6f}.npz")
                np.savez_compressed(fn, t=r["t"], y=r["y"])
                index[key] = {"path": os.path.relpath(fn, ROOT).replace(os.sep, "/"), "reused": False,
                              "max_abs_alpha_deg": amax, "valid": bool(ok),
                              "diverged": bool(r["diverged"])}
                if not ok:
                    excluded.append({**index[key], "key": key})
                generated += 1

        print(f"  {fc_id}: done ({generated} generated, {reused} reused so far)")

    runtime = time.perf_counter() - t0
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                     text=True).strip()
    files = sorted(f for f in os.listdir(OUT) if f.endswith(".npz"))
    total = sum(os.path.getsize(os.path.join(OUT, f)) for f in files)

    with open(os.path.join(ROOT, "data", "manifests", "DS-0002.yaml"), "w",
              encoding="utf-8") as fh:
        yaml.safe_dump({
            "dataset_id": "DS-0002",
            "name": "exp0011-fault-magnitude-grid",
            "layer": "derived",
            "source": "simulation",
            "generation_date": datetime.now(timezone.utc).date().isoformat(),
            "generation_method": "experiments/EXP-0011/generate_magnitudes.py",
            "software_version": "aura 0.4.0",
            "git_commit": commit,
            "configuration": "experiments/EXP-0011/config/exp0011.yaml",
            "configuration_sha256": sha256_file(CFG11P),
            "random_seed_base": None,
            "n_runs": len(files),
            "parent_dataset": "DS-0001",
            "checksum_manifest": "data/manifests/DS-0002.sha256",
            "units": "SI; angles in radians; altitude in metres positive up",
            "sampling_rate_hz": float(cfg2["sensors"]["sample_rate_hz"]),
            "frozen": False,
            "license": "internal",
            "total_bytes": int(total),
            "n_excluded_templates": len(excluded),
            "description": (
                "Fault-magnitude grid for EXP-0011: 4 flight conditions x 13 "
                "magnitude-varying fault classes x 9 magnitudes, on GFW-1. The m=1.0 "
                "slice is reused from DS-0001 rather than regenerated. Deterministic and "
                "fully regenerable; not published in Git per the data policy."),
        }, fh, sort_keys=False)

    with open(os.path.join(ROOT, "data", "manifests", "DS-0002.sha256"), "w",
              encoding="utf-8") as fh:
        for f in files:
            fh.write(f"{sha256_file(os.path.join(OUT, f))}  {f}\n")

    with open(os.path.join(ROOT, "results", "validation", "EXP-0011",
                           "template_index.json"), "w", encoding="utf-8") as fh:
        json.dump({"index": index, "excluded": excluded,
                   "n_generated": generated, "n_reused": reused,
                   "runtime_seconds": runtime}, fh, indent=2)

    print(f"\ngenerated {generated}, reused {reused}, excluded {len(excluded)} templates "
          f"in {runtime:.0f} s; {total/1024/1024:.1f} MiB (git-ignored)")
    if excluded:
        print("EXCLUDED (pre-declared rule: diverged or |alpha| > 25 deg):")
        for e in excluded[:20]:
            print(f"   {e['key']}  max|alpha|={e['max_abs_alpha_deg']:.1f} deg")
    return 0


if __name__ == "__main__":
    os.makedirs(os.path.join(ROOT, "results", "validation", "EXP-0011"), exist_ok=True)
    raise SystemExit(main())
