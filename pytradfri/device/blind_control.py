"""Class to control the blinds."""
from pytradfri.command import Command
from pytradfri.const import (
    RANGE_BLIND,
    ATTR_BLIND_CURRENT_POSITION,
    ATTR_START_BLINDS,
    ATTR_BLIND_TRIGGER,
)
from pytradfri.device.blind import Blind
from pytradfri.device.controller import Controller


class BlindControl(Controller):
    """Class to control the blinds."""

    def __init__(self, device):
        self._device = device

    @property
    def raw(self):
        """Return raw data that it represents."""
        return self._device.raw[ATTR_START_BLINDS]

    @property
    def blinds(self):
        """Return blind objects of the blind control."""
        return [Blind(self._device, i) for i in range(len(self.raw))]

    def trigger_blind(self):
        """Trigger the blind's movement."""
        return self.set_value({ATTR_BLIND_TRIGGER: True})

    def set_state(self, state):
        """Set state of a blind."""
        self._value_validate(state, RANGE_BLIND, "Blind position")

        return self.set_value({ATTR_BLIND_CURRENT_POSITION: state})

    def set_value(self, value):
        """
        Set values on blind control.
        Returns a Command.
        """
        return Command("put", self._device.path, {ATTR_START_BLINDS: [value]})
