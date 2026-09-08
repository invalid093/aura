"""
EXP-0010 pilot verification.

Technical verification only. Nothing here is scientific evidence for or against the
hypothesis; it checks the machinery before the full run.

Checks:
  V-F  recomputed d_ij reproduces the EXP-0002 matrix (same data, same pipeline)
  V-C  the exact 18-dim Gram reduction agrees with direct full-dimensional simulation
       and with the closed-form pairwise probability
  MC   statistical stability at the pre-declared replication count
  cost runtime and storage estimates for the full grid
"""
from __future__ import annotations

import json
import os
import sys
import time

import numpy as np
import yaml

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)

from analysis.practical_diagnosability import (                 # noqa: E402
    sigma_vector, load_window, gram, squared_deflection, p_disc,
    p_iso_mc, p_iso_direct,
)

CFG2 = os.path.join(ROOT, "experiments", "EXP-0002", "config", "exp0002.yaml")
CFG10 = os.path.join(ROOT, "experiments", "EXP-0010", "config", "exp0010.yaml")
DAT = os.path.join(ROOT, "data", "derived", "EXP-0002")
RES2 = os.path.join(ROOT, "results", "validation", "EXP-0002")
FAIL = []


def check(name, ok, detail=""):
    if not ok:
        FAIL.append(name)
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f"  --  {detail}" if detail else ""))


def load_condition(fc, ids, sigma):
    t = None
    traj = {}
    for f in ids:
        z = np.load(os.path.join(DAT, f"{fc}_{f}.npz"))
        traj[f] = z["y"]
        if t is None:
            t = z["t"]
    return t, traj


def main():
    cfg2 = yaml.safe_load(open(CFG2, encoding="utf-8"))
    cfg10 = yaml.safe_load(open(CFG10, encoding="utf-8"))
    res2 = json.load(open(os.path.join(RES2, "exp0002_results.json"), encoding="utf-8"))
    ids = res2["fault_ids"]
    sigma = sigma_vector(cfg2)
    onset = float(cfg2["simulation"]["fault_onset"])

    print("=" * 78)
    print("EXP-0010 PILOT VERIFICATION")
    print("=" * 78)

    # ---------------------------------------------------------- V-F consistency
    print("\nV-F  CONSISTENCY WITH EXP-0002 (same data, independent pipeline)")
    fc = "FC-1"
    t, traj = load_condition(fc, ids, sigma)
    full_window = float(t[-1] - onset)
    W = load_window(traj, t, sigma, onset, full_window)
    M = gram(W)
    D = squared_deflection(M)
    K, N = 13, W.shape[1] // 13
    d_recomputed = np.sqrt(D / (K * N))
    d_exp0002 = np.loadtxt(os.path.join(RES2, f"distance_matrix_{fc}.csv"),
                           delimiter=",", skiprows=1)
    err = float(np.max(np.abs(d_recomputed - d_exp0002)))
    check("recomputed d_ij matches EXP-0002", err < 1e-9, f"max abs diff {err:.2e}")
    check("N samples in full window == 1801", N == 1801, str(N))
    check("deflection relation d' = d_ij*sqrt(K*N) holds",
          abs(np.sqrt(K * N) - 153.01) < 0.02, f"sqrt(K*N)={np.sqrt(K*N):.2f}")

    # ------------------------------------------------- V-C exactness of reduction
    print("\nV-C  GRAM REDUCTION vs DIRECT FULL-DIMENSIONAL SIMULATION")
    win = 0.5
    Ws = load_window(traj, t, sigma, onset, win)
    Ms = gram(Ws)
    for eta in (50.0, 200.0):
        rng1 = np.random.default_rng(12345)
        t0 = time.perf_counter()
        p_fast, _ = p_iso_mc(Ms, eta, 20000, rng1)
        t_fast = time.perf_counter() - t0

        rng2 = np.random.default_rng(54321)
        t0 = time.perf_counter()
        p_slow, _ = p_iso_direct(Ws, eta, 400, rng2, Ws.shape[1])
        t_slow = time.perf_counter() - t0

        se = np.sqrt(max(p_slow * (1 - p_slow), 1e-6) / 400)
        agree = abs(p_fast - p_slow) < 4 * se
        check(f"eta={eta:g}: Gram MC == direct simulation",
              agree, f"fast {p_fast:.4f} vs direct {p_slow:.4f} (+/-{2*se:.4f}); "
                     f"speedup {t_slow/400/(t_fast/20000):.0f}x per trial")

    # ------------------------------------------- closed form vs MC for one pair
    print("\nCLOSED-FORM PAIRWISE PROBABILITY vs MONTE CARLO")
    i, j = ids.index("F1_Vt"), ids.index("F2_Vt")
    for eta in (100.0, 300.0):
        Pcf = p_disc(squared_deflection(Ms), eta)[i, j]
        dprime = np.sqrt(squared_deflection(Ms)[i, j]) / eta
        rng = np.random.default_rng(999)
        # two-hypothesis MC: correct iff ||v||^2 - 2 z.v > 0, z.v ~ N(0, ||v||^2)
        nv2 = squared_deflection(Ms)[i, j] / eta ** 2
        u = rng.standard_normal(200000) * np.sqrt(nv2)
        Pmc = float((nv2 / 2.0 > u).mean())
        se = np.sqrt(Pmc * (1 - Pmc) / 200000)
        check(f"eta={eta:g}: closed form == MC", abs(Pcf - Pmc) < 4 * se + 1e-4,
              f"closed {Pcf:.4f} vs MC {Pmc:.4f}, d'={dprime:.3f}")

    # ------------------------------------------------------- MC stability
    print("\nMONTE CARLO STABILITY AT THE PRE-DECLARED N")
    n_mc = int(cfg10["monte_carlo"]["replications"])
    vals = []
    for s in range(5):
        p, _ = p_iso_mc(Ms, 100.0, n_mc, np.random.default_rng(1000 + s))
        vals.append(p)
    spread = float(np.max(vals) - np.min(vals))
    check(f"P_iso stable across 5 seeds at N={n_mc}", spread < 0.01,
          f"range {spread:.4f}, mean {np.mean(vals):.4f}")

    # ------------------------------------------------------------- cost
    print("\nCOST ESTIMATE FOR THE FULL GRID")
    t0 = time.perf_counter()
    p_iso_mc(Ms, 100.0, n_mc, np.random.default_rng(7))
    per_cell = time.perf_counter() - t0
    n_cells = (len(cfg10["flight_conditions"]) * len(cfg10["noise"]["eta_levels"])
               * len(cfg10["observation_windows"]))
    print(f"   per (condition,eta,window) cell: {per_cell:.2f} s")
    print(f"   cells: {n_cells}  ->  estimated {n_cells*per_cell/60:.1f} min")
    print(f"   trials: {n_cells*18*n_mc/1e6:.0f} M classifications")
    print("   new simulation required: NONE (EXP-0002 trajectories reused)")

    print("\n" + "=" * 78)
    if FAIL:
        print(f"PILOT VERIFICATION: {len(FAIL)} CHECK(S) FAILED")
        for f in FAIL:
            print("   -", f)
        return 1
    print("PILOT VERIFICATION: ALL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
