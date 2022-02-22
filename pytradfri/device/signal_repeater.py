"""Represent a signal repeater."""
from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:
    # avoid cyclic import at runtime.
    from . import Device


class SignalRepeaterResponse(BaseModel):
    """Represent the blind part of the device response."""


class SignalRepeater:
    """Represent a signal repeater."""

    def __init__(self, device: Device, index: int):
        """Create object of class."""
        self.device = device
        self.index = index

    @property
    def raw(self) -> SignalRepeaterResponse:
        """Return raw data that it represents."""
        return self.device.raw.signal_repater_control[self.index]  # type: ignore[union-attr, index]
