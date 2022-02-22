"""Class to control the signal repeater."""
from __future__ import annotations

from .base_controller import BaseController
from .signal_repeater import SignalRepeater


class SignalRepeaterControl(BaseController):
    """Class to control the signal repeaters."""

    @property
    def raw(self):
        """Return raw data that it represents."""
        return self._device.signal_repeater_control

    @property
    def signal_repeaters(self):
        """Return signal repeater objects of the signal repeater control."""
        return [SignalRepeater(self._device, i) for i in range(len(self.raw))]
