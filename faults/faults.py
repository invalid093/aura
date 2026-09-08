"""
Fault models for EXP-0002.

Faults are injected at the measurement and actuation interfaces, not into the
plant dynamics -- with the single exception of F6, which necessarily acts on the
plant. This distinction determines what a structural model of the system must
contain, and is recorded in reports/phase0/EXPERIMENTAL_DESIGN_PRELIMINARY.md.

Magnitudes come from configuration and are referenced to the pre-declared sensor
sigma scale. They are not tuned to produce a particular matrix.

F5 (increased noise) is deliberately absent: in a deterministic, noise-free
simulation its mean response is identical to nominal BY CONSTRUCTION. Including
it would inject a guaranteed ambiguous pair that is an artefact of the
experimental design, not a property of the aircraft. See experiment_spec.md 4.
"""

from __future__ import annotations

import numpy as np

from aircraft.gfw1 import CHANNELS

MECHANISMS = ("F0", "F1", "F2", "F3", "F4", "F6")


class Fault:
    """A single fault instance.

    mode     one of MECHANISMS
    channel  measurement channel name for sensor faults; None for F0 and F6
    """

    def __init__(self, mode: str, channel: str | None, cfg: dict,
                 magnitude_scale: float = 1.0, duration: float | None = None):
        if mode not in MECHANISMS:
            raise ValueError(f"unknown fault mode {mode!r}")
        if mode in ("F1", "F2", "F3", "F4") and channel is None:
            raise ValueError(f"{mode} requires a channel")
        if mode in ("F0", "F6") and channel is not None:
            raise ValueError(f"{mode} takes no channel")

        self.mode = mode
        self.channel = channel
        self.idx = CHANNELS.index(channel) if channel else -1
        self.onset = float(cfg["simulation"]["fault_onset"])
        self.duration = float(duration if duration is not None
                              else cfg["simulation"]["duration"])
        self.scale = float(magnitude_scale)

        fc = cfg["faults"]
        sigma = float(cfg["sensors"]["sigma"][channel]) if channel else 0.0
        self.sigma = sigma
        self.bias = self.scale * float(fc["bias_sigma_multiple"]) * sigma
        self.scale_factor = 1.0 + self.scale * (float(fc["scale_factor"]) - 1.0)
        drift_total = self.scale * float(fc["drift_end_sigma_multiple"]) * sigma
        self.drift_rate = drift_total / max(self.duration - self.onset, 1e-9)
        self.elev_eff = 1.0 - self.scale * (1.0 - float(fc["elevator_effectiveness"]))

        self._stuck_value: float | None = None

    # ------------------------------------------------------------------ naming
    @property
    def fault_id(self) -> str:
        return self.mode if self.channel is None else f"{self.mode}_{self.channel}"

    # ------------------------------------------------------------------ sensors
    def corrupt(self, y_true: np.ndarray, t: float) -> np.ndarray:
        """Return the measured output vector, with the sensor fault applied."""
        y = y_true.copy()
        if self.mode in ("F0", "F6") or t < self.onset:
            # A stuck sensor must latch the value present at onset; capture it on
            # the last pre-onset sample so the latch does not depend on step size.
            if self.mode == "F4":
                self._stuck_value = float(y_true[self.idx])
            return y

        k = self.idx
        if self.mode == "F1":
            y[k] = y_true[k] + self.bias
        elif self.mode == "F2":
            y[k] = self.scale_factor * y_true[k]
        elif self.mode == "F3":
            y[k] = y_true[k] + self.drift_rate * (t - self.onset)
        elif self.mode == "F4":
            if self._stuck_value is None:                      # pragma: no cover
                self._stuck_value = float(y_true[k])
            y[k] = self._stuck_value
        return y

    # ---------------------------------------------------------------- actuators
    def elevator_gain(self, t: float) -> float:
        """Multiplicative elevator effectiveness actually delivered to the plant."""
        if self.mode == "F6" and t >= self.onset:
            return self.elev_eff
        return 1.0

    def reset(self) -> None:
        self._stuck_value = None


def build_fault_set(cfg: dict, magnitude_scale: float = 1.0,
                    duration: float | None = None) -> list[Fault]:
    """The pre-registered EXP-0002 fault set: F0 + 4 mechanisms x 4 channels + F6."""
    faults = [Fault("F0", None, cfg, magnitude_scale, duration)]
    for mode in ("F1", "F2", "F3", "F4"):
        for ch in cfg["faults"]["channels"]:
            faults.append(Fault(mode, ch, cfg, magnitude_scale, duration))
    faults.append(Fault("F6", None, cfg, magnitude_scale, duration))
    return faults
