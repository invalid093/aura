"""
Deterministic closed-loop simulation harness for EXP-0002.

Fixed-step RK4 with zero-order-hold control, which is the standard discrete
realisation of a digital flight controller and keeps the whole pipeline
deterministic: there is no adaptive step, no random number generation and no
external solver whose version could change a result
(infrastructure/reproducibility.md, assumption A-INF-05).

Loop order per step, matching a real flight computer:
    measure (with fault) -> compute control -> apply actuator fault -> integrate
"""

from __future__ import annotations

import numpy as np

from aircraft.gfw1 import GFW1, N_CHANNELS
from faults.faults import Fault
from simulation.controller import Controller


def simulate(model: GFW1, cfg: dict, x0: np.ndarray, trim_ctrl: np.ndarray,
             trim_info: dict, fault: Fault, dt: float | None = None,
             duration: float | None = None, unseen=None):
    """Run one closed-loop scenario.

    Returns dict with sampled time, measurements, states and controls.
    Measurements are recorded at the configured sensor rate; the integrator runs
    faster, so the recorded signal is a decimation of the continuous one.

    `unseen` (EXP-0012) optionally applies an UNSEEN fault -- a mechanism absent from
    the diagnostic hypothesis library. It is applied AFTER the library fault, and may
    act on the measurements or on the plant's aerodynamic coefficients. The parameter
    defaults to None, so this code path is inert and every prior experiment reproduces
    bit-for-bit; that is verified explicitly in EXP-0012's pilot.
    """
    sim = cfg["simulation"]
    dt = float(sim["dt"] if dt is None else dt)
    duration = float(sim["duration"] if duration is None else duration)
    fs = float(cfg["sensors"]["sample_rate_hz"])

    decim = int(round(1.0 / (fs * dt)))
    if abs(decim * dt * fs - 1.0) > 1e-9:
        raise ValueError(f"sensor rate {fs} Hz is not an integer multiple of 1/dt={1/dt}")

    n_steps = int(round(duration / dt))
    n_samples = n_steps // decim + 1

    t_out = np.empty(n_samples, dtype=np.float64)
    y_out = np.empty((n_samples, N_CHANNELS), dtype=np.float64)
    u_out = np.empty((n_samples, 4), dtype=np.float64)
    x_out = np.empty((n_samples, x0.size), dtype=np.float64)

    ctrl = Controller(cfg, trim_ctrl, trim_info)
    fault.reset()
    if unseen is not None:
        unseen.reset()

    x = x0.astype(np.float64).copy()
    u_applied = trim_ctrl.astype(np.float64).copy()
    diverged = False
    si = 0

    for n in range(n_steps + 1):
        t = n * dt

        # --- an unseen PLANT fault changes the aircraft itself, before forces are computed
        if unseen is not None:
            unseen.apply_plant(model, t)

        # --- measure (fault corrupts what the flight computer sees)
        y_true = model.true_outputs(x, u_applied)
        y_meas = fault.corrupt(y_true, t)
        if unseen is not None:
            y_meas = unseen.corrupt(y_meas, t,
                                    {"rho": model.density(x[11]), "g": model.g})

        # --- control from the faulted measurement, then actuator limits
        u_cmd, v_err = ctrl(t, y_meas, x)
        u_cmd = model.clip_controls(u_cmd)

        # --- actuator fault acts on the plant, after the command is formed
        u_applied = u_cmd.copy()
        u_applied[0] = u_cmd[0] * fault.elevator_gain(t)

        # --- record at sensor rate (measurement is the faulted one, as a
        #     diagnoser would receive it)
        if n % decim == 0 and si < n_samples:
            t_out[si] = t
            y_out[si] = y_meas
            u_out[si] = u_applied
            x_out[si] = x
            si += 1

        if n == n_steps:
            break

        # --- integrate (RK4, zero-order-hold on control)
        k1 = model.derivative(x, u_applied, v_err)
        k2 = model.derivative(x + 0.5 * dt * k1, u_applied, v_err)
        k3 = model.derivative(x + 0.5 * dt * k2, u_applied, v_err)
        k4 = model.derivative(x + dt * k3, u_applied, v_err)
        x = x + (dt / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)

        if not np.all(np.isfinite(x)) or abs(x[11]) > 1e6:
            diverged = True
            break

    return {
        "t": t_out[:si],
        "y": y_out[:si],
        "u": u_out[:si],
        "x": x_out[:si],
        "diverged": diverged,
        "n_samples": si,
        "dt": dt,
        "duration": duration,
        "fault_id": fault.fault_id,
    }
