"""Class to control the sockets."""
from pytradfri.command import Command
from pytradfri.const import ATTR_SWITCH_PLUG, ATTR_DEVICE_STATE
from pytradfri.device.socket import Socket


class SocketControl:
    """Class to control the sockets."""

    def __init__(self, device):
        self._device = device

    @property
    def raw(self):
        """Return raw data that it represents."""
        return self._device.raw[ATTR_SWITCH_PLUG]

    @property
    def sockets(self):
        """Return socket objects of the socket control."""
        return [Socket(self._device, i) for i in range(len(self.raw))]

    def set_state(self, state, *, index=0):
        """Set state of a socket."""
        return self.set_values({ATTR_DEVICE_STATE: int(state)}, index=index)

    def set_values(self, values, *, index=0):
        """
        Set values on socket control.
        Returns a Command.
        """
        assert len(self.raw) == 1, "Only devices with 1 socket supported"

        return Command("put", self._device.path, {ATTR_SWITCH_PLUG: [values]})

    def __repr__(self):
        return "<SocketControl for {} ({} sockets)>".format(
            self._device.name, len(self.raw)
        )
