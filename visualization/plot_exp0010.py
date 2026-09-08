"""
EXP-0010 figures.

Three figures, each answering one question. Figures the brief lists that would be
redundant with these are deliberately not generated (brief §18).
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
RES = os.path.join(ROOT, "results", "validation", "EXP-0010")
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
        json.dump({"figure": name, "question_answered": q, "experiment_id": "EXP-0010",
                   "results_file": "results/validation/EXP-0010/exp0010_results.json",
                   "dataset_ids": ["DS-0001"], "script": "visualization/plot_exp0010.py",
                   "git_commit": commit(),
                   "generated_from_results_utc": res["generated_utc"]}, fh, indent=2)


def main():
    res = json.load(open(os.path.join(RES, "exp0010_results.json"), encoding="utf-8"))
    conds, wins, etas = res["flight_conditions"], res["observation_windows"], res["eta_levels"]
    P, ids = res["P_iso"], res["fault_ids"]

    # ------------------------------------------------------------------ FIG-004
    # Q: what actually limits isolation -- noise level, or observation window?
    fig, ax = plt.subplots(1, 2, figsize=(12.4, 4.7))

    for fc in conds:
        for e, ls, a in ((1.0, "-", 1.0), (10.0, "--", 0.9), (50.0, ":", 0.8)):
            ax[0].plot(wins, [P[f"{fc}|{w}|{e}"] for w in wins], ls, color=COL[fc],
                       alpha=a, lw=2 if e == 1.0 else 1.5,
                       label=f"{fc}, $\\eta$={e:g}" if fc == "FC-1" or e == 1.0 else None)
    ax[0].axhline(0.95, color="k", ls="-.", lw=1)
    ax[0].annotate("$P_{iso}=0.95$", (0.06, 0.965), fontsize=8)
    ax[0].set_xscale("log")
    ax[0].set_xlabel("observation window after fault onset (s)")
    ax[0].set_ylabel("$P_{iso}$  (18-way correct isolation)")
    ax[0].set_title("Isolation is limited by TIME, not by noise\n"
                    "(at the reference spec $\\eta$=1, isolation needs ~5 s)", fontsize=10)
    ax[0].legend(fontsize=7, ncol=2, loc="lower right")
    ax[0].grid(alpha=0.3)
    ax[0].set_ylim(0, 1.03)

    for fc in conds:
        ax[1].plot(etas, [P[f"{fc}|18.0|{e}"] for e in etas], "o-", color=COL[fc],
                   lw=2, label=fc, ms=4)
    ax[1].axhline(0.95, color="k", ls="-.", lw=1)
    ax[1].axvspan(1, 5, color="#2e8b57", alpha=0.08)
    ax[1].annotate("realistic\nsensor range", (2.2, 0.30), fontsize=8, ha="center",
                   color="#2e8b57")
    ax[1].annotate("experimental stress levels\n(proxy for total effective uncertainty)",
                   (120, 0.30), fontsize=8, ha="center", color="#7a0000")
    ax[1].set_xscale("log")
    ax[1].set_xlabel(r"effective uncertainty multiplier $\eta$  ($\times$ reference $\sigma$)")
    ax[1].set_ylabel("$P_{iso}$")
    ax[1].set_title("Full 18 s window: noise must be ~10–19$\\times$ spec\n"
                    "before isolation degrades below 0.95", fontsize=10)
    ax[1].legend(fontsize=8)
    ax[1].grid(alpha=0.3)
    ax[1].set_ylim(0, 1.03)

    fig.suptitle("EXP-0010  Practical fault isolation under measurement uncertainty "
                 "(Bayes-optimal, known templates — an UPPER BOUND)", fontsize=11)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "FIG-004-isolation-vs-noise-and-window.png"), dpi=150)
    plt.close(fig)
    sidecar("FIG-004-isolation-vs-noise-and-window",
            "What limits fault isolation: noise level or observation window?", res)

    # ------------------------------------------------------------------ FIG-005
    # Q: does the EXP-0002 ambiguity group predict which faults fail first under noise?
    grp = ["F0", "F2_q", "F2_alpha", "F4_alpha", "F4_Vt"]
    fig, ax = plt.subplots(figsize=(7.6, 4.8))
    for j, f in enumerate(ids):
        y = [res["per_fault_P_iso"][f"FC-1|18.0|{e}"][j] for e in etas]
        if f in grp:
            ax.plot(etas, y, "o-", lw=2.2, ms=4.5, label=f"{f}  (EXP-0002 group)", zorder=3)
        else:
            ax.plot(etas, y, "-", color="#b8b8b8", lw=1, alpha=0.8, zorder=1,
                    label="other 13 faults" if j == 1 else None)
    ax.set_xscale("log")
    ax.set_xlabel(r"effective uncertainty multiplier $\eta$")
    ax.set_ylabel("per-fault $P_{iso}$")
    ax.set_title("EXP-0002's five-member ambiguity group, identified with NO noise model,\n"
                 "is exactly the set that degrades first under uncertainty (FC-1)", fontsize=10)
    ax.legend(fontsize=8, loc="lower left")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "FIG-005-ambiguity-group-under-noise.png"), dpi=150)
    plt.close(fig)
    sidecar("FIG-005-ambiguity-group-under-noise",
            "Does the deterministic EXP-0002 ambiguity group predict which faults "
            "degrade first under measurement uncertainty?", res)

    # ------------------------------------------------------------------ FIG-006
    # Q: do the two closed-form predictions survive contact with uncertainty?
    fig, ax = plt.subplots(1, 2, figsize=(11.6, 4.4))

    a = res["analytic_prediction"]
    pr = [a[fc]["eta95_predicted"] for fc in conds]
    me = [a[fc]["eta95_measured"] for fc in conds]
    for fc, x, y in zip(conds, pr, me):
        ax[0].plot(x, y, "o", color=COL[fc], ms=9, label=f"{fc} ($V_0$={a[fc]['V0']:.0f} m/s)")
    lim = [0, max(me) * 1.15]
    ax[0].plot(lim, lim, "k--", lw=1, label="perfect prediction")
    ax[0].plot(lim, [2 * v for v in lim], color="grey", ls=":", lw=1,
               label=r"2$\times$ (analytic is conservative)")
    ax[0].set_xlim(lim); ax[0].set_ylim(lim)
    ax[0].set_xlabel(r"$\eta_{95}$ predicted by the closed form (V$_t$ channel only)")
    ax[0].set_ylabel(r"$\eta_{95}$ measured (all 13 channels)")
    ax[0].set_title(f"EXP-0002's closed-form bias/scale prediction\n"
                    f"still ranks correctly under noise (r = "
                    f"{res['analytic_prediction_pearson_r']:.3f})", fontsize=10)
    ax[0].legend(fontsize=7.5)
    ax[0].grid(alpha=0.3)

    nd = res["validity"]["noise_distribution"]
    keys = list(nd.keys())
    white = [nd[k]["gaussian"] for k in keys]
    ar1 = [nd[k]["ar1"] for k in keys]
    t4 = [nd[k]["student_t"] for k in keys]
    ax[1].plot(white, t4, "s", color="#2e8b57", ms=7, label="Student-t($\\nu$=4)")
    ax[1].plot(white, ar1, "o", color="#b03060", ms=7, label="AR(1), $\\rho$=0.5")
    lim2 = [0, max(white) * 1.15]
    ax[1].plot(lim2, lim2, "k--", lw=1, label="no change vs white Gaussian")
    ax[1].set_xlim(lim2); ax[1].set_ylim(lim2)
    ax[1].set_xlabel("$P_{iso}$ under white Gaussian noise")
    ax[1].set_ylabel("$P_{iso}$ under the alternative noise model")
    ax[1].set_title("Heavy tails: no effect.  Temporal correlation: 21% loss,\n"
                    r"quantitatively explained by $\sqrt{(1+\rho)/(1-\rho)}$ (r = 0.999)",
                    fontsize=10)
    ax[1].legend(fontsize=8)
    ax[1].grid(alpha=0.3)

    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "FIG-006-predictions-and-noise-models.png"), dpi=150)
    plt.close(fig)
    sidecar("FIG-006-predictions-and-noise-models",
            "Do the closed-form predictions survive noise, and does the conclusion "
            "survive non-Gaussian and temporally correlated noise?", res)

    print("wrote FIG-004, FIG-005, FIG-006")


if __name__ == "__main__":
    raise SystemExit(main())
