"""Represent a blind."""
from pytradfri.const import ATTR_START_BLINDS, ATTR_BLIND_CURRENT_POSITION


class Blind:
    """Represent a blind."""

    def __init__(self, device, index):
        self.device = device
        self.index = index

    @property
    def raw(self):
        """Return raw data that it represents."""
        return self.device.raw[ATTR_START_BLINDS][self.index]

    @property
    def current_cover_position(self):
        """Get the current position of the blind."""
        return self.raw.get(ATTR_BLIND_CURRENT_POSITION)
