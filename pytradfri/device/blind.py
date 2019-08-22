"""Represent a blind."""
from pytradfri.const import ATTR_SWITCH_PLUG


class Blind:
    """Represent a socket."""

    def __init__(self, device, index):
        self.device = device
        self.index = index

    @property
    def raw(self):
        """Return raw data that it represents."""
        return self.device.raw[ATTR_SWITCH_PLUG][self.index]
