"""
GFW-1 -- generic fixed-wing 6-DOF aircraft model.

Nonlinear rigid-body flight dynamics with coefficient-form aerodynamics and a
blended stall model. Every parameter comes from configuration
(experiments/EXP-0002/config/exp0002.yaml); nothing physical is hard-coded here.

SCOPE (assumption A-SIM-01, extended by ADR-0007)
    GFW-1 is a *generic, representative* fixed-wing aircraft. It is not a model of
    any specific validated airframe. No result computed with it licenses a claim
    about a real aircraft.

Simplifications, each recorded in docs/assumptions.md:
    A-SIM-02  rigid body; no aeroelasticity
    A-SIM-04  no wind or turbulence
    A-SIM-05  algebraic actuators (no lag); position limits only
    A-SIM-06  fixed-step RK4 (step-size convergence checked in EXP-0002 S-A)

State vector (13):
    0  u      body-axis forward velocity      m/s
    1  v      body-axis lateral velocity      m/s
    2  w      body-axis normal velocity       m/s
    3  p      roll rate                       rad/s
    4  q      pitch rate                      rad/s
    5  r      yaw rate                        rad/s
    6  phi    roll angle                      rad
    7  theta  pitch angle                     rad
    8  psi    yaw angle                       rad
    9  pn     north position                  m
    10 pe     east position                   m
    11 h      altitude (positive up)          m
    12 xi     autothrottle integral state     m (integral of m/s)

Control vector (4): [de, da, dr, throttle], rad and [0,1].
"""

from __future__ import annotations

import numpy as np

# State indices
U, V, W, P, Q, R, PHI, THETA, PSI, PN, PE, H, XI = range(13)
N_STATES = 13

# Measurement channel order -- must match config sensors.channels
CHANNELS = ["p", "q", "r", "ax", "ay", "az", "Vt", "alpha", "beta", "h", "phi", "theta", "psi"]
N_CHANNELS = len(CHANNELS)


