"""Class to control the sockets."""
from pytradfri.command import Command
from pytradfri.const import ATTR_BLIND_TRIGGER


class BlindControl:
    """Class to control the sockets."""

    def __init__(self, device):
        self._device = device

    def set_state(self, state):
        """Set state of a socket."""
        return self.set_value(
            state
        )

    def set_value(self, value):
        """
        Set values on blind control.
        Returns a Command.
        """

        return Command('put', self._device.path, {
            ATTR_BLIND_TRIGGER: value
        })
