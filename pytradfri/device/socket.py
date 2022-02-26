"""Represent a socket."""
from __future__ import annotations

from typing import Any

from ..const import ATTR_DEVICE_STATE


class Socket:
    """Represent a socket."""

    def __init__(self, device, index):
        """Create object of class."""
        self.device = device
        self.index = index

    @property
    def state(self):
        """State."""
        return self.raw.get(ATTR_DEVICE_STATE) == 1

    @property
    def raw(self) -> dict[str, Any]:
        """Return raw data that it represents."""
        socket_control_response = self.device.raw.socket_control
        assert socket_control_response is not None
        return socket_control_response[self.index]

    def __repr__(self):
        """Return representation of class object."""
        state = "on" if self.state else "off"
        return f"<Socket #{self.index} - name: {self.device.name}, state: {state}>"
