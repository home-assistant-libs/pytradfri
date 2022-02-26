"""Class to control the signal repeater."""
from __future__ import annotations

from typing import Any

from .base_controller import BaseController
from .signal_repeater import SignalRepeater


class SignalRepeaterControl(BaseController):
    """Class to control the signal repeaters."""

    @property
    def raw(self) -> list[dict[str, Any]]:
        """Return raw data that it represents."""
        signal_repeater_control_response = self._device.raw.signal_repeater_control
        assert signal_repeater_control_response is not None
        return signal_repeater_control_response

    @property
    def signal_repeaters(self):
        """Return signal repeater objects of the signal repeater control."""
        return [SignalRepeater(self._device, i) for i in range(len(self.raw))]
