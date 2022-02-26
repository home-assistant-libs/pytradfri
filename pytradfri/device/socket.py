"""Represent a socket."""
from ..const import ATTR_DEVICE_STATE, ATTR_SWITCH_PLUG


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
    def raw(self):
        """Return raw data that it represents."""
        return self.device.raw[ATTR_SWITCH_PLUG][self.index]

    def __repr__(self):
        """Return representation of class object."""
        state = "on" if self.state else "off"
        return f"<Socket #{self.index} - name: {self.device.name}, state: {state}>"
