"""
EXP-0002 pilot verification (experiment_spec.md; brief section 8).

Technical verification ONLY. Nothing here is scientific evidence for or against
the hypothesis -- it checks that the machinery works before the full run.

Checks:
  1. trim converges at every flight condition, with physically sensible values
  2. nominal closed-loop run is stable and tracks the excitation
  3. fault injection actually perturbs the intended channel
  4. units are as declared
  5. distance metric behaves (d(i,i)=0, symmetry, non-negativity)
  6. matrix construction is well-formed
  7. bitwise reproducibility of a repeated run
  8. runtime and storage measured
"""

from __future__ import annotations

import hashlib
import os
import sys
import time

import numpy as np
import yaml

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from aircraft.gfw1 import GFW1, CHANNELS                       # noqa: E402
from aircraft.trim import trim                                 # noqa: E402
from faults.faults import Fault                                # noqa: E402
from simulation.simulate import simulate                       # noqa: E402
from analysis.isolability import distance_matrix               # noqa: E402

CFG_PATH = os.path.join(os.path.dirname(__file__), "config", "exp0002.yaml")
FAIL = []


def check(name, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    if not condition:
        FAIL.append(name)
    print(f"  [{status}] {name}" + (f"  --  {detail}" if detail else ""))


def main():
    with open(CFG_PATH, "r", encoding="utf-8") as fh:
        cfg = yaml.safe_load(fh)
    model = GFW1(cfg)

    print("=" * 78)
    print("EXP-0002 PILOT VERIFICATION")
    print("=" * 78)

    # ---------------------------------------------------------------- 1. trim
    print("\n1. TRIM CONVERGENCE AND PHYSICAL PLAUSIBILITY")
    trims = {}
    for fc in cfg["flight_conditions"]:
        try:
            x0, u0, info = trim(model, fc["airspeed_mps"], fc["altitude_m"])
        except RuntimeError as exc:
            check(f"trim {fc['id']}", False, str(exc))
            continue
        trims[fc["id"]] = (x0, u0, info)
        print(f"   {fc['id']}: h={info['altitude_m']:6.0f} m  V={info['Vt']:5.1f} m/s  "
              f"rho={info['rho']:.4f}  qbar={info['qbar_Pa']:7.1f} Pa  "
              f"alpha={info['alpha_deg']:6.2f} deg  de={info['de_deg']:6.2f} deg  "
              f"thr={info['throttle']:.3f}  az={info['az_trim']:7.3f}  "
              f"res={info['residual_norm']:.1e}")
        check(f"trim {fc['id']} converged", info["residual_norm"] < 1e-10)
        check(f"trim {fc['id']} alpha in [-10,25] deg", -10 < info["alpha_deg"] < 25,
              f"{info['alpha_deg']:.2f} deg")
        check(f"trim {fc['id']} throttle in (0,1)", 0.0 < info["throttle"] < 1.0,
              f"{info['throttle']:.3f}")
        check(f"trim {fc['id']} az near -g", abs(info["az_trim"] + cfg["environment"]["g"]) < 0.5,
              f"{info['az_trim']:.3f} m/s^2")

    if not trims:
        print("\nABORT: no trim converged.")
        return 1

    # distinct regimes?
    qbars = [t[2]["qbar_Pa"] for t in trims.values()]
    alphas = [t[2]["alpha_deg"] for t in trims.values()]
    check("flight conditions span dynamic pressure", max(qbars) / min(qbars) > 2.0,
          f"qbar range {min(qbars):.0f}-{max(qbars):.0f} Pa")
    check("flight conditions span trim alpha", max(alphas) - min(alphas) > 5.0,
          f"alpha range {min(alphas):.1f} to {max(alphas):.1f} deg")

    # ------------------------------------------------------- 2. nominal run
    print("\n2. NOMINAL CLOSED-LOOP RUN (FC-1)")
    fc_id = cfg["flight_conditions"][0]["id"]
    x0, u0, info = trims[fc_id]
    f0 = Fault("F0", None, cfg)
    t_start = time.perf_counter()
    run0 = simulate(model, cfg, x0, u0, info, f0)
    runtime = time.perf_counter() - t_start

    y = run0["y"]
    th_idx = CHANNELS.index("theta")
    q_idx = CHANNELS.index("q")
    check("nominal run did not diverge", not run0["diverged"])
    check("nominal run sample count", run0["n_samples"] == 2001, str(run0["n_samples"]))
    check("all outputs finite", bool(np.all(np.isfinite(y))))
    theta_dev = np.degrees(y[:, th_idx] - info["alpha_rad"])
    check("excitation moves pitch attitude", np.ptp(theta_dev) > 2.0,
          f"theta swing {np.ptp(theta_dev):.2f} deg")
    check("closed loop stays bounded", np.max(np.abs(theta_dev)) < 30.0,
          f"max |dtheta| {np.max(np.abs(theta_dev)):.2f} deg")
    check("pitch rate excited (needed for scale faults)",
          np.max(np.abs(y[:, q_idx])) > 5 * cfg["sensors"]["sigma"]["q"],
          f"max |q| {np.max(np.abs(y[:, q_idx])):.4f} rad/s")
    check("airspeed regulated", np.max(np.abs(y[:, CHANNELS.index('Vt')] - info["Vt"])) < 5.0,
          f"max dV {np.max(np.abs(y[:, CHANNELS.index('Vt')] - info['Vt'])):.2f} m/s")
    check("lateral states remain zero (symmetric excitation)",
          np.max(np.abs(y[:, CHANNELS.index('phi')])) < 1e-9,
          f"max |phi| {np.max(np.abs(y[:, CHANNELS.index('phi')])):.2e} rad")
    print(f"   runtime {runtime:.3f} s/run   samples {run0['n_samples']}")

    # --------------------------------------------------- 3. fault injection
    print("\n3. FAULT INJECTION VERIFICATION")
    onset = cfg["simulation"]["fault_onset"]
    sig = cfg["sensors"]["sigma"]

    for mode, ch in (("F1", "q"), ("F2", "Vt"), ("F3", "alpha"), ("F4", "az")):
        f = Fault(mode, ch, cfg)
        run = simulate(model, cfg, x0, u0, info, f)
        k = CHANNELS.index(ch)
        pre = run["t"] < onset
        post = run["t"] >= onset
        d_pre = np.max(np.abs(run["y"][pre, k] - run0["y"][pre, k]))
        d_post = np.max(np.abs(run["y"][post, k] - run0["y"][post, k]))
        check(f"{mode}_{ch} inert before onset", d_pre < 1e-12, f"{d_pre:.2e}")
        check(f"{mode}_{ch} perturbs {ch} after onset", d_post > 0.5 * sig[ch],
              f"max dev {d_post:.4g} ({d_post/sig[ch]:.1f} sigma)")

    # F1 bias magnitude must equal exactly 10 sigma at the corrupted channel
    f1 = Fault("F1", "q", cfg)
    r1 = simulate(model, cfg, x0, u0, info, f1)
    check("F1 bias magnitude == 10 sigma as configured",
          abs(f1.bias - 10.0 * sig["q"]) < 1e-15, f"bias={f1.bias:.6e}")

    # F6 must NOT corrupt any measurement directly, only via the plant
    f6 = Fault("F6", None, cfg)
    r6 = simulate(model, cfg, x0, u0, info, f6)
    pre = r6["t"] < onset
    check("F6 inert before onset", np.max(np.abs(r6["y"][pre] - run0["y"][pre])) < 1e-12)
    check("F6 changes trajectory after onset",
          np.max(np.abs(r6["y"][r6["t"] >= onset] - run0["y"][r6["t"] >= onset])) > 0,
          "actuator fault propagates through plant")

    # ------------------------------------------------------------ 4. units
    print("\n4. UNIT VERIFICATION")
    check("alpha in radians (trim < 0.5 rad)", abs(info["alpha_rad"]) < 0.5,
          f"{info['alpha_rad']:.4f} rad")
    check("Vt in m/s", abs(y[0, CHANNELS.index("Vt")] - info["Vt"]) < 1e-9)
    check("h in metres", abs(y[0, CHANNELS.index("h")] - info["altitude_m"]) < 1e-9)
    check("az is specific force, not including gravity",
          abs(y[0, CHANNELS.index("az")] + cfg["environment"]["g"]) < 0.5,
          f"{y[0, CHANNELS.index('az')]:.3f} m/s^2")

    # ------------------------------------------- 5/6. metric and matrix
    print("\n5. DISTANCE METRIC AND MATRIX CONSTRUCTION")
    runs = {"F0": run0, "F1_q": r1, "F6": r6}
    ids, D = distance_matrix(runs, cfg)
    check("matrix is square", D.shape == (3, 3))
    check("diagonal is zero", bool(np.allclose(np.diag(D), 0.0)))
    check("matrix is symmetric", bool(np.allclose(D, D.T)))
    check("distances non-negative", bool(np.all(D >= 0)))
    ids_s, D_s = distance_matrix({"a": run0, "b": run0}, cfg)
    check("identical runs give d = 0", D_s[0, 1] < 1e-15, f"{D_s[0,1]:.2e}")
    print(f"   d(F0,F1_q)={D[0,1]:.3f}  d(F0,F6)={D[0,2]:.3f}  d(F1_q,F6)={D[1,2]:.3f}")

    # ---------------------------------------------------- 7. reproducibility
    print("\n6. REPRODUCIBILITY")
    run0b = simulate(model, cfg, x0, u0, info, Fault("F0", None, cfg))
    h1 = hashlib.sha256(run0["y"].tobytes()).hexdigest()
    h2 = hashlib.sha256(run0b["y"].tobytes()).hexdigest()
    check("repeated run is bitwise identical", h1 == h2, h1[:16])

    # ------------------------------------------------- 8. runtime / storage
    print("\n7. RUNTIME AND STORAGE")
    bytes_per_run = run0["y"].nbytes + run0["u"].nbytes + run0["x"].nbytes + run0["t"].nbytes
    n_runs_full = len(cfg["flight_conditions"]) * 18
    print(f"   runtime/run      {runtime:.3f} s")
    print(f"   storage/run      {bytes_per_run/1024:.1f} KiB (float64, uncompressed)")
    print(f"   full experiment  {n_runs_full} runs -> "
          f"{n_runs_full*runtime:.1f} s, {n_runs_full*bytes_per_run/1024/1024:.1f} MiB")

    print("\n" + "=" * 78)
    if FAIL:
        print(f"PILOT VERIFICATION: {len(FAIL)} CHECK(S) FAILED")
        for f in FAIL:
            print(f"   - {f}")
        return 1
    print("PILOT VERIFICATION: ALL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
