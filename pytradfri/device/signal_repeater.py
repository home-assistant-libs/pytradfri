"""Represent a signal repeater."""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from . import Device


class SignalRepeater:
    """Represent a signal repeater."""

    def __init__(self, device: Device, index: int) -> None:
        """Create object of class."""
        self.device = device
        self.index = index

    @property
    def raw(self) -> dict[str, Any]:
        """Return raw data that it represents."""
        signal_repeater_control_response = self.device.raw.signal_repeater_control
        assert signal_repeater_control_response is not None
        return signal_repeater_control_response[self.index]
