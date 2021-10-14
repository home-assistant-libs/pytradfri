"""Class to control the air purifiers."""
from __future__ import annotations

from typing import cast

from ..command import Command
from ..const import (
    ROOT_AIR_PURIFIER,
    ATTR_AIR_PURIFIER_STATE,
    ATTR_AIR_PURIFIER_CONTROLS_LOCKED,
    ATTR_AIR_PURIFIER_LEDS_OFF,
    RANGE_AIR_PURIFIER,
)
from ..resource import TYPE_RAW
from .base_controller import BaseController
from .air_purifier import AirPurifier


class AirPurifierControl(BaseController):
    """Class to control the air purifiers."""

    @property
    def raw(self) -> TYPE_RAW:
        """Return raw data that it represents."""
        return cast(TYPE_RAW, self._device.raw[ROOT_AIR_PURIFIER])

    @property
    def air_purifiers(self) -> list[AirPurifier]:
        """Return air purifier objects of the air purifier control."""
        return [AirPurifier(self._device, i) for i in range(len(self.raw))]

    def set_state(self, state: int) -> Command:
        """Set state of a air purifier.
        0: off
        1: Fan level auto
        10: Fan level 1
        20: Fan level 2
        30: Fan level 3
        40: Fan level 4
        50: Fan level 5
        """
        self._value_validate(state, RANGE_AIR_PURIFIER, "Air Purifier mode")
        return self.set_value({ATTR_AIR_PURIFIER_STATE: state})

    def set_controls_locked(self, locked: bool) -> Command:
        """Set physical controls locked of the air purifier"""

        return self.set_value({ATTR_AIR_PURIFIER_CONTROLS_LOCKED: 1 if locked else 0})

    def set_leds_off(self, leds_off: bool) -> Command:
        """Set led's off/on of the air purifier"""

        return self.set_value({ATTR_AIR_PURIFIER_LEDS_OFF: 1 if leds_off else 0})

    def set_value(self, value: dict[str, bool | int]) -> Command:
        """Set values on air purifier control.

        Returns a Command.
        """
        return Command("put", self._device.path, {ROOT_AIR_PURIFIER: [value]})
