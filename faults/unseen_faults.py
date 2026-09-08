"""
Unseen faults for EXP-0012 — mechanisms deliberately ABSENT from the diagnostic
hypothesis library.

Every unseen fault has a physical interpretation, a mathematical definition, and a
stated reason for lying outside H_known = {F0, bias, scale, drift, stuck on
(q, az, Vt, alpha), elevator effectiveness}. See experiments/EXP-0012/experiment_spec.md §5.

Two kinds are represented, and they enter the simulation at different points:

  * SENSOR-level (UF-001..UF-004) corrupt the measurement, like the library faults.
  * PLANT-level (UF-005, UF-006) modify aerodynamic coefficients, so they change the
    aircraft itself. These are applied by temporarily mutating the model's coefficients
    from onset; the caller must restore them (`restore`), which the runner does.

None of these is arbitrary numerical corruption: each is a documented or physically
plausible degradation mode.
"""

from __future__ import annotations

import numpy as np

from aircraft.gfw1 import CHANNELS

UNSEEN_IDS = ("UF-001", "UF-002", "UF-003", "UF-004", "UF-005", "UF-006")


class UnseenFault:
    """One unseen fault at one magnitude scale."""

    def __init__(self, uf_id: str, cfg2: dict, cfg12: dict, scale: float = 1.0):
        if uf_id not in UNSEEN_IDS:
            raise ValueError(f"unknown unseen fault {uf_id!r}")
        self.id = uf_id
        self.scale = float(scale)
        self.onset = float(cfg2["simulation"]["fault_onset"])
        self.dt = float(cfg2["simulation"]["dt"])
        p = cfg12["unseen_faults"][uf_id]
        self.params = p
        self.channel = p.get("channel")
        self.idx = CHANNELS.index(self.channel) if self.channel else -1
        self.is_plant = bool(p.get("plant", False))
        self._saved = None
        self.reset()

    @property
    def label(self) -> str:
        return f"{self.id}_m{self.scale:g}"

    def reset(self) -> None:
        self._last = None          # UF-001 stiction memory
        self._filt = None          # UF-003 lag state

    # ------------------------------------------------------------- sensor level
    def corrupt(self, y_true: np.ndarray, t: float, aux: dict) -> np.ndarray:
        """Return the measured vector with the unseen sensor fault applied."""
        y = y_true.copy()
        if self.is_plant:
            return y

        pre = t < self.onset
        k = self.idx

        if self.id == "UF-001":
            # Vane stiction: the reading only moves once the true value has departed
            # by more than delta from the last reported value.
            delta = self.scale * float(self.params["delta"])
            if pre or self._last is None:
                self._last = float(y_true[k])
                return y
            if abs(y_true[k] - self._last) >= delta:
                self._last = float(y_true[k] - np.sign(y_true[k] - self._last) * delta)
            y[k] = self._last

        elif self.id == "UF-002":
            # Rate-gyro saturation: output clips beyond the sensor's range.
            if not pre:
                L = float(self.params["limit"]) / max(self.scale, 1e-9)
                y[k] = float(np.clip(y_true[k], -L, L))

        elif self.id == "UF-003":
            # Pitot pneumatic lag from a partial line blockage: first-order filter.
            tau = self.scale * float(self.params["tau"])
            if pre or self._filt is None:
                self._filt = float(y_true[k])
            else:
                a = self.dt / max(tau, 1e-9)
                self._filt += min(a, 1.0) * (float(y_true[k]) - self._filt)
            y[k] = self._filt

        elif self.id == "UF-004":
            # Static-port blockage: ONE static-pressure error corrupts BOTH barometric
            # altitude and airspeed. h_err = dp/(rho g); V_err ~ dp/(rho V).
            if not pre:
                dp = self.scale * float(self.params["delta_p"])
                rho = float(aux["rho"])
                g = float(aux["g"])
                V = max(float(y_true[CHANNELS.index("Vt")]), 1.0)
                y[CHANNELS.index("h")] = y_true[CHANNELS.index("h")] + dp / (rho * g)
                y[CHANNELS.index("Vt")] = y_true[CHANNELS.index("Vt")] + dp / (rho * V)
        return y

    # -------------------------------------------------------------- plant level
    def apply_plant(self, model, t: float) -> None:
        """Mutate aerodynamic coefficients from onset (zero-order hold across the step)."""
        if not self.is_plant:
            return
        if self._saved is None:
            self._saved = {k: model.p[k] for k in self.params["coefficients"]}
        if t < self.onset:
            for k, v in self._saved.items():
                model.p[k] = v
            return
        for k, v in self._saved.items():
            factor = 1.0 - self.scale * float(self.params["loss"]) \
                if self.params["mode"] == "reduce" \
                else 1.0 + self.scale * float(self.params["loss"])
            model.p[k] = v * factor

    def restore(self, model) -> None:
        """Undo any plant mutation. The runner calls this after every run."""
        if self._saved:
            for k, v in self._saved.items():
                model.p[k] = v
        self._saved = None
