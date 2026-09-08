"""
EXP-0011 runner — unknown fault magnitude as a nuisance parameter.

Executes the pre-registered design in experiment_spec.md, using DS-0002 (the magnitude
grid) plus the reused DS-0001 slice at m = 1.0.

Two methodological points, both decided before the results were read:

  * The PRIMARY manifold measure is the **continuous** minimum separation over
    magnitude, not the grid minimum. A discrete grid can only sample near the true
    intersection, so a grid minimum would make the headline number an artefact of grid
    resolution. The grid minimum is retained as validity attack W-A.
  * Detectability is evaluated at the FULL window, as pre-registered: it asks whether a
    fault is large enough to matter at all, which is a property of the fault, not of the
    window being analysed. Window-specific detectability is reported separately.

Nothing here selects a metric, threshold, magnitude range or prior: all come from
configuration.
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

from aircraft.gfw1 import CHANNELS                               # noqa: E402
from analysis.magnitude_ambiguity import (                       # noqa: E402
    TemplateSet, p_disc_from_deflection, overlap_band,
    continuous_manifold_overlap,
)

CFG2P = os.path.join(ROOT, "experiments", "EXP-0002", "config", "exp0002.yaml")
CFG11P = os.path.join(ROOT, "experiments", "EXP-0011", "config", "exp0011.yaml")
RES = os.path.join(ROOT, "results", "validation", "EXP-0011")


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for c in iter(lambda: fh.read(65536), b""):
            h.update(c)
    return h.hexdigest()


def cell_seed(base, *parts):
    return int(hashlib.sha256("|".join(map(str, (base,) + parts)).encode()).hexdigest()[:8], 16)


def build_templates(index, fc, window, onset, sigma):
    rows, labels, valid = [], [], []
    for key, meta in index.items():
        f, cls, mstr = key.split("|")
        if f != fc:
            continue
        z = np.load(os.path.join(ROOT, meta["path"]))
        t = z["t"]
        mask = (t >= onset - 1e-12) & (t <= onset + window + 1e-12)
        rows.append((z["y"][mask] / sigma).ravel())
        # F0 and F4 ("stuck") are magnitude-free: one template each.
        no_mag = (cls == "F0") or cls.startswith("F4")
        labels.append((cls, None if no_mag else float(mstr)))
        valid.append(bool(meta["valid"]))
    return TemplateSet(np.asarray(rows), labels, valid)


def main():
    t_start = time.perf_counter()
    os.makedirs(RES, exist_ok=True)
    cfg2 = yaml.safe_load(open(CFG2P, encoding="utf-8"))
    cfg = yaml.safe_load(open(CFG11P, encoding="utf-8"))
    tindex = json.load(open(os.path.join(RES, "template_index.json"), encoding="utf-8"))
    index = tindex["index"]

    sigma = np.array([float(cfg2["sensors"]["sigma"][c]) for c in CHANNELS])
    onset = float(cfg2["simulation"]["fault_onset"])
    conds, wins = cfg["flight_conditions"], [float(w) for w in cfg["observation_windows"]]
    etas = [float(e) for e in cfg["noise"]["eta_levels"]]
    grid = [float(x) for x in cfg["magnitude"]["grid"]]
    n_mc = int(cfg["monte_carlo"]["replications"])
    seed_base = int(cfg["noise"]["seed_base"])
    bands, kc = cfg["metrics"]["overlap_bands"], cfg["knowledge_conditions"]
    det_min = float(cfg["detectability"]["min_deflection"])

    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    print(f"EXP-0011  commit={commit[:8]} cfg={sha256_file(CFG11P)[:12]}")
    print(f"  templates: {tindex['n_generated']} generated + {tindex['n_reused']} reused, "
          f"{len(tindex['excluded'])} excluded by the pre-declared validity rule")

    sets = {(fc, w): build_templates(index, fc, w, onset, sigma)
            for fc in conds for w in wins}
    ts0 = sets[(conds[0], 18.0)]
    print(f"  {len(ts0.labels)} templates per condition, {len(ts0.classes)} classes")

    # Detectability is a property of the fault (pre-registered: evaluated at the full window)
    det, det_local = {}, {}
    for fc in conds:
        ts = sets[(fc, 18.0)]
        i0 = ts.labels.index(("F0", None))
        d = ts.detectable(i0, det_min) & ts.valid
        # BUGFIX: the NOMINAL class is always admissible. d(F0,F0)=0 < the floor, so F0
        # was being dropped from the manifold analysis and made unselectable by the
        # Case B/C classifier while Case A could still choose it -- biasing that comparison.
        d[i0] = True
        det[fc] = d
        # Window-LOCAL detectability (POST-HOC, not pre-registered). The pre-registered
        # floor is evaluated at the full window, so at short windows it admits faults that
        # are not visible at all, conflating "these two faults look alike" with "neither is
        # visible yet". This screens that out.
        for w in wins:
            tsw = sets[(fc, w)]
            j0 = tsw.labels.index(("F0", None))
            dl = tsw.detectable(j0, det_min) & tsw.valid
            dl[j0] = True
            det_local[(fc, w)] = dl
        print(f"  {fc}: {int(det[fc].sum())}/{len(ts.labels)} admissible at full window; "
              f"window-local at 0.5 s: {int(det_local[(fc, 0.5)].sum())}")

    # ------------------------------------- PRIMARY: continuous manifold overlap
    print("\nCONTINUOUS MANIFOLD OVERLAP (magnitude free within its admissible range)")
    manifold = {}
    for fc in conds:
        rec = {}
        for w in wins:
            ts = sets[(fc, w)]
            cls, D, arg, fits, ndeg = continuous_manifold_overlap(ts, det[fc], 1.0)
            P = p_disc_from_deflection(D, 1.0)
            pairs = []
            for a in range(len(cls)):
                for b in range(a + 1, len(cls)):
                    if not np.isfinite(D[a, b]):
                        continue
                    ma, mb, _ = arg[(cls[a], cls[b])]
                    pairs.append({"a": cls[a], "b": cls[b], "D_min": float(D[a, b]),
                                  "P_disc_worst": float(P[a, b]),
                                  "band": overlap_band(P[a, b], bands),
                                  "m_a": ma, "m_b": mb})
            pairs.sort(key=lambda p: p["P_disc_worst"])
            counts = {}
            for p in pairs:
                counts[p["band"]] = counts.get(p["band"], 0) + 1
            rec[str(w)] = {
                "band_counts": counts,
                "worst_pairs": pairs[:10],
                "n_degenerate_classes": ndeg,
                "mean_linear_fit_residual": float(np.mean(
                    [f["residual_frac"] for f in fits.values() if not f["point_class"]])),
                "max_linear_fit_residual": float(np.max(
                    [f["residual_frac"] for f in fits.values() if not f["point_class"]])),
            }
        manifold[fc] = rec
        for w in (0.5, 2.0, 18.0):
            r = rec[str(w)]
            wp = r["worst_pairs"][0]
            print(f"  {fc} w={w:5.2f}s: {r['band_counts']}  worst {wp['a']}/{wp['b']} "
                  f"P={wp['P_disc_worst']:.3f} at m=({wp['m_a']},{wp['m_b']})")

    # ---- POST-HOC: manifold overlap restricted to faults VISIBLE IN THE WINDOW
    print("\nMANIFOLD OVERLAP, window-local detectability (POST-HOC, not pre-registered)")
    manifold_local = {}
    for fc in conds:
        rec = {}
        for w in wins:
            ts = sets[(fc, w)]
            cls, D, arg, fits, ndeg = continuous_manifold_overlap(ts, det_local[(fc, w)], 1.0)
            P = p_disc_from_deflection(D, 1.0)
            pairs = []
            for a in range(len(cls)):
                for b in range(a + 1, len(cls)):
                    if not np.isfinite(D[a, b]):
                        continue
                    ma, mb, _ = arg[(cls[a], cls[b])]
                    pairs.append({"a": cls[a], "b": cls[b], "D_min": float(D[a, b]),
                                  "P_disc_worst": float(P[a, b]),
                                  "band": overlap_band(P[a, b], bands), "m_a": ma, "m_b": mb})
            pairs.sort(key=lambda p: p["P_disc_worst"])
            counts = {}
            for p in pairs:
                counts[p["band"]] = counts.get(p["band"], 0) + 1
            rec[str(w)] = {"band_counts": counts, "worst_pairs": pairs[:10],
                           "n_classes_visible": len(cls), "n_pairs": len(pairs)}
        manifold_local[fc] = rec
        for w in (0.5, 2.0, 18.0):
            r = rec[str(w)]
            wp = r["worst_pairs"][0] if r["worst_pairs"] else None
            extra = (f"  worst {wp['a']}/{wp['b']} P={wp['P_disc_worst']:.3f}") if wp else ""
            print(f"  {fc} w={w:5.2f}s: {r['n_classes_visible']} classes visible, "
                  f"{r['band_counts']}{extra}")


    # ------------------------------------------------------ classifier sweep
    print("\nCLASSIFIER SWEEP (P_class: correct fault-CLASS identification)")
    P_class, mag_err = {}, {}
    for fc in conds:
        for w in wins:
            ts = sets[(fc, w)]
            for case in ("A_known", "B_bounded", "C_broad"):
                gi = kc[case]["grid_indices"]
                prior = None
                if gi is not None:
                    allowed = {grid[k] for k in gi}
                    prior = [k for k, (c, m) in enumerate(ts.labels)
                             if (m is None or m in allowed) and det[fc][k]]
                for eta in etas:
                    r = ts.classify_mc(
                        eta, n_mc, np.random.default_rng(cell_seed(seed_base, fc, w)),
                        case=case[0], prior_indices=prior,
                        true_indices=[k for k in range(len(ts.labels)) if det[fc][k]],
                        estimate_magnitude=(case != "A_known"))
                    P_class[f"{fc}|{w}|{case}|{eta}"] = r["P_class"]
                    if r["mean_relative_magnitude_error"] is not None:
                        mag_err[f"{fc}|{w}|{case}|{eta}"] = r["mean_relative_magnitude_error"]
        print(f"  {fc}: " + "  ".join(
            f"{w:g}s[A={P_class[f'{fc}|{w}|A_known|1.0']:.3f} "
            f"C={P_class[f'{fc}|{w}|C_broad|1.0']:.3f}]" for w in (0.5, 2.0, 18.0)))

    # EXPLORATORY (not pre-registered). Case B as pre-registered draws truths from the
    # FULL grid, so its prior excludes the truth 4/9 of the time -- it therefore measures
    # prior MISSPECIFICATION, not bounded knowledge. This variant matches truths to the
    # prior and so measures bounded knowledge.
    print("\nEXPLORATORY  Case B-prime: bounded prior WITH matched truths")
    P_class_Bprime = {}
    for fc in conds:
        for w in wins:
            ts = sets[(fc, w)]
            allowed = {grid[k] for k in kc["B_bounded"]["grid_indices"]}
            keep = [k for k, (c, mm) in enumerate(ts.labels)
                    if (mm is None or mm in allowed) and det[fc][k]]
            for eta in etas:
                r = ts.classify_mc(eta, n_mc,
                                   np.random.default_rng(cell_seed(seed_base, fc, w)),
                                   case="B", prior_indices=keep, true_indices=keep,
                                   estimate_magnitude=False)
                P_class_Bprime[f"{fc}|{w}|{eta}"] = r["P_class"]
        print(f"  {fc}: " + "  ".join(f"{w:g}s={P_class_Bprime[f'{fc}|{w}|1.0']:.3f}"
                                      for w in (0.5, 2.0, 18.0)))


    # ------------------------------------------- analytical prediction test
    print("\nANALYTICAL PREDICTION TEST (F1_Vt / F2_Vt, magnitude free) -- not refitted")
    k = float(cfg2["faults"]["scale_factor"])
    sV = float(cfg2["sensors"]["sigma"]["Vt"])
    analytic = {}
    for fc in conds:
        rec = {}
        z = np.load(os.path.join(ROOT, "data", "derived", "EXP-0002", f"{fc}_F0.npz"))
        tt = z["t"]
        for w in wins:
            mask = (tt >= onset - 1e-12) & (tt <= onset + w + 1e-12)
            V = z["y"][mask, CHANNELS.index("Vt")]
            d_pred = np.sqrt(len(V)) * (k - 1.0) * float(np.std(V)) / sV
            ts = sets[(fc, w)]
            cls, D, _, _, _ = continuous_manifold_overlap(ts, det[fc], 1.0)
            ia, ib = cls.index("F1_Vt"), cls.index("F2_Vt")
            rec[str(w)] = {"d_pred_lower_bound": float(d_pred),
                           "d_measured": float(D[ia, ib]),
                           "P_pred": float(p_disc_from_deflection(d_pred, 1.0)),
                           "P_measured": float(p_disc_from_deflection(D[ia, ib], 1.0)),
                           "std_V_in_window": float(np.std(V))}
        analytic[fc] = rec
        print(f"  {fc}: " + "  ".join(
            f"{w:g}s[pred {rec[str(w)]['d_pred_lower_bound']:.2f} "
            f"meas {rec[str(w)]['d_measured']:.2f}]" for w in (0.5, 2.0, 18.0)))
    pr = [analytic[fc][str(w)]["d_pred_lower_bound"] for fc in conds for w in wins]
    me = [analytic[fc][str(w)]["d_measured"] for fc in conds for w in wins]
    ar = float(np.corrcoef(pr, me)[0, 1])
    print(f"  Pearson(predicted lower bound, measured) over all {len(pr)} cells = {ar:.4f}")

    # ------------------------------------------------------- validity attacks
    print("\nW-A GRID MINIMUM vs CONTINUOUS MINIMUM")
    grid_check = {}
    for fc in conds:
        ts = sets[(fc, 0.5)]
        _, Dg, _ = ts.manifold_overlap(1.0, restrict=det[fc])
        cls, Dc, _, _, _ = continuous_manifold_overlap(ts, det[fc], 1.0)
        iu = np.triu_indices(Dc.shape[0], 1)
        g = Dg[:Dc.shape[0], :Dc.shape[0]][iu]
        c = Dc[iu]
        ok = np.isfinite(g) & np.isfinite(c) & (c > 1e-6)   # exclude exact coincidences
        ratio = g[ok] / c[ok]
        grid_check[fc] = {"n_pairs_compared": int(ok.sum()),
                          "median_ratio_grid_over_continuous": float(np.median(ratio)),
                          "max_ratio": float(np.max(ratio)),
                          "n_exactly_coincident": int((c <= 1e-6).sum())}
        print(f"  {fc} (0.5 s): over {int(ok.sum())} resolvable pairs the grid overstates "
              f"separation by a median {np.median(ratio):.2f}x (max {np.max(ratio):.1f}x); "
              f"{int((c<=1e-6).sum())} pairs exactly coincident")

    print("\nW-B MAGNITUDE RANGE (Case B [0.5,2] vs Case C [0.25,4])")
    range_check = {}
    for fc in conds:
        row = {}
        for w in (0.5, 2.0, 18.0):
            row[str(w)] = {"B": P_class[f"{fc}|{w}|B_bounded|1.0"],
                           "C": P_class[f"{fc}|{w}|C_broad|1.0"]}
        range_check[fc] = row
        print(f"  {fc}: " + "  ".join(
            f"{w:g}s[B={row[str(w)]['B']:.3f} C={row[str(w)]['C']:.3f}]"
            for w in (0.5, 2.0, 18.0)))

    print("\nW-G DETECTABILITY FLOOR ON/OFF (0.5 s window)")
    floor_check = {}
    for fc in conds:
        ts = sets[(fc, 0.5)]
        _, Don, _, _, _ = continuous_manifold_overlap(ts, det[fc], 1.0)
        _, Doff, _, _, _ = continuous_manifold_overlap(ts, ts.valid, 1.0)
        floor_check[fc] = {"min_with_floor": float(np.nanmin(Don)),
                           "min_without_floor": float(np.nanmin(Doff)),
                           "n_below_floor": int((ts.valid & ~det[fc]).sum())}
        print(f"  {fc}: with floor {np.nanmin(Don):.3f}, without {np.nanmin(Doff):.3f}, "
              f"{floor_check[fc]['n_below_floor']} templates below floor")

    print("\nW-E LINEARITY OF THE MAGNITUDE FAMILIES")
    for fc in conds:
        r = manifold[fc]["18.0"]
        print(f"  {fc}: mean fit residual {r['mean_linear_fit_residual']*100:.3f}%, "
              f"max {r['max_linear_fit_residual']*100:.3f}%")

    # ---------------------------------------------------------------- outputs
    runtime = time.perf_counter() - t_start
    payload = {
        "experiment_id": "EXP-0011",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": commit,
        "config": "experiments/EXP-0011/config/exp0011.yaml",
        "config_sha256": sha256_file(CFG11P),
        "source_datasets": ["DS-0001", "DS-0002"],
        "environment": {"python": platform.python_version(), "numpy": np.__version__,
                        "platform": platform.platform()},
        "classes": ts0.classes,
        "flight_conditions": conds,
        "observation_windows": wins,
        "eta_levels": etas,
        "magnitude_grid": grid,
        "monte_carlo_replications": n_mc,
        "probabilistic_interpretation": (
            "All probabilities are conditional on the GFW-1 model, the fault taxonomy, "
            "the declared magnitude grid and uniform priors, the Gaussian white noise "
            "model, the stated sigma, and the observation window. Template FAMILIES are "
            "still assumed exactly known (TV-M5), so these remain upper bounds. They are "
            "not real-world confidences."),
        "primary_manifold_measure": "continuous minimum over magnitude (linear family fit)",
        "n_detectable": {fc: int(det[fc].sum()) for fc in conds},
        "manifold_overlap": manifold,
        "manifold_overlap_window_local": manifold_local,
        "P_class_Bprime_exploratory": P_class_Bprime,
        "P_class": P_class,
        "magnitude_estimation_error": mag_err,
        "analytic_prediction": analytic,
        "analytic_prediction_pearson_r": ar,
        "validity": {"grid_vs_continuous": grid_check, "magnitude_range": range_check,
                     "detectability_floor": floor_check},
        "excluded_templates": tindex["excluded"],
        "runtime_seconds": runtime,
    }
    with open(os.path.join(RES, "exp0011_results.json"), "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, default=float)

    arr = np.zeros((len(conds), len(wins), 3, len(etas)))
    for a, fc in enumerate(conds):
        for b, w in enumerate(wins):
            for c, case in enumerate(("A_known", "B_bounded", "C_broad")):
                for d, e in enumerate(etas):
                    arr[a, b, c, d] = P_class[f"{fc}|{w}|{case}|{e}"]
    np.savez_compressed(os.path.join(RES, "P_class_surface.npz"), P_class=arr,
                        conditions=np.array(conds), windows=np.array(wins),
                        cases=np.array(["A_known", "B_bounded", "C_broad"]),
                        etas=np.array(etas))
    print(f"\nDone in {runtime:.1f} s.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
