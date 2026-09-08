"""
EXP-0002 full experiment runner.

Executes the pre-registered design in experiment_spec.md:
  4 flight conditions x 18 faults = 72 primary runs,
  plus the four required sensitivity sweeps (S-A, S-B, S-C, S-D) and the
  determinism check (S-E).

Writes:
  results/validation/EXP-0002/   summaries, matrices, sensitivity (committed)
  data/derived/EXP-0002/         trajectories (.npz, git-ignored, regenerable)
  data/manifests/DS-0001.yaml    provenance for the trajectory set

No metric or threshold is chosen here; everything comes from configuration.
"""

from __future__ import annotations

import hashlib
import json
import os
import platform
import subprocess
import sys
import time
from datetime import datetime, timezone

import numpy as np
import yaml

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)

from aircraft.gfw1 import GFW1                                  # noqa: E402
from aircraft.trim import trim                                  # noqa: E402
from faults.faults import build_fault_set                       # noqa: E402
from simulation.simulate import simulate                        # noqa: E402
from analysis.isolability import (                              # noqa: E402
    distance_matrix, binary_matrix, summarise, compare_conditions,
    matrix_to_text, upper_triangle, spearman,
)

CFG_PATH = os.path.join(ROOT, "experiments", "EXP-0002", "config", "exp0002.yaml")
RES_DIR = os.path.join(ROOT, "results", "validation", "EXP-0002")
DAT_DIR = os.path.join(ROOT, "data", "derived", "EXP-0002")


def git_info():
    def run(args):
        try:
            return subprocess.check_output(args, cwd=ROOT, text=True,
                                           stderr=subprocess.DEVNULL).strip()
        except Exception:                                        # pragma: no cover
            return "unknown"
    commit = run(["git", "rev-parse", "HEAD"])
    dirty = run(["git", "status", "--porcelain"]) != ""
    return commit, dirty


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def run_grid(model, cfg, trims, magnitude_scale=1.0, dt=None, duration=None,
             save=False, tag=""):
    """Run every fault at every flight condition. Returns {fc_id: {fault_id: run}}."""
    out = {}
    for fc in cfg["flight_conditions"]:
        fc_id = fc["id"]
        x0, u0, info = trims[fc_id]
        runs = {}
        for f in build_fault_set(cfg, magnitude_scale, duration):
            r = simulate(model, cfg, x0, u0, info, f, dt=dt, duration=duration)
            if r["diverged"]:
                print(f"   ! DIVERGED {fc_id}/{f.fault_id} -- recorded as INVALID")
            runs[f.fault_id] = r
            if save:
                np.savez_compressed(
                    os.path.join(DAT_DIR, f"{fc_id}_{f.fault_id}.npz"),
                    t=r["t"], y=r["y"], u=r["u"], x=r["x"])
        out[fc_id] = runs
    return out


def check_validity(model, cfg, trims):
    """Validity gate (added after FAIL-0001).

    Trim convergence proves an equilibrium exists; it does not prove the closed loop
    can hold it through the manoeuvre. FC-4 trimmed to 2e-15 and then stalled. Every
    condition's NOMINAL run must stay inside the declared envelope or the condition is
    marked INVALID and excluded from the determination.
    """
    from aircraft.gfw1 import CHANNELS
    V = cfg["validity"]
    out = {}
    for fc_id, (x0, u0, info) in trims.items():
        r = simulate(model, cfg, x0, u0, info, build_fault_set(cfg)[0])   # F0
        y = r["y"]
        a = np.degrees(y[:, CHANNELS.index("alpha")])
        th = np.degrees(y[:, CHANNELS.index("theta")])
        vt = y[:, CHANNELS.index("Vt")]
        hh = y[:, CHANNELS.index("h")]
        met = {
            "alpha_trim_deg": info["alpha_deg"],
            "alpha_max_deg": float(a.max()),
            "dtheta_max_deg": float(np.max(np.abs(th - info["alpha_deg"]))),
            "dV_max_mps": float(np.max(np.abs(vt - info["Vt"]))),
            "dh_max_m": float(np.max(np.abs(hh - info["altitude_m"]))),
            "diverged": bool(r["diverged"]),
        }
        met["valid"] = bool(
            not met["diverged"]
            and met["alpha_max_deg"] < float(V["alpha_max_deg"])
            and met["dtheta_max_deg"] < float(V["dtheta_max_deg"])
            and met["dV_max_mps"] < float(V["dV_max_mps"])
            and met["dh_max_m"] < float(V["dh_max_m"]))
        met["status"] = "VALID" if met["valid"] else "INVALID"
        out[fc_id] = met
    return out


