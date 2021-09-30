"""Class to control the signal repeater."""
from __future__ import annotations

from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    # avoid cyclic import at runtime.
    from . import Device
else:
    Device = dict

from ..const import ROOT_SIGNAL_REPEATER
<<<<<<< HEAD
from .base_controller import BaseController
=======
from ..resource import TYPE_RAW
>>>>>>> 6d1218a (Strict 3.)
from .signal_repeater import SignalRepeater


class SignalRepeaterControl(BaseController):
    """Class to control the signal repeaters."""

    @property
    def raw(self) -> TYPE_RAW:
        """Return raw data that it represents."""
        return cast(TYPE_RAW, self._device.raw[ROOT_SIGNAL_REPEATER])

    @property
    def signal_repeaters(self) -> list[SignalRepeater]:
        """Return signal repeater objects of the signal repeater control."""
        return [SignalRepeater(self._device, i) for i in range(len(self.raw))]
