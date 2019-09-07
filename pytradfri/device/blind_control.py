"""Class to control the sockets."""
from pytradfri.command import Command
from pytradfri.const import RANGE_BLIND, \
    ATTR_BLIND_CURRENT_POSITION
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

        value = [
            {
                ATTR_BLIND_CURRENT_POSITION: value
            }
        ]
        value = {"15015": [{"5536": 50}]}

        print(self._device.path)
        print(value)

        """
        # {"15015": [{"5536": 50}]}
        ['15001', 65538]
        [{'5523': 50}]
        """

        return Command('put', self._device.path, value)
