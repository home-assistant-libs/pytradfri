"""Class to control the blinds."""
from __future__ import annotations

from ..command import Command
from ..const import (
    ATTR_BLIND_CURRENT_POSITION,
    ATTR_BLIND_TRIGGER,
    ATTR_START_BLINDS,
    RANGE_BLIND,
)
from .base_controller import BaseController
from .blind import Blind, BlindResponse


class BlindControl(BaseController):
    """Class to control the blinds."""

    @property
    def raw(self) -> list[BlindResponse]:
        """Return raw data that it represents."""
        blind_control_response = self._device.raw.blind_control
        assert blind_control_response is not None
        return blind_control_response

    @property
    def blinds(self) -> list[Blind]:
        """Return blind objects of the blind control."""
        return [Blind(self._device, i) for i in range(len(self.raw))]

    def trigger_blind(self) -> Command[None]:
        """Trigger the blind's movement."""
        return self.set_value({ATTR_BLIND_TRIGGER: True})

    def set_state(self, state: int) -> Command[None]:
        """Set state of a blind."""
        self._value_validate(state, RANGE_BLIND, "Blind position")

        return self.set_value({ATTR_BLIND_CURRENT_POSITION: state})

    def set_value(self, value: dict[str, bool | int]) -> Command[None]:
        """Set values on blind control.

        Returns a Command.
        """
        return Command("put", self._device.path, {ATTR_START_BLINDS: [value]})