def main():
    t_start = time.perf_counter()
    os.makedirs(RES_DIR, exist_ok=True)
    os.makedirs(DAT_DIR, exist_ok=True)

    with open(CFG_PATH, "r", encoding="utf-8") as fh:
        cfg = yaml.safe_load(fh)
    cfg_sha = sha256_file(CFG_PATH)
    commit, dirty = git_info()
    model = GFW1(cfg)

    tau = float(cfg["analysis"]["threshold_primary"])
    tol = float(cfg["analysis"]["numerically_identical_tol"])

    print(f"EXP-0002  commit={commit[:8]} dirty={dirty} config_sha={cfg_sha[:12]}")

    # ------------------------------------------------------------------ trim
    trims, trim_report = {}, {}
    for fc in cfg["flight_conditions"]:
        x0, u0, info = trim(model, fc["airspeed_mps"], fc["altitude_m"])
        trims[fc["id"]] = (x0, u0, info)
        trim_report[fc["id"]] = {**info, "rationale": fc["rationale"]}
        print(f"  trim {fc['id']}: alpha={info['alpha_deg']:6.2f} deg  "
              f"qbar={info['qbar_Pa']:7.1f} Pa  de={info['de_deg']:6.2f} deg")

    # ------------------------------------------------------- validity gate
    print("\nVALIDITY GATE (nominal run must hold trim through the manoeuvre)")
    valid = check_validity(model, cfg, trims)
    for fc_id, v in valid.items():
        print(f"  {fc_id}: {v['status']:8s} a_trim={v['alpha_trim_deg']:6.2f} "
              f"a_max={v['alpha_max_deg']:7.2f}  |dth|={v['dtheta_max_deg']:6.2f}  "
              f"|dV|={v['dV_max_mps']:6.2f}  |dh|={v['dh_max_m']:7.1f}")
    valid_ids = [k for k, v in valid.items() if v["valid"]]
    invalid_ids = [k for k, v in valid.items() if not v["valid"]]
    if invalid_ids:
        print(f"  EXCLUDED from the determination: {invalid_ids} (see FAIL-0001)")

    # -------------------------------------------------------------- primary
    print(f"\nPRIMARY GRID ({len(cfg['flight_conditions'])} conditions x 18 faults)")
    grid = run_grid(model, cfg, trims, save=True)

    D_by_cond, summaries, ids = {}, {}, None
    for fc_id, runs in grid.items():
        ids, D = distance_matrix(runs, cfg)
        D_by_cond[fc_id] = D
        summaries[fc_id] = summarise(ids, D, tau, tol)
        summaries[fc_id]["validity"] = valid[fc_id]["status"]
        s = summaries[fc_id]
        print(f"  {fc_id} [{valid[fc_id]['status']}]: {s['n_distinguishable']}/{s['n_pairs']} "
              f"distinguishable ({s['frac_distinguishable']*100:.1f}%)  "
              f"d range [{s['min_distance']:.3g}, {s['max_distance']:.3g}]")

    # The determination uses VALID conditions only. The invalid condition is still
    # computed and reported -- it is evidence about the failure, not deleted.
    D_valid = {k: D_by_cond[k] for k in valid_ids}
    cross = compare_conditions(ids, D_valid, tau)
    cross_all = compare_conditions(ids, D_by_cond, tau)
    print("\n  cross-condition (VALID only):")
    for k, v in cross["pairwise"].items():
        print(f"    {k:15s} rho={v['spearman_rho']:.4f}  flips={v['binary_flips']:3d}")

    # ------------------------------------------------ S-B threshold sweep
    print("\nS-B THRESHOLD SWEEP")
    sweep = {}
    for t_ in cfg["analysis"]["threshold_sweep"]:
        sweep[str(t_)] = {}
        for fc_id, D in D_by_cond.items():
            s = summarise(ids, D, float(t_), tol)
            sweep[str(t_)][fc_id] = {
                "n_distinguishable": s["n_distinguishable"],
                "frac_distinguishable": s["frac_distinguishable"],
                "is_fully_diagonal": s["is_fully_diagonal"],
                "is_fully_dense": s["is_fully_dense"],
            }
        cr = compare_conditions(ids, D_valid, float(t_))
        sweep[str(t_)]["max_binary_flips_valid"] = max(
            v["binary_flips"] for v in cr["pairwise"].values())
        sweep[str(t_)]["min_spearman_valid"] = min(
            v["spearman_rho"] for v in cr["pairwise"].values())
        row = "  ".join(f"{fc}:{sweep[str(t_)][fc]['n_distinguishable']:3d}"
                        for fc in D_by_cond)
        print(f"  tau={t_:<6g} {row}   valid_flips={sweep[str(t_)]['max_binary_flips_valid']}"
              f"  min_rho={sweep[str(t_)]['min_spearman_valid']:.4f}")

    # ------------------------------------------------------ S-A dt sweep
    print("\nS-A INTEGRATION STEP SWEEP")
    dt_sens = {}
    base_vec = {fc: upper_triangle(D_by_cond[fc]) for fc in D_by_cond}
    base_dt = float(cfg["simulation"]["dt"])
    for dtv in cfg["sensitivity"]["dt_sweep"]:
        g = grid if abs(float(dtv) - base_dt) < 1e-15 else run_grid(model, cfg, trims, dt=float(dtv))
        rec = {}
        for fc_id, runs in g.items():
            _, D = distance_matrix(runs, cfg)
            s = summarise(ids, D, tau, tol)
            v = upper_triangle(D)
            rec[fc_id] = {
                "n_distinguishable": s["n_distinguishable"],
                "max_rel_diff_vs_base": float(
                    np.max(np.abs(v - base_vec[fc_id]) / (base_vec[fc_id] + 1e-12))),
                "spearman_vs_base": spearman(v, base_vec[fc_id]),
            }
        dt_sens[str(dtv)] = rec
        print(f"  dt={dtv:<7g} " + "  ".join(
            f"{fc}:{rec[fc]['n_distinguishable']:3d}(rho={rec[fc]['spearman_vs_base']:.4f})"
            for fc in rec))

    # ----------------------------------------------- S-C magnitude sweep
    print("\nS-C FAULT MAGNITUDE SWEEP")
    mag_sens = {}
    for ms in cfg["sensitivity"]["magnitude_scale_sweep"]:
        g = grid if abs(float(ms) - 1.0) < 1e-15 else run_grid(
            model, cfg, trims, magnitude_scale=float(ms))
        Dm = {}
        rec = {}
        for fc_id, runs in g.items():
            _, D = distance_matrix(runs, cfg)
            Dm[fc_id] = D
            s = summarise(ids, D, tau, tol)
            rec[fc_id] = {"n_distinguishable": s["n_distinguishable"],
                          "frac_distinguishable": s["frac_distinguishable"],
                          "is_fully_diagonal": s["is_fully_diagonal"],
                          "is_fully_dense": s["is_fully_dense"]}
        cr = compare_conditions(ids, {k: Dm[k] for k in valid_ids}, tau)
        rec["max_binary_flips"] = max(v["binary_flips"] for v in cr["pairwise"].values())
        rec["min_spearman_between_conditions"] = min(
            v["spearman_rho"] for v in cr["pairwise"].values())
        mag_sens[str(ms)] = rec
        print(f"  scale={ms:<5g} " + "  ".join(
            f"{fc}:{rec[fc]['n_distinguishable']:3d}" for fc in D_by_cond)
            + f"   valid_flips={rec['max_binary_flips']}"
            + f"  min_rho={rec['min_spearman_between_conditions']:.4f}")

    # ------------------------------------------------ S-D duration sweep
    print("\nS-D DURATION SWEEP")
    dur_sens = {}
    base_dur = float(cfg["simulation"]["duration"])
    for dur in cfg["sensitivity"]["duration_sweep"]:
        g = grid if abs(float(dur) - base_dur) < 1e-15 else run_grid(
            model, cfg, trims, duration=float(dur))
        Dd, rec = {}, {}
        for fc_id, runs in g.items():
            _, D = distance_matrix(runs, cfg)
            Dd[fc_id] = D
            s = summarise(ids, D, tau, tol)
            rec[fc_id] = {"n_distinguishable": s["n_distinguishable"]}
        cr = compare_conditions(ids, {k: Dd[k] for k in valid_ids}, tau)
        rec["max_binary_flips"] = max(v["binary_flips"] for v in cr["pairwise"].values())
        dur_sens[str(dur)] = rec
        print(f"  T={dur:<5g}s " + "  ".join(
            f"{fc}:{rec[fc]['n_distinguishable']:3d}" for fc in D_by_cond)
            + f"   valid_flips={rec['max_binary_flips']}")

    # ------------------------------------------------------ S-E determinism
    print("\nS-E DETERMINISM")
    g2 = run_grid(model, cfg, trims)
    identical = all(
        hashlib.sha256(grid[fc][fid]["y"].tobytes()).hexdigest()
        == hashlib.sha256(g2[fc][fid]["y"].tobytes()).hexdigest()
        for fc in grid for fid in grid[fc])
    n_checked = sum(len(v) for v in grid.values())
    print(f"  all {n_checked} runs bitwise reproducible: {identical}")

    # ------------------------------------------------------------- outputs
    runtime = time.perf_counter() - t_start

    for fc_id, D in D_by_cond.items():
        np.savetxt(os.path.join(RES_DIR, f"distance_matrix_{fc_id}.csv"), D,
                   delimiter=",", fmt="%.9e",
                   header=",".join(ids), comments="")
        with open(os.path.join(RES_DIR, f"binary_matrix_{fc_id}.txt"), "w",
                  encoding="utf-8") as fh:
            fh.write(f"EXP-0002 response-based distinguishability -- {fc_id}\n")
            fh.write(f"tau = {tau} (multiples of per-sample per-channel RMS sensor noise)\n\n")
            fh.write(matrix_to_text(ids, D, tau) + "\n")

    payload = {
        "experiment_id": "EXP-0002",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": commit,
        "git_dirty": dirty,
        "config": "experiments/EXP-0002/config/exp0002.yaml",
        "config_sha256": cfg_sha,
        "environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "platform": platform.platform(),
        },
        "fault_ids": ids,
        "threshold_primary": tau,
        "trim": trim_report,
        "validity_gate": valid,
        "valid_conditions": valid_ids,
        "invalid_conditions": invalid_ids,
        "summaries": summaries,
        "cross_condition": cross,
        "cross_condition_including_invalid": cross_all,
        "threshold_sweep": sweep,
        "sensitivity_dt": dt_sens,
        "sensitivity_magnitude": mag_sens,
        "sensitivity_duration": dur_sens,
        "determinism_bitwise_reproducible": bool(identical),
        "runtime_seconds": runtime,
    }
    with open(os.path.join(RES_DIR, "exp0002_results.json"), "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, default=float)

    # dataset manifest for the (git-ignored, regenerable) trajectory set
    files = sorted(f for f in os.listdir(DAT_DIR) if f.endswith(".npz"))
    total = sum(os.path.getsize(os.path.join(DAT_DIR, f)) for f in files)
    checks = {f: sha256_file(os.path.join(DAT_DIR, f)) for f in files}
    with open(os.path.join(ROOT, "data", "manifests", "DS-0001.yaml"), "w",
              encoding="utf-8") as fh:
        yaml.safe_dump({
            "dataset_id": "DS-0001",
            "name": "exp0002-response-trajectories",
            "layer": "derived",
            "source": "simulation",
            "generation_date": datetime.now(timezone.utc).date().isoformat(),
            "generation_method": "experiments/EXP-0002/run_exp0002.py",
            "software_version": "aura 0.2.0",
            "git_commit": commit,
            "git_dirty": dirty,
            "configuration": "experiments/EXP-0002/config/exp0002.yaml",
            "configuration_sha256": cfg_sha,
            "random_seed_base": None,
            "n_runs": len(files),
            "parent_dataset": None,
            "checksum_manifest": "data/manifests/DS-0001.sha256",
            "units": "SI; angles in radians; altitude in metres positive up",
            "sampling_rate_hz": float(cfg["sensors"]["sample_rate_hz"]),
            "frozen": False,
            "license": "internal",
            "total_bytes": int(total),
            "description": (
                "Closed-loop measured-output trajectories for EXP-0002: 4 flight "
                "conditions x 18 fault modes on the GFW-1 generic fixed-wing model. "
                "Deterministic and fully regenerable from the configuration and code "
                "at the recorded commit -- not published in Git per the data policy."),
        }, fh, sort_keys=False)
    with open(os.path.join(ROOT, "data", "manifests", "DS-0001.sha256"), "w",
              encoding="utf-8") as fh:
        for f, h in checks.items():
            fh.write(f"{h}  {f}\n")

    print(f"\nDone in {runtime:.1f} s. Trajectories: {total/1024/1024:.1f} MiB in "
          f"{len(files)} files (git-ignored).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
