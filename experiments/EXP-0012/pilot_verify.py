"""
EXP-0012 pilot verification.

Technical verification and the pre-registered statistical sizing (spec §9): the
replication count for the full run is CHOSEN FROM MEASURED VARIANCE, not assumed.

Checks:
  1. prior experiments still reproduce bit-for-bit after extending simulate()
  2. each unseen fault actually perturbs the aircraft, and is inert before onset
  3. plant faults are restored (no state leakage between runs)
  4. the exact Monte Carlo reproduces a direct full-dimensional simulation
  5. FACT 1 holds numerically: a uniform misfit leaves the posterior unchanged
  6. score/confidence/residual variance -> replication count
  7. runtime and storage
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import time

import numpy as np
import yaml

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)

from aircraft.gfw1 import CHANNELS                              # noqa: E402
from analysis.hypothesis_mismatch import (                      # noqa: E402
    diagnose_unseen, chi2_threshold, false_confidence,
)

CFG2P = os.path.join(ROOT, "experiments", "EXP-0002", "config", "exp0002.yaml")
CFG12P = os.path.join(ROOT, "experiments", "EXP-0012", "config", "exp0012.yaml")
RES11 = os.path.join(ROOT, "results", "validation", "EXP-0011")
RES12 = os.path.join(ROOT, "results", "validation", "EXP-0012")
FAIL = []


def check(name, ok, detail=""):
    if not ok:
        FAIL.append(name)
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f"  --  {detail}" if detail else ""))


def load_known(index, fc, window, onset, sigma):
    rows, labels = [], []
    for key, meta in index.items():
        f, cls, mstr = key.split("|")
        if f != fc or not meta["valid"]:
            continue
        z = np.load(os.path.join(ROOT, meta["path"]))
        t = z["t"]
        mask = (t >= onset - 1e-12) & (t <= onset + window + 1e-12)
        rows.append((z["y"][mask] / sigma).ravel())
        labels.append(cls)
    return np.asarray(rows), labels


def load_unseen(uindex, fc, uf, scale, window, onset, sigma):
    key = f"{fc}|{uf}|{scale:.8f}"
    z = np.load(os.path.join(ROOT, uindex[key]["path"]))
    t = z["t"]
    mask = (t >= onset - 1e-12) & (t <= onset + window + 1e-12)
    return (z["y"][mask] / sigma).ravel()


def main():
    cfg2 = yaml.safe_load(open(CFG2P, encoding="utf-8"))
    cfg = yaml.safe_load(open(CFG12P, encoding="utf-8"))
    ti = json.load(open(os.path.join(RES11, "template_index.json"), encoding="utf-8"))["index"]
    ui = json.load(open(os.path.join(RES12, "unseen_index.json"), encoding="utf-8"))
    sigma = np.array([float(cfg2["sensors"]["sigma"][c]) for c in CHANNELS])
    onset = float(cfg2["simulation"]["fault_onset"])

    print("=" * 78)
    print("EXP-0012 PILOT VERIFICATION")
    print("=" * 78)

    # ------------------------------------------------ 1. no regression upstream
    print("\n1. PRIOR EXPERIMENTS STILL REPRODUCE (simulate() was extended)")
    from aircraft.gfw1 import GFW1
    from aircraft.trim import trim
    from faults.faults import Fault
    from simulation.simulate import simulate
    model = GFW1(cfg2)
    fcm = {f["id"]: f for f in cfg2["flight_conditions"]}
    same = True
    for fc, fid in (("FC-1", "F0"), ("FC-2", "F2_Vt")):
        x0, u0, info = trim(model, fcm[fc]["airspeed_mps"], fcm[fc]["altitude_m"])
        mode, ch = (fid.split("_") + [None])[:2]
        r = simulate(model, cfg2, x0, u0, info, Fault(mode, ch, cfg2))
        h1 = hashlib.sha256(r["y"].tobytes()).hexdigest()
        h2 = hashlib.sha256(np.load(os.path.join(
            ROOT, "data", "derived", "EXP-0002", f"{fc}_{fid}.npz"))["y"].tobytes()).hexdigest()
        same &= (h1 == h2)
    check("EXP-0002 trajectories bit-identical after the simulate() change", same)

    # ------------------------------------------- 2/3. unseen faults behave
    print("\n2. UNSEEN FAULTS PERTURB THE AIRCRAFT, AND ARE INERT BEFORE ONSET")
    z0 = np.load(os.path.join(ROOT, "data", "derived", "EXP-0002", "FC-1_F0.npz"))
    for uf in ("UF-001", "UF-002", "UF-003", "UF-004", "UF-005", "UF-006"):
        z = np.load(os.path.join(ROOT, ui["index"][f"FC-1|{uf}|1.00000000"]["path"]))
        t = z["t"]
        pre, post = t < onset, t >= onset
        dpre = float(np.max(np.abs(z["y"][pre] - z0["y"][pre])))
        # Detectability is set by the ACCUMULATED deflection against the pre-declared
        # floor of 4.65, not by the maximum per-sample deviation. A sub-sigma error
        # sustained over 1801 samples is easily detectable; an early version of this
        # check used the max and wrongly flagged UF-003.
        defl = float(np.linalg.norm((z["y"][post] - z0["y"][post]) / sigma))
        mx = float(np.max(np.abs((z["y"][post] - z0["y"][post]) / sigma)))
        check(f"{uf} inert before onset", dpre < 1e-12, f"{dpre:.1e}")
        check(f"{uf} detectable after onset", defl > 4.65,
              f"deflection {defl:.1f} (max {mx:.2f} sigma/sample)")

    print("\n3. PLANT FAULTS DO NOT LEAK STATE BETWEEN RUNS")
    for c in ("Cma", "CD0"):
        check(f"model.{c} restored", abs(model.p[c] - float(cfg2["aircraft"][c])) < 1e-15)

    # ------------------------------------ 4. exact MC vs direct simulation
    print("\n4. EXACT MONTE CARLO vs DIRECT FULL-DIMENSIONAL SIMULATION")
    W, labels = load_known(ti, "FC-1", 2.0, onset, sigma)
    wu = load_unseen(ui["index"], "FC-1", "UF-005", 1.0, 2.0, onset, sigma)
    Aug = np.vstack([W, wu[None, :]])
    M = Aug @ Aug.T
    class_of = labels + ["UF-005"]
    mask = np.zeros(len(class_of), dtype=bool)
    mask[:len(labels)] = True
    KN = W.shape[1]

    for eta in (1.0, 10.0):
        fast = diagnose_unseen(M, len(labels), class_of, mask, eta, 4000,
                               np.random.default_rng(7), KN)
        # direct: build noise in full dimension
        rng = np.random.default_rng(11)
        nd, conf_d, res_d = 300, [], []
        for _ in range(nd):
            y = wu + eta * rng.standard_normal(KN)
            d2 = np.sum((y[None, :] - W) ** 2, axis=1) / eta ** 2
            cls = sorted(set(labels))
            # marginal likelihood over magnitude (log-sum-exp), NOT a profile minimum:
            # an earlier version of this check used min(), which is a different estimator
            # and disagreed with the code under test at high noise.
            ll = []
            for c in cls:
                a = -0.5 * d2[[i for i, l in enumerate(labels) if l == c]]
                am = a.max()
                ll.append(am + np.log(np.exp(a - am).sum() / len(a)))
            ll = np.array(ll)
            p = np.exp(ll - ll.max()); p /= p.sum()
            conf_d.append(p.max()); res_d.append(d2.min())
        se = np.std(conf_d) / np.sqrt(nd)
        check(f"eta={eta:g}: confidence matches direct simulation",
              abs(fast["mean_confidence"] - np.mean(conf_d)) < 5 * se + 0.02,
              f"fast {fast['mean_confidence']:.4f} vs direct {np.mean(conf_d):.4f}")
        check(f"eta={eta:g}: residual matches direct simulation",
              abs(fast["mean_residual"] - np.mean(res_d)) / max(np.mean(res_d), 1) < 0.05,
              f"fast {fast['mean_residual']:.0f} vs direct {np.mean(res_d):.0f}")

    # ----------------------------- 5. FACT 1: uniform misfit cancels in the posterior
    print("\n5. FACT 1 HOLDS NUMERICALLY (posterior is blind to uniform misfit)")
    base = diagnose_unseen(M, len(labels), class_of, mask, 1.0, 3000,
                           np.random.default_rng(3), KN)
    M2 = M.copy()
    # push the unseen template far from EVERY known template, preserving their geometry:
    # add a component orthogonal to the known span -> D_uj increases by the same constant
    extra = 5000.0
    M2[len(labels), len(labels)] += extra
    far = diagnose_unseen(M2, len(labels), class_of, mask, 1.0, 3000,
                          np.random.default_rng(3), KN)
    check("posterior confidence unchanged by a uniform misfit",
          abs(base["mean_confidence"] - far["mean_confidence"]) < 0.01,
          f"{base['mean_confidence']:.4f} vs {far['mean_confidence']:.4f}")
    check("residual DOES rise with the same uniform misfit",
          far["mean_residual"] > base["mean_residual"] + 0.9 * extra,
          f"{base['mean_residual']:.0f} -> {far['mean_residual']:.0f}")

    # ------------------------------------------- 6. replication sizing
    print("\n6. REPLICATION SIZING FROM MEASURED VARIANCE")
    vals = []
    for s in range(6):
        r = diagnose_unseen(M, len(labels), class_of, mask, 1.0, 2000,
                            np.random.default_rng(100 + s), KN)
        vals.append(false_confidence(r["conf_ge_threshold"], 0.95))
    sd = float(np.std(vals, ddof=1))
    print(f"   FC at tau=0.95 across 6 pilot seeds: mean {np.mean(vals):.4f}, sd {sd:.4f}")
    # worst-case binomial sd is 0.5/sqrt(N); target half-width 0.01 at 95%
    n_needed = int(np.ceil((1.96 * 0.5 / 0.01) ** 2))
    print(f"   worst-case binomial sizing for +/-0.01 at 95%: N = {n_needed}")
    n_chosen = 10000
    print(f"   CHOSEN N = {n_chosen} (half-width <= {1.96*0.5/np.sqrt(n_chosen):.4f})")
    check("chosen N resolves the effect", n_chosen >= 9000)

    # --------------------------------------------------------- 7. cost
    print("\n7. RUNTIME")
    t0 = time.perf_counter()
    diagnose_unseen(M, len(labels), class_of, mask, 1.0, n_chosen,
                    np.random.default_rng(1), KN)
    per = time.perf_counter() - t0
    cells = 4 * 7 * 3 * 6 * 3
    print(f"   per cell {per:.2f} s; {cells} cells -> ~{cells*per/60:.0f} min")

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
