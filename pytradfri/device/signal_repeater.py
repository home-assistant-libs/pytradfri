"""Represent a signal repeater."""
from typing import TYPE_CHECKING

from ..const import ROOT_SIGNAL_REPEATER

if TYPE_CHECKING:
    # avoid cyclic import at runtime.
    from . import Device


class SignalRepeater:
    """Represent a signal repeater."""

    def __init__(self, device: "Device", index: int):
        """Create object of class."""
        self.device = device
        self.index = index

    @property
    def raw(self):
        """Return raw data that it represents."""
        return self.device.raw[ROOT_SIGNAL_REPEATER][self.index]
