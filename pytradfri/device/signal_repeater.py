"""Represent a signal repeater."""
from typing import TYPE_CHECKING, cast

from ..const import ROOT_SIGNAL_REPEATER
from ..resource import TYPE_RAW, TYPE_RAW_LIST

if TYPE_CHECKING:
    # avoid cyclic import at runtime.
    from . import Device
else:
    Device = dict


class SignalRepeater:
    """Represent a signal repeater."""

    def __init__(self, device: Device, index: int) -> None:
        """Create object of class."""
        self.device = device
        self.index = index

    @property
    def raw(self) -> TYPE_RAW:
        """Return raw data that it represents."""
        return cast(
            TYPE_RAW,
            cast(TYPE_RAW_LIST, self.device.raw)[ROOT_SIGNAL_REPEATER][self.index],
        )
