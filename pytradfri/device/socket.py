"""Represent a socket."""
from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

from pytradfri.const import ATTR_DEVICE_STATE, ATTR_ID, ATTR_LIGHT_DIMMER

if TYPE_CHECKING:
    # avoid cyclic import at runtime.
    from . import Device


class SocketResponse(BaseModel):
    """Represent the socket part of the device response."""

    id: int = Field(alias=ATTR_ID)
    state: int = Field(alias=ATTR_DEVICE_STATE)
    dimmer: int = Field(alias=ATTR_LIGHT_DIMMER)


class Socket:
    """Represent a socket."""

    def __init__(self, device: "Device", index: int):
        """Create object of class."""
        self.device = device
        self.index = index

    @property
    def raw(self) -> SocketResponse:
        """Return raw response."""
        return self.device.raw.socket_control[self.index]  # type: ignore[union-attr, index]

    @property
    def state(self) -> bool:
        """State."""
        return self.raw.state == 1

    def __repr__(self) -> str:
        """Return representation of class object."""
        state = "on" if self.state else "off"
        return f"<Socket #{self.index} - name: {self.device.name}, state: {state}>"
