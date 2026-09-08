"""
EXP-0012 figures. Three, each answering one question; the redundant candidates in the
brief's figure list are deliberately not generated.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt                                  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)
RES = os.path.join(ROOT, "results", "validation", "EXP-0012")
FIG = os.path.join(ROOT, "results", "figures")
MODE_COL = {"not_yet_detectable": "#b0b0b0", "ambiguous_among_known": "#e07b39",
            "confidently_wrong": "#7a0000", "poorly_explained_by_all_known": "#2e8b57"}


def commit():
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True,
                                       stderr=subprocess.DEVNULL).strip()
    except Exception:
        return "unknown"


def sidecar(name, q, res):
    with open(os.path.join(FIG, f"{name}.json"), "w", encoding="utf-8") as fh:
        json.dump({"figure": name, "question_answered": q, "experiment_id": "EXP-0012",
                   "results_file": "results/validation/EXP-0012/exp0012_results.json",
                   "dataset_ids": ["DS-0001", "DS-0002", "DS-0003"],
                   "script": "visualization/plot_exp0012.py", "git_commit": commit(),
                   "generated_from_results_utc": res["generated_utc"]}, fh, indent=2)


def main():
    res = json.load(open(os.path.join(RES, "exp0012_results.json"), encoding="utf-8"))
    R, M = res["results"], res["manifold"]
    wins = [0.25, 0.5, 1.0, 2.0, 5.0, 10.0, 18.0]

    # ------------------------------------------------------------------ FIG-013
    # Q: does confidence rise while the diagnosis is wrong, and does the fit test miss it?
    fig, ax = plt.subplots(1, 2, figsize=(12.4, 4.7))
    for i, (uf, title) in enumerate((
            ("UF-003", "UF-003 pitot lag → diagnosed as NO FAULT"),
            ("UF-005", "UF-005 pitch-stability loss → diagnosed as\nelevator-effectiveness loss"))):
        conf = [R[f"FC-1|{w}|{uf}|1.0|1.0"]["median_confidence"] for w in wins]
        rej = [R[f"FC-1|{w}|{uf}|1.0|1.0"]["frac_chi2_rejects"] for w in wins]
        win = [R[f"FC-1|{w}|{uf}|1.0|1.0"]["modal_winner"] for w in wins]
        a = ax[i]
        a.plot(wins, conf, "o-", color="#7a0000", lw=2.4, ms=6,
               label="posterior confidence in the WRONG diagnosis")
        a.plot(wins, rej, "s--", color="#2e8b57", lw=2.0, ms=5,
               label=r"$\chi^2$ residual test rejects (catches the mismatch)")
        a.axhline(0.95, color="k", ls=":", lw=1)
        a.annotate(r"$\tau=0.95$", (0.26, 0.965), fontsize=8)
        a.set_xscale("log")
        a.set_xlabel("observation window after fault onset (s)")
        a.set_ylabel("probability")
        a.set_ylim(-0.03, 1.06)
        a.set_title(title, fontsize=10)
        a.legend(fontsize=7.5, loc="center left")
        a.grid(alpha=0.3)
        for w, c, ww in zip(wins, conf, win):
            if w in (0.25, 18.0):
                a.annotate(ww, (w, c), fontsize=7, color="#7a0000",
                           va="bottom", ha="left" if w < 1 else "right")
    fig.suptitle("EXP-0012  The true fault is absent from the hypothesis library. "
                 "Confidence rises anyway.", fontsize=11)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "FIG-013-confidently-wrong.png"), dpi=150)
    plt.close(fig)
    sidecar("FIG-013-confidently-wrong",
            "Does diagnostic confidence increase with observation while the diagnosis is "
            "wrong, and does the goodness-of-fit test catch it?", res)

    # ------------------------------------------------------------------ FIG-014
    # Q: is false confidence explained by proximity to a known manifold?
    fig, ax = plt.subplots(figsize=(7.6, 5.0))
    xs, ys, cs = [], [], []
    for k, v in R.items():
        fc, w, uf, s, eta = k.split("|")
        mk = f"{fc}|{w}|{uf}|{s}"
        if mk not in M:
            continue
        nd = M[mk]["nearest_distance"] / float(eta)
        xs.append(max(nd, 1e-2))
        ys.append(v["median_confidence"])
        cs.append(MODE_COL[v["failure_mode"]])
    ax.scatter(xs, ys, c=cs, s=9, alpha=0.55, linewidths=0)
    thr = [M[f"FC-1|{w}|UF-001|1.0"]["chi2_detection_threshold"] for w in wins]
    ax.axvspan(0.01, min(thr), color="#7a0000", alpha=0.06)
    ax.annotate("below the $\\chi^2$ detection threshold:\n"
                "the residual CANNOT see the mismatch",
                (0.05, 0.45), fontsize=8, color="#7a0000")
    for t in (min(thr), max(thr)):
        ax.axvline(t, color="k", ls="--", lw=1)
    ax.annotate(f"threshold range\n{min(thr):.1f}–{max(thr):.1f}",
                (max(thr) * 1.3, 0.12), fontsize=8)
    ax.axhline(0.95, color="k", ls=":", lw=1)
    ax.set_xscale("log")
    ax.set_xlabel(r"distance from the unseen fault to the nearest KNOWN hypothesis  ($/\eta$)")
    ax.set_ylabel("posterior confidence in the chosen (wrong) hypothesis")
    ax.set_title("False confidence is explained by proximity to a known manifold.\n"
                 "Colour = failure mode; the $\\chi^2$ threshold predicts it in 99.3% of cells.",
                 fontsize=10)
    handles = [plt.Line2D([], [], marker="o", ls="", color=c, label=m.replace("_", " "))
               for m, c in MODE_COL.items()]
    ax.legend(handles=handles, fontsize=8, loc="lower right")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "FIG-014-confidence-vs-manifold-distance.png"), dpi=150)
    plt.close(fig)
    sidecar("FIG-014-confidence-vs-manifold-distance",
            "Is false confidence explained by proximity to a known fault manifold, and "
            "does the analytic detection threshold predict when the residual fails?", res)

    # ------------------------------------------------------------------ FIG-015
    # Q: does more observation fix the problem, and for which faults does it not?
    fig, ax = plt.subplots(1, 2, figsize=(12.4, 4.6))
    modes = ["not_yet_detectable", "ambiguous_among_known",
             "confidently_wrong", "poorly_explained_by_all_known"]
    bottom = np.zeros(len(wins))
    for m in modes:
        vals = []
        for w in wins:
            n = sum(1 for k, v in R.items()
                    if k.split("|")[1] == str(w) and v["failure_mode"] == m)
            t = sum(1 for k in R if k.split("|")[1] == str(w))
            vals.append(100.0 * n / t)
        ax[0].bar(range(len(wins)), vals, bottom=bottom, color=MODE_COL[m],
                  label=m.replace("_", " "), alpha=0.9)
        bottom += np.asarray(vals)
    ax[0].set_xticks(range(len(wins)))
    ax[0].set_xticklabels([f"{w:g}" for w in wins])
    ax[0].set_xlabel("observation window (s)")
    ax[0].set_ylabel("% of cells")
    ax[0].set_title("More observation shifts cells into 'caught by the residual' —\n"
                    "but never eliminates the dangerous mode", fontsize=10)
    ax[0].legend(fontsize=7.5, loc="lower left")
    ax[0].grid(alpha=0.3, axis="y")

    ufs = sorted({k.split("|")[2] for k in R})
    persist = []
    for uf in ufs:
        n = sum(1 for k, v in R.items() if k.split("|")[2] == uf
                and k.split("|")[1] == "18.0" and v["failure_mode"] == "confidently_wrong")
        persist.append(n)
    ax[1].bar(range(len(ufs)), persist, color="#7a0000", alpha=0.85)
    ax[1].set_xticks(range(len(ufs)))
    ax[1].set_xticklabels(ufs, rotation=20, fontsize=8)
    ax[1].set_ylabel("cells still confidently wrong at 18 s")
    ax[1].set_title("Persistent danger at FULL observation.\n"
                    "Every unseen fault has at least one such cell.", fontsize=10)
    ax[1].grid(alpha=0.3, axis="y")
    for i, v in enumerate(persist):
        ax[1].text(i, v + 0.08, str(v), ha="center", fontsize=9)

    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "FIG-015-does-more-data-fix-it.png"), dpi=150)
    plt.close(fig)
    sidecar("FIG-015-does-more-data-fix-it",
            "Does more observation resolve hypothesis-space mismatch, and which unseen "
            "faults remain confidently misdiagnosed at full observation?", res)

    print("wrote FIG-013, FIG-014, FIG-015")


if __name__ == "__main__":
    raise SystemExit(main())
