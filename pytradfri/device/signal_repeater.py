"""Represent a signal repeater."""
from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

from ..const import ATTR_ID

if TYPE_CHECKING:
    from . import Device


class SignalRepeaterResponse(BaseModel):
    """Represent API response for a signal repeater."""

    id: int = Field(alias=ATTR_ID)


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
