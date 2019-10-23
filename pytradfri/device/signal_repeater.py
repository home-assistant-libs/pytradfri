"""Represent a signal repeater."""
from pytradfri.const import ROOT_SIGNAL_REPEATER


class SignalRepeater:
    """Represent a signal repeater."""

    def __init__(self, device, index):
        self.device = device
        self.index = index

    @property
    def raw(self):
        """Return raw data that it represents."""
        return self.device.raw[ROOT_SIGNAL_REPEATER][self.index]
