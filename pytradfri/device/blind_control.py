"""Class to control the blinds."""
from __future__ import annotations

from typing import TYPE_CHECKING, cast

from pytradfri.command import Command
from pytradfri.const import (
    ATTR_BLIND_CURRENT_POSITION,
    ATTR_BLIND_TRIGGER,
    ATTR_START_BLINDS,
    RANGE_BLIND,
)
from pytradfri.device.blind import Blind
from pytradfri.device.controller import Controller
from pytradfri.resource import TYPE_RAW

if TYPE_CHECKING:
    # avoid cyclic import at runtime.
    from . import Device


class BlindControl(Controller):
    """Class to control the blinds."""

    def __init__(self, device: Device) -> None:
        """Create object of class."""
        self._device = device

    @property
    def raw(self) -> TYPE_RAW:
        """Return raw data that it represents."""
        return cast(TYPE_RAW, self._device.raw[ATTR_START_BLINDS])

    @property
    def blinds(self) -> list[Blind]:
        """Return blind objects of the blind control."""
        return [Blind(self._device, i) for i in range(len(self.raw))]

    def trigger_blind(self) -> Command:
        """Trigger the blind's movement."""
        return self.set_value({ATTR_BLIND_TRIGGER: True})

    def set_state(self, state: int) -> Command:
        """Set state of a blind."""
        self._value_validate(state, RANGE_BLIND, "Blind position")

        return self.set_value({ATTR_BLIND_CURRENT_POSITION: state})

    def set_value(self, value: dict[str, bool | int]) -> Command:
        """Set values on blind control.

        Returns a Command.
        """
        return Command("put", self._device.path, {ATTR_START_BLINDS: [value]})
