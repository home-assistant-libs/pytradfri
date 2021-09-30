"""Class to control the sockets."""
from __future__ import annotations

from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    # avoid cyclic import at runtime.
    from . import Device
else:
    Device = dict

from ..command import Command
from ..const import ATTR_DEVICE_STATE, ATTR_SWITCH_PLUG
<<<<<<< HEAD
from .base_controller import BaseController
=======
from ..resource import TYPE_RAW
>>>>>>> 6d1218a (Strict 3.)
from .socket import Socket


class SocketControl(BaseController):
    """Class to control the sockets."""

    @property
    def raw(self) -> TYPE_RAW:
        """Return raw data that it represents."""
        return cast(TYPE_RAW, self._device.raw[ATTR_SWITCH_PLUG])

    @property
    def sockets(self) -> list[Socket]:
        """Return socket objects of the socket control."""
        return [Socket(self._device, i) for i in range(len(self.raw))]

    def set_state(self, state: int, *, index: int = 0) -> Command:
        """Set state of a socket."""
        return self.set_values({ATTR_DEVICE_STATE: int(state)}, index=index)

    def set_values(self, values: dict[str, int], *, index: int = 0) -> Command:
        """Set values on socket control.

        Returns a Command.
        """
        assert len(self.raw) == 1, "Only devices with 1 socket supported"

        return Command("put", self._device.path, {ATTR_SWITCH_PLUG: [values]})
