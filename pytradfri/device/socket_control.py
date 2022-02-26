"""Class to control the sockets."""
from typing import Any, Dict

from ..command import Command
from ..const import ATTR_DEVICE_STATE, ATTR_SWITCH_PLUG
from .base_controller import BaseController
from .socket import Socket


class SocketControl(BaseController):
    """Class to control the sockets."""

    @property
    def raw(self) -> list[Dict[str, Any]]:
        """Return raw data that it represents."""
        socket_control_response = self._device.raw.socket_control
        assert socket_control_response is not None
        return socket_control_response

    @property
    def sockets(self):
        """Return socket objects of the socket control."""
        return [Socket(self._device, i) for i in range(len(self.raw))]

    def set_state(self, state, *, index=0):
        """Set state of a socket."""
        return self.set_values({ATTR_DEVICE_STATE: int(state)}, index=index)

    def set_values(self, values, *, index=0):
        """Set values on socket control.

        Returns a Command.
        """
        assert len(self.raw) == 1, "Only devices with 1 socket supported"

        return Command("put", self._device.path, {ATTR_SWITCH_PLUG: [values]})
