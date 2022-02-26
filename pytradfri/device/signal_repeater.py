"""Represent a signal repeater."""
from typing import Any, Dict


class SignalRepeater:
    """Represent a signal repeater."""

    def __init__(self, device, index):
        """Create object of class."""
        self.device = device
        self.index = index

    @property
    def raw(self) -> Dict[str, Any]:
        """Return raw data that it represents."""
        signal_repater_control_response = self.device.raw.signal_repeater_control
        assert signal_repater_control_response is not None
        return signal_repater_control_response[self.index]
