"""
EXP-0012 trajectory generation: the unseen faults.

Generates only the unseen-fault trajectories (DS-0003). The KNOWN-fault hypothesis
library is reused unchanged from DS-0001 and DS-0002 -- nothing about it is regenerated.

Applies the same envelope-validity rule as EXP-0011 (divergence or alpha > 25 deg), so
that the FAIL-0001 mistake -- analysing trajectories where the aircraft has departed --
is not repeated.
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
from faults.unseen_faults import UnseenFault, UNSEEN_IDS        # noqa: E402
from simulation.simulate import simulate                        # noqa: E402

CFG2P = os.path.join(ROOT, "experiments", "EXP-0002", "config", "exp0002.yaml")
CFG12P = os.path.join(ROOT, "experiments", "EXP-0012", "config", "exp0012.yaml")
OUT = os.path.join(ROOT, "data", "derived", "EXP-0012")
RES = os.path.join(ROOT, "results", "validation", "EXP-0012")


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for c in iter(lambda: fh.read(65536), b""):
            h.update(c)
    return h.hexdigest()


def main():
    t0 = time.perf_counter()
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(RES, exist_ok=True)
    cfg2 = yaml.safe_load(open(CFG2P, encoding="utf-8"))
    cfg = yaml.safe_load(open(CFG12P, encoding="utf-8"))
    model = GFW1(cfg2)

    a_max = float(cfg["template_validity"]["exclude_if_max_alpha_deg_above"])
    fcmeta = {f["id"]: f for f in cfg2["flight_conditions"]}
    scales = [float(s) for s in cfg["magnitude_scales"]]

    index, excluded, n = {}, [], 0
    for fc_id in cfg["flight_conditions"]:
        fc = fcmeta[fc_id]
        x0, u0, info = trim(model, fc["airspeed_mps"], fc["altitude_m"])
        for uf_id in UNSEEN_IDS:
            for s in scales:
                uf = UnseenFault(uf_id, cfg2, cfg, scale=s)
                try:
                    r = simulate(model, cfg2, x0, u0, info, Fault("F0", None, cfg2),
                                 unseen=uf)
                finally:
                    uf.restore(model)      # never leave the plant mutated
                a = np.degrees(r["y"][:, CHANNELS.index("alpha")])
                amax = float(np.max(np.abs(a))) if np.all(np.isfinite(a)) else float("inf")
                ok = (not r["diverged"]) and np.all(np.isfinite(r["y"])) and amax <= a_max

                fn = os.path.join(OUT, f"{fc_id}_{uf_id}_m{s:.6f}.npz")
                np.savez_compressed(fn, t=r["t"], y=r["y"])
                key = f"{fc_id}|{uf_id}|{s:.8f}"
                index[key] = {"path": os.path.relpath(fn, ROOT).replace(os.sep, "/"),
                              "max_abs_alpha_deg": amax, "valid": bool(ok),
                              "diverged": bool(r["diverged"]),
                              "category": cfg["unseen_faults"][uf_id]["category"],
                              "predicted_position": cfg["unseen_faults"][uf_id]["predicted_position"]}
                if not ok:
                    excluded.append({**index[key], "key": key})
                n += 1
        print(f"  {fc_id}: {n} generated so far")

    # sanity: the plant must be back to its configured values
    for uf_id in UNSEEN_IDS:
        p = cfg["unseen_faults"][uf_id]
        if p.get("plant"):
            for c in p["coefficients"]:
                assert abs(model.p[c] - float(cfg2["aircraft"][c])) < 1e-15, \
                    f"plant coefficient {c} was not restored"
    print("  plant coefficients verified restored to configured values")

    runtime = time.perf_counter() - t0
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    files = sorted(f for f in os.listdir(OUT) if f.endswith(".npz"))
    total = sum(os.path.getsize(os.path.join(OUT, f)) for f in files)

    with open(os.path.join(ROOT, "data", "manifests", "DS-0003.yaml"), "w",
              encoding="utf-8") as fh:
        yaml.safe_dump({
            "dataset_id": "DS-0003",
            "name": "exp0012-unseen-fault-trajectories",
            "layer": "derived",
            "source": "simulation",
            "generation_date": datetime.now(timezone.utc).date().isoformat(),
            "generation_method": "experiments/EXP-0012/generate_unseen.py",
            "software_version": "aura 0.6.0",
            "git_commit": commit,
            "configuration": "experiments/EXP-0012/config/exp0012.yaml",
            "configuration_sha256": sha256_file(CFG12P),
            "random_seed_base": None,
            "n_runs": len(files),
            "parent_dataset": None,
            "checksum_manifest": "data/manifests/DS-0003.sha256",
            "units": "SI; angles in radians; altitude in metres positive up",
            "sampling_rate_hz": float(cfg2["sensors"]["sample_rate_hz"]),
            "frozen": False,
            "license": "internal",
            "total_bytes": int(total),
            "n_excluded": len(excluded),
            "description": (
                "Unseen-fault trajectories for EXP-0012: 4 flight conditions x 6 unseen "
                "fault mechanisms x 3 magnitudes on GFW-1. These faults are deliberately "
                "ABSENT from the diagnostic hypothesis library. Deterministic and fully "
                "regenerable; not published in Git per the data policy."),
        }, fh, sort_keys=False)

    with open(os.path.join(ROOT, "data", "manifests", "DS-0003.sha256"), "w",
              encoding="utf-8") as fh:
        for f in files:
            fh.write(f"{sha256_file(os.path.join(OUT, f))}  {f}\n")

    with open(os.path.join(RES, "unseen_index.json"), "w", encoding="utf-8") as fh:
        json.dump({"index": index, "excluded": excluded, "n_generated": n,
                   "runtime_seconds": runtime}, fh, indent=2)

    print(f"\ngenerated {n} unseen-fault trajectories in {runtime:.0f} s; "
          f"{total/1024/1024:.1f} MiB (git-ignored); {len(excluded)} excluded")
    for e in excluded:
        print(f"   EXCLUDED {e['key']}  max|alpha|={e['max_abs_alpha_deg']:.1f} deg "
              f"diverged={e['diverged']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
