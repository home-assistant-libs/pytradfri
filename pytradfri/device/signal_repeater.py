"""Represent a signal repeater."""
from __future__ import annotations

from typing import TYPE_CHECKING

from ..resource import BaseResponse

if TYPE_CHECKING:
    from . import Device


class SignalRepeaterResponse(BaseResponse):
    """Represent API response for a signal repeater."""


class SignalRepeater:
    """Represent a signal repeater."""

    def __init__(self, device: Device, index: int) -> None:
        """Create object of class."""
        self.device = device
        self.index = index

    @property
    def id(self) -> int:
        """Return ID."""
        return self.raw.id

    @property
    def raw(self) -> SignalRepeaterResponse:
        """Return raw data that it represents."""
        signal_repeater_control_response = self.device.raw.signal_repeater_control
        assert signal_repeater_control_response is not None
        return signal_repeater_control_response[self.index]
