"""
EXP-0012 runner — unseen faults / hypothesis-space mismatch.

Executes the pre-registered design in experiment_spec.md. The KNOWN-fault hypothesis
library is reused unchanged from DS-0001/DS-0002; only the unseen-fault trajectories
(DS-0003) are new.

Reports the posterior and the residual SEPARATELY throughout, because the whole point is
that they carry different information: the posterior cannot express hypothesis-space
mismatch (FACT 1), the residual can (FACT 2).
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

from aircraft.gfw1 import CHANNELS                              # noqa: E402
from analysis.hypothesis_mismatch import (                     # noqa: E402
    diagnose_unseen, chi2_threshold, false_confidence,
)
from analysis.magnitude_ambiguity import (                     # noqa: E402
    TemplateSet, continuous_manifold_overlap,
)

CFG2P = os.path.join(ROOT, "experiments", "EXP-0002", "config", "exp0002.yaml")
CFG11P = os.path.join(ROOT, "experiments", "EXP-0011", "config", "exp0011.yaml")
CFG12P = os.path.join(ROOT, "experiments", "EXP-0012", "config", "exp0012.yaml")
RES11 = os.path.join(ROOT, "results", "validation", "EXP-0011")
RES = os.path.join(ROOT, "results", "validation", "EXP-0012")
N_MC = 10000            # chosen in the pilot from measured variance


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for c in iter(lambda: fh.read(65536), b""):
            h.update(c)
    return h.hexdigest()


def seed_of(base, *parts):
    return int(hashlib.sha256("|".join(map(str, (base,) + parts)).encode()).hexdigest()[:8], 16)


def load_known(index, fc, window, onset, sigma):
    rows, labels, mags = [], [], []
    for key, meta in index.items():
        f, cls, mstr = key.split("|")
        if f != fc or not meta["valid"]:
            continue
        z = np.load(os.path.join(ROOT, meta["path"]))
        t = z["t"]
        mask = (t >= onset - 1e-12) & (t <= onset + window + 1e-12)
        rows.append((z["y"][mask] / sigma).ravel())
        labels.append(cls)
        mags.append(None if cls == "F0" or cls.startswith("F4") else float(mstr))
    return np.asarray(rows), labels, mags


def load_traj(path, window, onset, sigma):
    z = np.load(os.path.join(ROOT, path))
    t = z["t"]
    mask = (t >= onset - 1e-12) & (t <= onset + window + 1e-12)
    return (z["y"][mask] / sigma).ravel()


def classify_mode(rec, det_floor, tau, alpha):
    """The three failure modes, kept strictly separate (spec §8)."""
    if rec["deflection_from_F0"] < det_floor:
        return "not_yet_detectable"
    if rec["frac_chi2_rejects"] >= 0.5:
        return "poorly_explained_by_all_known"
    if rec["median_confidence"] >= tau:
        return "confidently_wrong"
    return "ambiguous_among_known"


def main():
    t_start = time.perf_counter()
    os.makedirs(RES, exist_ok=True)
    cfg2 = yaml.safe_load(open(CFG2P, encoding="utf-8"))
    cfg11 = yaml.safe_load(open(CFG11P, encoding="utf-8"))
    cfg = yaml.safe_load(open(CFG12P, encoding="utf-8"))
    ti = json.load(open(os.path.join(RES11, "template_index.json"), encoding="utf-8"))["index"]
    ui = json.load(open(os.path.join(RES, "unseen_index.json"), encoding="utf-8"))

    sigma = np.array([float(cfg2["sensors"]["sigma"][c]) for c in CHANNELS])
    onset = float(cfg2["simulation"]["fault_onset"])
    conds = cfg["flight_conditions"]
    wins = [float(w) for w in cfg["observation_windows"]]
    etas = [float(e) for e in cfg["noise"]["eta_levels"]]
    scales = [float(s) for s in cfg["magnitude_scales"]]
    ufs = list(cfg["unseen_faults"].keys())
    tau = float(cfg["metrics"]["confidence_threshold"])
    alpha = float(cfg["metrics"]["chi2_alpha"])
    det_floor = float(cfg11["detectability"]["min_deflection"])
    base = int(cfg["noise"]["seed_base"])

    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    print(f"EXP-0012  commit={commit[:8]} cfg={sha256_file(CFG12P)[:12]}  N_mc={N_MC}")
    print(f"  hypothesis library reused unchanged from DS-0001/DS-0002; "
          f"{len(ufs)} unseen faults x {len(scales)} magnitudes (DS-0003)")

    results, manifold, control = {}, {}, {}
    for fc in conds:
        for w in wins:
            W, labels, mags = load_known(ti, fc, w, onset, sigma)
            KN = W.shape[1]
            n_known = len(labels)

            # ---- nearest-known CONTINUOUS manifold distance (extends EXP-0011)
            for uf in ufs:
                for s in scales:
                    key = f"{fc}|{uf}|{s:.8f}"
                    meta = ui["index"][key]
                    if not meta["valid"]:
                        continue
                    wu = load_traj(meta["path"], w, onset, sigma)
                    ts = TemplateSet(np.vstack([W, wu[None, :]]),
                                     list(zip(labels, mags)) + [(uf, None)],
                                     np.ones(n_known + 1, dtype=bool))
                    cls, D, arg, fits, _ = continuous_manifold_overlap(
                        ts, np.ones(n_known + 1, dtype=bool), 1.0)
                    iu = cls.index(uf)
                    row = [(cls[j], float(D[iu, j])) for j in range(len(cls))
                           if j != iu and np.isfinite(D[iu, j])]
                    row.sort(key=lambda r: r[1])
                    i0 = cls.index("F0")
                    manifold[f"{fc}|{w}|{uf}|{s}"] = {
                        "nearest_class": row[0][0], "nearest_distance": row[0][1],
                        "second_class": row[1][0], "second_distance": row[1][1],
                        "distance_to_F0": float(D[iu, i0]),
                        "chi2_detection_threshold": float(np.sqrt(
                            2.3263 * np.sqrt(2.0 * KN))),
                    }

                    # ---- diagnosis at each noise level
                    Aug = np.vstack([W, wu[None, :]])
                    M = Aug @ Aug.T
                    class_of = labels + [uf]
                    mask = np.zeros(n_known + 1, dtype=bool)
                    mask[:n_known] = True
                    for eta in etas:
                        r = diagnose_unseen(M, n_known, class_of, mask, eta, N_MC,
                                            np.random.default_rng(seed_of(base, fc, w, uf, s, eta)),
                                            KN)
                        rec = {
                            "modal_winner": r["modal_winner"],
                            "winner_counts": r["winner_counts"],
                            "median_confidence": r["median_confidence"],
                            "mean_confidence": r["mean_confidence"],
                            "max_confidence": r["max_confidence"],
                            "FC_at_tau": false_confidence(r["conf_ge_threshold"], tau),
                            "mean_runner_up_margin": r["mean_runner_up_margin"],
                            "normalised_residual": r["normalised_residual"],
                            "median_chi2_pvalue": r["median_chi2_pvalue"],
                            "frac_chi2_rejects": r["frac_chi2_rejects_at_01"],
                            "nearest_distance": row[0][1],
                            "deflection_from_F0": float(D[iu, i0]) / eta,
                            "KN": KN,
                        }
                        rec["failure_mode"] = classify_mode(rec, det_floor, tau, alpha)
                        results[f"{fc}|{w}|{uf}|{s}|{eta}"] = rec

            # ---- Case A control: a KNOWN fault through the identical pipeline
            for ctrl_cls, ctrl_mag in (("F1_q", 1.0), ("F6", 1.0)):
                kk = [i for i, (c, m) in enumerate(zip(labels, mags))
                      if c == ctrl_cls and (m is None or abs(m - ctrl_mag) < 1e-9)]
                if not kk:
                    continue
                wu = W[kk[0]]
                M = np.vstack([W, wu[None, :]]) @ np.vstack([W, wu[None, :]]).T
                class_of = labels + [ctrl_cls + "_TRUTH"]
                mask = np.zeros(n_known + 1, dtype=bool)
                mask[:n_known] = True
                r = diagnose_unseen(M, n_known, class_of, mask, 1.0, N_MC,
                                    np.random.default_rng(seed_of(base, fc, w, ctrl_cls)), KN)
                control[f"{fc}|{w}|{ctrl_cls}"] = {
                    "modal_winner": r["modal_winner"],
                    "correct": r["modal_winner"] == ctrl_cls,
                    "median_confidence": r["median_confidence"],
                    "normalised_residual": r["normalised_residual"],
                    "frac_chi2_rejects": r["frac_chi2_rejects_at_01"],
                }
        print(f"  {fc} done ({time.perf_counter()-t_start:.0f} s)")

    # ------------------------------------------------------------------ summary
    print("\nPRIMARY RESULT (eta=1, magnitude x1): posterior vs residual")
    print(f"  {'uf':>7} {'window':>7} {'winner':>10} {'conf':>7} {'FC@.95':>7} "
          f"{'resid/KN':>9} {'chi2 rej':>9} {'mode':>32}")
    for uf in ufs:
        for w in (0.5, 2.0, 18.0):
            for fc in ["FC-1"]:
                k = f"{fc}|{w}|{uf}|1.0|1.0"
                if k not in results:
                    continue
                r = results[k]
                print(f"  {uf:>7} {w:7.2f} {r['modal_winner']:>10} "
                      f"{r['median_confidence']:7.4f} {r['FC_at_tau']:7.3f} "
                      f"{r['normalised_residual']:9.3f} {r['frac_chi2_rejects']:9.3f} "
                      f"{r['failure_mode']:>32}")

    print("\nCASE A CONTROL (known faults through the identical pipeline, eta=1)")
    ok = sum(1 for v in control.values() if v["correct"])
    print(f"  correct in {ok}/{len(control)} cells; "
          f"median residual/KN at full window: " +
          ", ".join(f"{c}={control[f'FC-1|18.0|{c}']['normalised_residual']:.3f}"
                    for c in ("F1_q", "F6") if f"FC-1|18.0|{c}" in control))

    print("\nFAILURE-MODE CENSUS (all cells, eta=1, magnitude x1)")
    census = {}
    for k, r in results.items():
        fc, w, uf, s, eta = k.split("|")
        if float(eta) != 1.0 or float(s) != 1.0:
            continue
        census[r["failure_mode"]] = census.get(r["failure_mode"], 0) + 1
    for m, n in sorted(census.items(), key=lambda x: -x[1]):
        print(f"  {m:>34}: {n}")

    runtime = time.perf_counter() - t_start
    payload = {
        "experiment_id": "EXP-0012",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": commit,
        "config": "experiments/EXP-0012/config/exp0012.yaml",
        "config_sha256": sha256_file(CFG12P),
        "source_datasets": ["DS-0001", "DS-0002", "DS-0003"],
        "environment": {"python": platform.python_version(), "numpy": np.__version__,
                        "platform": platform.platform()},
        "n_mc": N_MC,
        "confidence_threshold_tau": tau,
        "chi2_alpha": alpha,
        "confidence_definition": (
            "Posterior over H_known under a uniform class prior and the stated Gaussian "
            "noise model, with fault magnitude marginalised over the EXP-0011 grid. It is "
            "a probability CONDITIONAL on the hypothesis space containing the truth -- the "
            "condition this experiment deliberately violates. It is NOT the probability "
            "that the diagnosis is correct."),
        "unseen_faults": {u: cfg["unseen_faults"][u] for u in ufs},
        "results": results,
        "manifold": manifold,
        "control_known_faults": control,
        "failure_mode_census_eta1_mag1": census,
        "excluded_trajectories": ui["excluded"],
        "runtime_seconds": runtime,
    }
    with open(os.path.join(RES, "exp0012_results.json"), "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, default=float)
    print(f"\nDone in {runtime:.1f} s.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
