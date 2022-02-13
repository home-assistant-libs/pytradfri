"""Represent a socket."""

from pytradfri.type_hint import SocketResponse


class Socket:
    """Represent a socket."""

    def __init__(self, device, index):
        """Create object of class."""
        self.device = device
        self.index = index

    @property
    def state(self) -> bool:
        """State."""
        return self.raw.state == 1

    @property
    def raw(self) -> SocketResponse:
        """Return raw data that it represents."""
        return self.device.raw.socket[self.index]

    def __repr__(self) -> str:
        """Return representation of class object."""
        state = "on" if self.state else "off"
        return f"<Socket #{self.index} - name: {self.device.name}, state: {state}>"
