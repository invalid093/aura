"""
Trim solver for GFW-1.

Finds steady, wings-level, unaccelerated flight at a commanded airspeed and
altitude by solving a 3x3 nonlinear system in (alpha, elevator, throttle).

Implemented with a damped Newton iteration and a numerical Jacobian rather than
scipy, so that the result is deterministic and does not depend on an external
solver's version or tolerances (infrastructure/reproducibility.md).
"""

from __future__ import annotations

import numpy as np

from aircraft.gfw1 import GFW1, N_STATES, U, V, W, H, THETA


def _residual(model: GFW1, z: np.ndarray, Vt: float, h: float) -> np.ndarray:
    """Residual of the trim conditions: [udot, wdot, qdot] at the candidate point.

    z = [alpha, de, throttle]. Level flight is imposed by setting theta = alpha
    (flight-path angle zero), v = 0 and p = q = r = 0.
    """
    alpha, de, thr = z
    x = np.zeros(N_STATES, dtype=np.float64)
    x[U] = Vt * np.cos(alpha)
    x[V] = 0.0
    x[W] = Vt * np.sin(alpha)
    x[THETA] = alpha
    x[H] = h
    u_ctrl = np.array([de, 0.0, 0.0, thr], dtype=np.float64)
    dx = model.derivative(x, u_ctrl, 0.0)
    return np.array([dx[0], dx[2], dx[4]], dtype=np.float64)   # udot, wdot, qdot


def trim(model: GFW1, Vt: float, h: float,
         z0=(0.05, 0.0, 0.5), tol: float = 1e-11, max_iter: int = 200):
    """Solve for trim. Returns (state, controls, info).

    Raises RuntimeError if the residual does not converge -- a failed trim is a
    hard error, never silently accepted, because every downstream result would
    inherit the offset.
    """
    z = np.array(z0, dtype=np.float64)
    eps = 1e-7
    res_norm = np.inf

    for it in range(max_iter):
        f0 = _residual(model, z, Vt, h)
        res_norm = float(np.linalg.norm(f0))
        if res_norm < tol:
            break
        # Numerical Jacobian (central differences)
        J = np.zeros((3, 3), dtype=np.float64)
        for j in range(3):
            zp, zm = z.copy(), z.copy()
            zp[j] += eps
            zm[j] -= eps
            J[:, j] = (_residual(model, zp, Vt, h) - _residual(model, zm, Vt, h)) / (2.0 * eps)
        try:
            step = np.linalg.solve(J, -f0)
        except np.linalg.LinAlgError as exc:                     # pragma: no cover
            raise RuntimeError(f"trim Jacobian singular at Vt={Vt}, h={h}") from exc

        # Damped update: backtrack until the residual actually decreases.
        lam = 1.0
        for _ in range(40):
            z_new = z + lam * step
            if np.linalg.norm(_residual(model, z_new, Vt, h)) < res_norm:
                break
            lam *= 0.5
        z = z + lam * step

    if res_norm >= tol:
        raise RuntimeError(
            f"trim failed to converge at Vt={Vt} m/s, h={h} m: residual={res_norm:.3e}")

    alpha, de, thr = z
    x = np.zeros(N_STATES, dtype=np.float64)
    x[U] = Vt * np.cos(alpha)
    x[W] = Vt * np.sin(alpha)
    x[THETA] = alpha
    x[H] = h
    u_ctrl = np.array([de, 0.0, 0.0, thr], dtype=np.float64)

    y = model.true_outputs(x, u_ctrl)
    info = {
        "alpha_rad": float(alpha),
        "alpha_deg": float(np.degrees(alpha)),
        "de_rad": float(de),
        "de_deg": float(np.degrees(de)),
        "throttle": float(thr),
        "Vt": float(Vt),
        "altitude_m": float(h),
        "rho": float(model.density(h)),
        "qbar_Pa": float(0.5 * model.density(h) * Vt * Vt),
        "az_trim": float(y[5]),
        "residual_norm": res_norm,
        "iterations": it,
    }
    return x, u_ctrl, info
