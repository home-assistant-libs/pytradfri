"""Class to control the sockets."""
from pytradfri.command import Command
from pytradfri.const import ATTR_BLIND_TRIGGER, RANGE_BLIND
from pytradfri.device.controller import Controller


class BlindControl(Controller):
    """Class to control the sockets."""

    def __init__(self, device):
        self._device = device

    def set_state(self, state):
        """Set state of a socket."""

        # Only allow values in the range 0, 100 (open, closed)
        self._value_validate(state, RANGE_BLIND, "Blind position")

        return self.set_value(
            state
        )

    def set_value(self, value):
        """
        Set values on blind control.
        Returns a Command.
        """

        # {"15015": [{"5536": 50}]}
        value = [
            {
                ATTR_BLIND_TRIGGER: value
            }
        ]

        print(self._device.path)
        print(value)

        return Command('put', self._device.path, value)
