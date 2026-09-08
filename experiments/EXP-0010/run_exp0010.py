"""
EXP-0010 runner — measurement uncertainty and practical diagnosability.

Executes the pre-registered design in experiment_spec.md. Reuses the EXP-0002
deterministic trajectories (DS-0001) without re-simulation, except for validity
attack V-D which needs new fault magnitudes.

Nothing here selects a metric, threshold, noise level or replication count: all come
from configuration.
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

from analysis.practical_diagnosability import (                 # noqa: E402
    sigma_vector, load_window, gram, squared_deflection, p_disc, p_iso_mc,
    p_detect_mc, p_iso_direct, practical_ambiguity_pairs,
)

CFG2P = os.path.join(ROOT, "experiments", "EXP-0002", "config", "exp0002.yaml")
CFG10P = os.path.join(ROOT, "experiments", "EXP-0010", "config", "exp0010.yaml")
DAT = os.path.join(ROOT, "data", "derived", "EXP-0002")
RES2 = os.path.join(ROOT, "results", "validation", "EXP-0002")
RES = os.path.join(ROOT, "results", "validation", "EXP-0010")


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for c in iter(lambda: fh.read(65536), b""):
            h.update(c)
    return h.hexdigest()


def git_info():
    def run(a):
        try:
            return subprocess.check_output(a, cwd=ROOT, text=True,
                                           stderr=subprocess.DEVNULL).strip()
        except Exception:
            return "unknown"
    return run(["git", "rev-parse", "HEAD"]), run(["git", "status", "--porcelain"]) != ""


def cell_seed(base, fc, win, eta, tag=""):
    """Deterministic per-cell seed derived from the base seed and the cell identity."""
    s = f"{base}|{fc}|{win}|{eta}|{tag}"
    return int(hashlib.sha256(s.encode()).hexdigest()[:8], 16)


def load_condition(fc, ids):
    t, traj = None, {}
    for f in ids:
        z = np.load(os.path.join(DAT, f"{fc}_{f}.npz"))
        traj[f] = z["y"]
        if t is None:
            t = z["t"]
    return t, traj


def interp_crossing(etas, vals, level):
    """First eta at which vals (decreasing in eta) crosses below `level`, log-interpolated.

    Returns None if the curve never reaches the level within the swept range — reported
    as such rather than extrapolated.
    """
    e = np.asarray(etas, float)
    v = np.asarray(vals, float)
    for k in range(len(v) - 1):
        if v[k] >= level > v[k + 1]:
            f = (v[k] - level) / (v[k] - v[k + 1])
            return float(np.exp(np.log(e[k]) + f * (np.log(e[k + 1]) - np.log(e[k]))))
    return None


def main():
    t_start = time.perf_counter()
    os.makedirs(RES, exist_ok=True)
    cfg2 = yaml.safe_load(open(CFG2P, encoding="utf-8"))
    cfg = yaml.safe_load(open(CFG10P, encoding="utf-8"))
    res2 = json.load(open(os.path.join(RES2, "exp0002_results.json"), encoding="utf-8"))

    ids = res2["fault_ids"]
    sigma = sigma_vector(cfg2)
    onset = float(cfg2["simulation"]["fault_onset"])
    conds = cfg["flight_conditions"]
    etas = [float(e) for e in cfg["noise"]["eta_levels"]]
    wins = [float(w) for w in cfg["observation_windows"]]
    n_mc = int(cfg["monte_carlo"]["replications"])
    seed_base = int(cfg["noise"]["seed_base"])
    thr = float(cfg["metrics"]["practical_ambiguity_threshold"])
    commit, dirty = git_info()

    print(f"EXP-0010  commit={commit[:8]} dirty={dirty} "
          f"cfg={sha256_file(CFG10P)[:12]}  (reusing DS-0001, no re-simulation)")

    # ---------------------------------------------- Gram matrices per (cond, window)
    grams, Dsq = {}, {}
    for fc in conds:
        t, traj = load_condition(fc, ids)
        for w in wins:
            W = load_window(traj, t, sigma, onset, w)
            M = gram(W)
            grams[(fc, w)] = M
            Dsq[(fc, w)] = squared_deflection(M)
    n_samp = {w: int(round(w * 100)) + 1 for w in wins}
    print(f"  built {len(grams)} Gram matrices; window sample counts "
          f"{ {w: n_samp[w] for w in wins} }")

    # ------------------------------------------------------------- primary grid
    print("\nPRIMARY GRID: P_iso (18-way, Bayes-optimal, KNOWN templates -> UPPER BOUND)")
    P_iso = {}
    per_fault = {}
    det = {}
    for fc in conds:
        for w in wins:
            M = grams[(fc, w)]
            for eta in etas:
                rng = np.random.default_rng(cell_seed(seed_base, fc, w, eta))
                p, pf = p_iso_mc(M, eta, n_mc, rng)
                P_iso[(fc, w, eta)] = p
                per_fault[(fc, w, eta)] = pf
        row = "  ".join(f"{P_iso[(fc, 18.0, e)]:.3f}" for e in etas)
        print(f"  {fc} full window, eta={etas}: {row}")

    for fc in conds:
        for eta in etas:
            rng = np.random.default_rng(cell_seed(seed_base, fc, 18.0, eta, "det"))
            det[(fc, eta)] = p_detect_mc(grams[(fc, 18.0)], eta, n_mc, rng)

    # ----------------------------------- practical diagnosability limits per condition
    print("\nPRACTICAL DIAGNOSABILITY LIMIT (eta at which P_iso crosses a level)")
    limits = {}
    for fc in conds:
        for w in wins:
            v = [P_iso[(fc, w, e)] for e in etas]
            limits[(fc, w)] = {
                "eta_at_P95": interp_crossing(etas, v, 0.95),
                "eta_at_P50": interp_crossing(etas, v, 0.50),
                "P_iso_at_eta1": v[0],
            }
        L = limits[(fc, 18.0)]
        print(f"  {fc} (18 s window): P_iso(eta=1)={L['P_iso_at_eta1']:.4f}  "
              f"eta@P=0.95: {L['eta_at_P95']}  eta@P=0.50: {L['eta_at_P50']}")

    # ------------------------------------------------- five-member ambiguity group
    print("\nEXP-0002 FIVE-MEMBER AMBIGUITY GROUP UNDER NOISE")
    grp = cfg["analysis"]["ambiguity_group_exp0002"]
    group_analysis = {}
    for fc in conds:
        D = Dsq[(fc, 18.0)]
        rec = {}
        for eta in etas:
            P = p_disc(D, eta)
            amb = practical_ambiguity_pairs(ids, P, thr)
            members = sorted({x for a, b, _ in amb for x in (a, b)})
            in_grp = [p for p in amb if p[0] in grp and p[1] in grp]
            rec[str(eta)] = {
                "n_ambiguous_pairs": len(amb),
                "n_within_exp0002_group": len(in_grp),
                "members": members,
                "n_members": len(members),
                "top_pairs": amb[:8],
            }
        group_analysis[fc] = rec
        r = rec[str(etas[0])]
        print(f"  {fc}: at eta=1 -> {r['n_ambiguous_pairs']} practically ambiguous pairs "
              f"(P_disc<{thr}), {r['n_members']} faults involved")

    # ------------------------------------------- analytic prediction test (NOT refitted)
    print("\nANALYTIC PREDICTION TEST (F1_Vt / F2_Vt) -- prediction is fixed, not refitted")
    i1, i2 = ids.index("F1_Vt"), ids.index("F2_Vt")
    b = 10.0 * float(cfg2["sensors"]["sigma"]["Vt"])
    k = float(cfg2["faults"]["scale_factor"])
    sV = float(cfg2["sensors"]["sigma"]["Vt"])
    analytic = {}
    for fc in conds:
        V0 = float(res2["trim"][fc]["Vt"])
        N = n_samp[18.0]
        # Predicted deflection from the Vt channel alone, from the closed form
        d_pred = np.sqrt(N) * abs(b - (k - 1.0) * V0) / sV
        d_meas = float(np.sqrt(Dsq[(fc, 18.0)][i1, i2]))
        # eta at which the optimal binary test falls to P=0.95 (d'/2 = 1.6449)
        analytic[fc] = {
            "V0": V0,
            "d_pred_Vt_channel_only": float(d_pred),
            "d_measured_all_channels": d_meas,
            "eta95_predicted": float(d_pred / (2 * 1.6449)),
            "eta95_measured": float(d_meas / (2 * 1.6449)),
        }
        a = analytic[fc]
        print(f"  {fc} V0={V0:5.1f}: eta95 predicted {a['eta95_predicted']:8.1f}  "
              f"measured {a['eta95_measured']:8.1f}  ratio {a['eta95_measured']/a['eta95_predicted']:.3f}")
    pr = [analytic[fc]["eta95_predicted"] for fc in conds]
    me = [analytic[fc]["eta95_measured"] for fc in conds]
    analytic_r = float(np.corrcoef(pr, me)[0, 1])
    print(f"  Pearson(predicted, measured eta95) = {analytic_r:.4f}")

    # --------------------------------------------------------- validity attacks
    print("\nV-A SEED SENSITIVITY")
    alt = int(cfg["validity_attacks"]["alt_seed_base"])
    seed_check = {}
    for fc in conds:
        v1 = P_iso[(fc, 18.0, 50.0)]
        rng = np.random.default_rng(cell_seed(alt, fc, 18.0, 50.0))
        v2, _ = p_iso_mc(grams[(fc, 18.0)], 50.0, n_mc, rng)
        seed_check[fc] = {"base": v1, "alt": v2, "abs_diff": abs(v1 - v2)}
        print(f"  {fc}: base {v1:.4f}  alt-seed {v2:.4f}  diff {abs(v1-v2):.4f}")

    print("\nV-B NOISE DISTRIBUTION (direct full-dimensional simulation)")
    ac = cfg["validity_attacks"]["attack_cells"]
    ntr = int(cfg["validity_attacks"]["direct_sim_trials"])
    dist_check = {}
    for fc in ac["conditions"]:
        t, traj = load_condition(fc, ids)
        for w in ac["windows"]:
            W = load_window(traj, t, sigma, onset, float(w))
            for eta in ac["eta"]:
                rec = {}
                for dist in ("gaussian", "student_t", "ar1"):
                    rng = np.random.default_rng(cell_seed(seed_base, fc, w, eta, dist))
                    p, _ = p_iso_direct(
                        W, float(eta), max(ntr // 18, 60), rng, W.shape[1], noise=dist,
                        df=int(cfg["validity_attacks"]["t_distribution_df"]),
                        rho=float(cfg["validity_attacks"]["ar1_rho"]))
                    rec[dist] = p
                rec["gram_reference"] = P_iso[(fc, float(w), float(eta))]
                dist_check[f"{fc}|w={w}|eta={eta}"] = rec
                print(f"  {fc} w={w}s eta={eta}: gauss {rec['gaussian']:.3f}  "
                      f"t4 {rec['student_t']:.3f}  ar1 {rec['ar1']:.3f}  "
                      f"(gram {rec['gram_reference']:.3f})")

    print("\nV-D FAULT MAGNITUDE (requires re-simulation)")
    from aircraft.gfw1 import GFW1                               # noqa: E402
    from aircraft.trim import trim                               # noqa: E402
    from faults.faults import build_fault_set                    # noqa: E402
    from simulation.simulate import simulate                     # noqa: E402
    model = GFW1(cfg2)
    fcmeta = {f["id"]: f for f in cfg2["flight_conditions"]}
    mag_check = {}
    for ms in cfg["validity_attacks"]["magnitude_scales"]:
        rec = {}
        for fc in conds:
            x0, u0, info = trim(model, fcmeta[fc]["airspeed_mps"], fcmeta[fc]["altitude_m"])
            tr = {}
            for f in build_fault_set(cfg2, float(ms)):
                r = simulate(model, cfg2, x0, u0, info, f)
                tr[f.fault_id] = r["y"]
                tt = r["t"]
            Wm = load_window(tr, tt, sigma, onset, 18.0)
            Mm = gram(Wm)
            v = []
            for eta in etas:
                rng = np.random.default_rng(cell_seed(seed_base, fc, 18.0, eta, f"m{ms}"))
                p, _ = p_iso_mc(Mm, eta, n_mc, rng)
                v.append(p)
            rec[fc] = {"P_iso_by_eta": v,
                       "eta_at_P95": interp_crossing(etas, v, 0.95),
                       "eta_at_P50": interp_crossing(etas, v, 0.50)}
        mag_check[str(ms)] = rec
        print(f"  magnitude x{ms}: eta@P=0.95 " +
              "  ".join(f"{fc}:{rec[fc]['eta_at_P95']}" for fc in conds))

    # ------------------------------------------------------------------ outputs
    runtime = time.perf_counter() - t_start
    payload = {
        "experiment_id": "EXP-0010",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": commit, "git_dirty": dirty,
        "config": "experiments/EXP-0010/config/exp0010.yaml",
        "config_sha256": sha256_file(CFG10P),
        "source_dataset": "DS-0001",
        "environment": {"python": platform.python_version(), "numpy": np.__version__,
                        "platform": platform.platform()},
        "fault_ids": ids,
        "flight_conditions": conds,
        "eta_levels": etas,
        "observation_windows": wins,
        "monte_carlo_replications": n_mc,
        "classifier": "Bayes-optimal 18-way, KNOWN templates, known Gaussian noise -- UPPER BOUND",
        "P_iso": {f"{fc}|{w}|{e}": P_iso[(fc, w, e)] for fc in conds for w in wins for e in etas},
        "per_fault_P_iso": {f"{fc}|{w}|{e}": per_fault[(fc, w, e)].tolist()
                            for fc in conds for w in wins for e in etas},
        "detection": {f"{fc}|{e}": {"P_det": det[(fc, e)]["P_det"],
                                    "P_FA": det[(fc, e)]["P_FA"]}
                      for fc in conds for e in etas},
        "diagnosability_limits": {f"{fc}|{w}": limits[(fc, w)] for fc in conds for w in wins},
        "ambiguity_group_under_noise": group_analysis,
        "analytic_prediction": analytic,
        "analytic_prediction_pearson_r": analytic_r,
        "validity": {"seed": seed_check, "noise_distribution": dist_check,
                     "magnitude": mag_check},
        "runtime_seconds": runtime,
    }
    with open(os.path.join(RES, "exp0010_results.json"), "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, default=float)

    # compact machine-readable surface for figures / reuse
    arr = np.zeros((len(conds), len(wins), len(etas)))
    for a, fc in enumerate(conds):
        for b_, w in enumerate(wins):
            for c, e in enumerate(etas):
                arr[a, b_, c] = P_iso[(fc, w, e)]
    np.savez_compressed(os.path.join(RES, "P_iso_surface.npz"), P_iso=arr,
                        conditions=np.array(conds), windows=np.array(wins),
                        etas=np.array(etas))
    print(f"\nDone in {runtime:.1f} s. No new bulk data (EXP-0002 trajectories reused).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