class GFW1:
    """Nonlinear 6-DOF fixed-wing model. Stateless: all methods are pure functions."""

    def __init__(self, cfg: dict):
        a = cfg["aircraft"]
        env = cfg["environment"]
        self.p = dict(a)
        self.g = float(env["g"])
        self.rho0 = float(env["rho0"])
        self.isa_k = float(env["isa_lapse_coeff"])
        self.isa_n = float(env["isa_exponent"])

        self.m = float(a["mass"])
        self.S = float(a["S"])
        self.b = float(a["b"])
        self.c = float(a["c"])
        self.T_max = float(a["T_max"])
        self.AR = self.b ** 2 / self.S
        self.k_induced = 1.0 / (np.pi * float(a["e_oswald"]) * self.AR)

        # Inertia coupling terms (standard Gamma formulation for a body with Jxz)
        Jx, Jy, Jz, Jxz = (float(a["Jx"]), float(a["Jy"]), float(a["Jz"]), float(a["Jxz"]))
        G = Jx * Jz - Jxz ** 2
        self.Jy = Jy
        self.G1 = Jxz * (Jx - Jy + Jz) / G
        self.G2 = (Jz * (Jz - Jy) + Jxz ** 2) / G
        self.G3 = Jz / G
        self.G4 = Jxz / G
        self.G5 = (Jz - Jx) / Jy
        self.G6 = Jxz / Jy
        self.G7 = ((Jx - Jy) * Jx + Jxz ** 2) / G
        self.G8 = Jx / G

        lim = cfg["actuator"]
        self.lim = {k: float(vv) for k, vv in lim.items()}

    # ---------------------------------------------------------------- atmosphere
    def density(self, h: float) -> float:
        """ISA troposphere density. Clamped at the model's validity floor."""
        base = max(1.0 - self.isa_k * h, 1e-6)
        return self.rho0 * base ** self.isa_n

    # ---------------------------------------------------------------- aerodynamics
    def lift_coefficient(self, alpha: float) -> float:
        """Blended linear/flat-plate lift model.

        Below the blend region this is the linear CL0 + CLa*alpha. Beyond it the
        model transitions to a flat-plate form so that lift saturates rather than
        growing without bound. The blend is the standard sigmoid of
        Beard & McLain form; it is what makes the model genuinely nonlinear in
        alpha, which is the physical mechanism EXP-0002 depends on.
        """
        M = float(self.p["stall_M"])
        a0 = float(self.p["stall_a0"])
        # Guard the exponentials against overflow at extreme alpha
        e_neg = np.exp(np.clip(-M * (alpha - a0), -60.0, 60.0))
        e_pos = np.exp(np.clip(M * (alpha + a0), -60.0, 60.0))
        sigma = (1.0 + e_neg + e_pos) / ((1.0 + e_neg) * (1.0 + e_pos))
        cl_lin = float(self.p["CL0"]) + float(self.p["CLa"]) * alpha
        cl_flat = 2.0 * np.sign(alpha) * (np.sin(alpha) ** 2) * np.cos(alpha)
        return (1.0 - sigma) * cl_lin + sigma * cl_flat

    def forces_moments(self, x: np.ndarray, u_ctrl: np.ndarray):
        """Aerodynamic + propulsive forces (body axes) and moments.

        Returns (X, Y, Z, L, M, N, Vt, alpha, beta, qbar).
        """
        u, v, w = x[U], x[V], x[W]
        p, q, r = x[P], x[Q], x[R]
        de, da, dr, thr = u_ctrl

        Vt = float(np.sqrt(u * u + v * v + w * w))
        Vt = max(Vt, 1e-3)                       # avoid division by zero at rest
        alpha = float(np.arctan2(w, u))
        beta = float(np.arcsin(np.clip(v / Vt, -1.0, 1.0)))

        rho = self.density(x[H])
        qbar = 0.5 * rho * Vt * Vt
        qS = qbar * self.S

        # Non-dimensional rate terms
        c2V = self.c / (2.0 * Vt)
        b2V = self.b / (2.0 * Vt)

        CL = (self.lift_coefficient(alpha)
              + float(self.p["CLq"]) * c2V * q
              + float(self.p["CLde"]) * de)

        # Drag: parasite + induced, induced computed from the LINEAR lift term so
        # that the drag polar stays physical through the stall blend.
        cl_lin = float(self.p["CL0"]) + float(self.p["CLa"]) * alpha
        CD = (float(self.p["CD0"]) + self.k_induced * cl_lin ** 2
              + float(self.p["CDde"]) * abs(de))

        CY = (float(self.p["CYb"]) * beta
              + float(self.p["CYp"]) * b2V * p
              + float(self.p["CYr"]) * b2V * r
              + float(self.p["CYda"]) * da
              + float(self.p["CYdr"]) * dr)

        Cl = (float(self.p["Clb"]) * beta
              + float(self.p["Clp"]) * b2V * p
              + float(self.p["Clr"]) * b2V * r
              + float(self.p["Clda"]) * da
              + float(self.p["Cldr"]) * dr)

        Cm = (float(self.p["Cm0"])
              + float(self.p["Cma"]) * alpha
              + float(self.p["Cmq"]) * c2V * q
              + float(self.p["Cmde"]) * de)

        Cn = (float(self.p["Cnb"]) * beta
              + float(self.p["Cnp"]) * b2V * p
              + float(self.p["Cnr"]) * b2V * r
              + float(self.p["Cnda"]) * da
              + float(self.p["Cndr"]) * dr)

        # Lift and drag act in stability axes; rotate into body axes.
        ca, sa = np.cos(alpha), np.sin(alpha)
        thrust = self.T_max * thr
        X = qS * (-CD * ca + CL * sa) + thrust
        Y = qS * CY
        Z = qS * (-CD * sa - CL * ca)

        Lm = qS * self.b * Cl
        Mm = qS * self.c * Cm
        Nm = qS * self.b * Cn
        return X, Y, Z, Lm, Mm, Nm, Vt, alpha, beta, qbar

    # ---------------------------------------------------------------- dynamics
    def derivative(self, x: np.ndarray, u_ctrl: np.ndarray, v_err: float) -> np.ndarray:
        """State derivative. `v_err` drives the autothrottle integral state."""
        X, Y, Z, Lm, Mm, Nm, _, _, _, _ = self.forces_moments(x, u_ctrl)

        u, v, w = x[U], x[V], x[W]
        p, q, r = x[P], x[Q], x[R]
        phi, theta, psi = x[PHI], x[THETA], x[PSI]

        cphi, sphi = np.cos(phi), np.sin(phi)
        cth, sth = np.cos(theta), np.sin(theta)
        cpsi, spsi = np.cos(psi), np.sin(psi)
        cth = cth if abs(cth) > 1e-6 else np.sign(cth) * 1e-6   # gimbal guard

        dx = np.zeros(N_STATES, dtype=np.float64)

        # Translational (body axes, gravity resolved from Euler angles)
        dx[U] = r * v - q * w - self.g * sth + X / self.m
        dx[V] = p * w - r * u + self.g * cth * sphi + Y / self.m
        dx[W] = q * u - p * v + self.g * cth * cphi + Z / self.m

        # Rotational, with full Jxz coupling
        dx[P] = self.G1 * p * q - self.G2 * q * r + self.G3 * Lm + self.G4 * Nm
        dx[Q] = self.G5 * p * r - self.G6 * (p * p - r * r) + Mm / self.Jy
        dx[R] = self.G7 * p * q - self.G1 * q * r + self.G4 * Lm + self.G8 * Nm

        # Euler kinematics
        tth = sth / cth
        dx[PHI] = p + sphi * tth * q + cphi * tth * r
        dx[THETA] = cphi * q - sphi * r
        dx[PSI] = (sphi * q + cphi * r) / cth

        # Navigation
        dx[PN] = (u * cth * cpsi
                  + v * (sphi * sth * cpsi - cphi * spsi)
                  + w * (cphi * sth * cpsi + sphi * spsi))
        dx[PE] = (u * cth * spsi
                  + v * (sphi * sth * spsi + cphi * cpsi)
                  + w * (cphi * sth * spsi - sphi * cpsi))
        dx[H] = u * sth - v * sphi * cth - w * cphi * cth

        # Autothrottle integral
        dx[XI] = v_err
        return dx

    # ---------------------------------------------------------------- measurement
    def true_outputs(self, x: np.ndarray, u_ctrl: np.ndarray) -> np.ndarray:
        """Fault-free sensor outputs, in CHANNELS order.

        Accelerometers report non-gravitational specific force, which is the
        physically correct quantity: gravity does not appear.
        """
        X, Y, Z, _, _, _, Vt, alpha, beta, _ = self.forces_moments(x, u_ctrl)
        y = np.empty(N_CHANNELS, dtype=np.float64)
        y[0] = x[P]
        y[1] = x[Q]
        y[2] = x[R]
        y[3] = X / self.m
        y[4] = Y / self.m
        y[5] = Z / self.m
        y[6] = Vt
        y[7] = alpha
        y[8] = beta
        y[9] = x[H]
        y[10] = x[PHI]
        y[11] = x[THETA]
        y[12] = x[PSI]
        return y

    def clip_controls(self, u_ctrl: np.ndarray) -> np.ndarray:
        out = np.empty(4, dtype=np.float64)
        out[0] = np.clip(u_ctrl[0], self.lim["de_min"], self.lim["de_max"])
        out[1] = np.clip(u_ctrl[1], self.lim["da_min"], self.lim["da_max"])
        out[2] = np.clip(u_ctrl[2], self.lim["dr_min"], self.lim["dr_max"])
        out[3] = np.clip(u_ctrl[3], self.lim["throttle_min"], self.lim["throttle_max"])
        return out
