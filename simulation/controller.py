"""
Closed-loop flight controller for EXP-0002.

A stabilising controller is REQUIRED for this experiment rather than incidental.
In open loop a sensor fault never reaches the plant, so it would appear in exactly
one measurement channel and sensor-versus-actuator ambiguity could not arise at
all. Closing the loop through the four faulted channels (q, az, Vt, alpha) is what
makes the ambiguity question physically meaningful.

Structure: longitudinal pitch SAS with attitude, rate, angle-of-attack and normal
specific-force feedback, plus a PI autothrottle; lateral wings-leveller with roll
and yaw damping.

Gains are FIXED across all flight conditions -- no gain scheduling. Any difference
observed between conditions is therefore a property of the aircraft, not of a
controller that was retuned.

Sign conventions (Cmde < 0, i.e. positive elevator gives a nose-down moment):
    positive pitch error (theta_cmd > theta)  ->  negative elevator  (nose up)
    positive pitch rate                        ->  positive elevator  (damping)
    alpha above trim                           ->  positive elevator  (nose down)
    az below trim (pulling up)                 ->  positive elevator  (nose down)
"""

from __future__ import annotations

import numpy as np

from aircraft.gfw1 import XI


class Controller:
    def __init__(self, cfg: dict, trim_ctrl: np.ndarray, trim_info: dict):
        c = cfg["controller"]
        self.Kq = float(c["K_q"])
        self.Kth = float(c["K_theta"])
        self.Kal = float(c["K_alpha"])
        self.Kaz = float(c["K_az"])
        self.KV = float(c["K_V"])
        self.KVi = float(c["K_Vi"])
        self.Kphi = float(c["K_phi"])
        self.Kp = float(c["K_p"])
        self.Kr = float(c["K_r"])

        self.de_trim = float(trim_ctrl[0])
        self.thr_trim = float(trim_ctrl[3])
        self.theta_trim = float(trim_info["alpha_rad"])       # level flight: theta = alpha
        self.alpha_trim = float(trim_info["alpha_rad"])
        self.az_trim = float(trim_info["az_trim"])
        self.Vt_cmd = float(trim_info["Vt"])

        ex = cfg["excitation"]
        self.amp = np.radians(float(ex["amplitude_deg"]))
        self.t1 = float(ex["t1"])
        self.t2 = float(ex["t2"])
        self.t3 = float(ex["t3"])

    def theta_command(self, t: float) -> float:
        """Pitch-attitude doublet, identical at every flight condition."""
        if self.t1 <= t < self.t2:
            return self.theta_trim + self.amp
        if self.t2 <= t < self.t3:
            return self.theta_trim - self.amp
        return self.theta_trim

    def __call__(self, t: float, y_meas: np.ndarray, x: np.ndarray):
        """Return (controls, v_err).

        `y_meas` is the FAULTED measurement vector -- the controller sees exactly
        what a real flight computer would see, which is the point.
        `x` supplies only the autothrottle integral state.
        """
        p, q, r = y_meas[0], y_meas[1], y_meas[2]
        az = y_meas[5]
        Vt = y_meas[6]
        alpha = y_meas[7]
        phi, theta = y_meas[10], y_meas[11]

        theta_cmd = self.theta_command(t)

        de = (self.de_trim
              + self.Kq * q
              - self.Kth * (theta_cmd - theta)
              + self.Kal * (alpha - self.alpha_trim)
              - self.Kaz * (az - self.az_trim))

        v_err = self.Vt_cmd - Vt
        thr = self.thr_trim + self.KV * v_err + self.KVi * x[XI]

        da = -self.Kphi * phi - self.Kp * p
        dr = self.Kr * r

        return np.array([de, da, dr, thr], dtype=np.float64), v_err
