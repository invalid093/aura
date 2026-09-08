"""
EXP-0011 figures. Three, each answering one question; the redundant candidates listed
in the brief are deliberately not generated.
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
RES = os.path.join(ROOT, "results", "validation", "EXP-0011")
FIG = os.path.join(ROOT, "results", "figures")
COL = {"FC-1": "#1b6ca8", "FC-2": "#e07b39", "FC-3": "#2e8b57", "FC-5": "#8b3a8b"}


def commit():
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True,
                                       stderr=subprocess.DEVNULL).strip()
    except Exception:
        return "unknown"


def sidecar(name, q, res):
    with open(os.path.join(FIG, f"{name}.json"), "w", encoding="utf-8") as fh:
        json.dump({"figure": name, "question_answered": q, "experiment_id": "EXP-0011",
                   "results_file": "results/validation/EXP-0011/exp0011_results.json",
                   "dataset_ids": ["DS-0001", "DS-0002"],
                   "script": "visualization/plot_exp0011.py", "git_commit": commit(),
                   "generated_from_results_utc": res["generated_utc"]}, fh, indent=2)


def main():
    res = json.load(open(os.path.join(RES, "exp0011_results.json"), encoding="utf-8"))
    conds, wins = res["flight_conditions"], res["observation_windows"]
    P = res["P_class"]

    # ------------------------------------------------------------------ FIG-010
    # Q: does unknown magnitude hurt -- and is being UNCERTAIN worse than being WRONG?
    fig, ax = plt.subplots(1, 2, figsize=(12.4, 4.7))

    gapA = [np.mean([P[f"{fc}|{w}|A_known|1.0"] - P[f"{fc}|{w}|C_broad|1.0"]
                     for fc in conds]) for w in wins]
    gapB = [np.mean([P[f"{fc}|{w}|C_broad|1.0"] - P[f"{fc}|{w}|B_bounded|1.0"]
                     for fc in conds]) for w in wins]
    ax[0].plot(wins, gapA, "o-", color="#2e8b57", lw=2.4, ms=6,
               label="cost of NOT KNOWING the magnitude\n(broad prior vs known)")
    ax[0].plot(wins, gapB, "s-", color="#b03060", lw=2.4, ms=6,
               label="cost of being WRONG about it\n(prior that excludes the truth)")
    ax[0].axhline(0, color="k", lw=0.7)
    ax[0].set_xscale("log")
    ax[0].set_xlabel("observation window after fault onset (s)")
    ax[0].set_ylabel("loss in $P_{class}$")
    ax[0].set_title("Being uncertain about magnitude is nearly free.\n"
                    "Being wrong about it is not — and gets WORSE with more data.",
                    fontsize=10)
    ax[0].legend(fontsize=8, loc="center left")
    ax[0].grid(alpha=0.3)
    ax[0].annotate(f"{gapA[-1]:.4f}", (wins[-1], gapA[-1]), fontsize=8,
                   color="#2e8b57", va="bottom", ha="right")
    ax[0].annotate(f"{gapB[-1]:.3f}", (wins[-1], gapB[-1]), fontsize=8,
                   color="#b03060", va="top", ha="right")

    for fc in conds:
        ax[1].plot(wins, [P[f"{fc}|{w}|A_known|1.0"] for w in wins], "-", color=COL[fc],
                   lw=2.2, label=f"{fc} magnitude known")
        ax[1].plot(wins, [P[f"{fc}|{w}|C_broad|1.0"] for w in wins], "--", color=COL[fc],
                   lw=1.5, alpha=0.85)
    ax[1].set_xscale("log")
    ax[1].set_xlabel("observation window after fault onset (s)")
    ax[1].set_ylabel("$P_{class}$")
    ax[1].set_title("Fault-class isolation: magnitude known (solid)\n"
                    "vs unknown over a 16x range (dashed)", fontsize=10)
    ax[1].legend(fontsize=7.5)
    ax[1].grid(alpha=0.3)

    fig.suptitle("EXP-0011  Unknown fault magnitude as a nuisance parameter "
                 "(Bayes-optimal, known template families — an upper bound)", fontsize=11)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "FIG-010-unknown-vs-wrong-magnitude.png"), dpi=150)
    plt.close(fig)
    sidecar("FIG-010-unknown-vs-wrong-magnitude",
            "Does unknown fault magnitude hurt class isolation, and is being uncertain "
            "worse than being wrong?", res)

    # ------------------------------------------------------------------ FIG-011
    # Q: do fault families genuinely overlap, and is the overlap persistent or transient?
    fig, ax = plt.subplots(1, 2, figsize=(12.4, 4.6))
    ml = res["manifold_overlap_window_local"]
    for fc in conds:
        worst = [ml[fc][str(w)]["worst_pairs"][0]["P_disc_worst"] if ml[fc][str(w)]["worst_pairs"]
                 else np.nan for w in wins]
        ax[0].plot(wins, worst, "o-", color=COL[fc], lw=2, ms=5, label=fc)
    ax[0].axhline(0.5, color="grey", ls="-.", lw=1)
    ax[0].annotate("chance", (0.26, 0.512), fontsize=8, color="grey")
    ax[0].axhline(0.99, color="#2e8b57", ls=":", lw=1)
    ax[0].annotate("clearly separated  >0.99", (0.26, 0.965), fontsize=7.5, color="#2e8b57")
    ax[0].axvspan(0.2, 2.0, color="#b03060", alpha=0.06)
    ax[0].annotate("before the manoeuvre", (0.62, 0.62), fontsize=8, color="#b03060",
                   ha="center")
    ax[0].set_xscale("log")
    ax[0].set_xlabel("observation window (s)")
    ax[0].set_ylabel("$P_{disc}$ of the closest VISIBLE class pair")
    ax[0].set_title("Worst-case-magnitude overlap among faults that are\n"
                    "actually visible in the window (post-hoc analysis)", fontsize=10)
    ax[0].legend(fontsize=8, loc="lower right")
    ax[0].grid(alpha=0.3)

    # which pairs overlap, at the shortest window
    pairs, vals, cols = [], [], []
    for fc in conds:
        for p in ml[fc]["0.5"]["worst_pairs"]:
            if p["P_disc_worst"] < 0.99:
                pairs.append(f"{p['a']}/{p['b']}\n{fc}")
                vals.append(p["P_disc_worst"])
                cols.append(COL[fc])
    order = np.argsort(vals)
    ax[1].barh(range(len(vals)), [vals[i] for i in order],
               color=[cols[i] for i in order], alpha=0.85)
    ax[1].set_yticks(range(len(vals)))
    ax[1].set_yticklabels([pairs[i] for i in order], fontsize=7)
    ax[1].axvline(0.5, color="grey", ls="-.", lw=1)
    ax[1].set_xlim(0.4, 1.0)
    ax[1].set_xlabel("$P_{disc}$ (worst-case magnitude)")
    ax[1].set_title("Every overlapping pair at a 0.5 s window is\n"
                    "BIAS vs SCALE on the same channel", fontsize=10)
    ax[1].grid(alpha=0.3, axis="x")

    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "FIG-011-manifold-overlap-transient.png"), dpi=150)
    plt.close(fig)
    sidecar("FIG-011-manifold-overlap-transient",
            "Do fault families overlap when magnitude is free, which pairs, and is the "
            "overlap persistent or transient?", res)

    # ------------------------------------------------------------------ FIG-012
    # Q: which uncertainty source dominates -- noise or unknown magnitude?
    fig, ax = plt.subplots(figsize=(7.2, 4.6))
    etas = res["eta_levels"]
    for case, style, lab in (("A_known", "-", "magnitude known"),
                             ("C_broad", "--", "magnitude unknown (16x range)")):
        v = [np.mean([P[f"{fc}|2.0|{case}|{e}"] for fc in conds]) for e in etas]
        ax.plot(etas, v, style, marker="o", lw=2.2, ms=6, label=lab)
    ax.set_xscale("log")
    ax.set_xlabel(r"effective uncertainty multiplier $\eta$  ($\times$ reference $\sigma$)")
    ax.set_ylabel("$P_{class}$ (mean over conditions, 2 s window)")
    ax.set_title("Measurement noise dominates unknown magnitude —\n"
                 "but the two interact: the magnitude penalty grows with noise",
                 fontsize=10)
    for e in etas:
        a = np.mean([P[f"{fc}|2.0|A_known|{e}"] for fc in conds])
        c = np.mean([P[f"{fc}|2.0|C_broad|{e}"] for fc in conds])
        ax.annotate(f"gap {a-c:.3f}", (e, (a + c) / 2), fontsize=8, ha="center",
                    va="center", color="#b03060")
    ax.legend(fontsize=9)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "FIG-012-noise-vs-magnitude.png"), dpi=150)
    plt.close(fig)
    sidecar("FIG-012-noise-vs-magnitude",
            "Which uncertainty source dominates fault-class isolation: measurement noise "
            "or unknown fault magnitude?", res)

    print("wrote FIG-010, FIG-011, FIG-012")


if __name__ == "__main__":
    raise SystemExit(main())
