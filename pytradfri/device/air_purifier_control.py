"""Class to control the air purifiers."""
from __future__ import annotations

from ..command import Command
from ..const import (
    ATTR_AIR_PURIFIER_CONTROLS_LOCKED,
    ATTR_AIR_PURIFIER_LEDS_OFF,
    ATTR_AIR_PURIFIER_MODE,
    ATTR_AIR_PURIFIER_MODE_AUTO,
    RANGE_AIR_PURIFIER,
    ROOT_AIR_PURIFIER,
)
from .air_purifier import AirPurifier, AirPurifierResponse
from .base_controller import BaseController


class AirPurifierControl(BaseController):
    """Class to control the air purifiers."""

    @property
    def raw(self) -> list[AirPurifierResponse]:
        """Return raw data that it represents."""
        air_purifier_control_response = self._device.raw.air_purifier_control
        assert air_purifier_control_response is not None
        return air_purifier_control_response

    @property
    def air_purifiers(self) -> list[AirPurifier]:
        """Return air purifier objects of the air purifier control."""
        return [AirPurifier(self._device, i) for i in range(len(self.raw))]

    def turn_off(self, *, index: int = 0) -> Command[None]:
        """Turn the device off."""
        return self.set_value({ATTR_AIR_PURIFIER_MODE: 0}, index=index)

    def turn_on_auto_mode(self, *, index: int = 0) -> Command[None]:
        """Turn on auto mode."""
        return self.set_value(
            {ATTR_AIR_PURIFIER_MODE: ATTR_AIR_PURIFIER_MODE_AUTO}, index=index
        )

    def set_fan_speed(self, mode: int, *, index: int = 0) -> Command[None]:
        """Set the fan speed of the purifier."""
        self._value_validate(mode, RANGE_AIR_PURIFIER, "Air Purifier mode")
        return self.set_value({ATTR_AIR_PURIFIER_MODE: mode}, index=index)

    def set_controls_locked(self, locked: bool, *, index: int = 0) -> Command[None]:
        """Set physical controls locked of the air purifier."""
        return self.set_value(
            {ATTR_AIR_PURIFIER_CONTROLS_LOCKED: 1 if locked else 0}, index=index
        )

    def set_leds_off(self, leds_off: bool, *, index: int = 0) -> Command[None]:
        """Set led's off/on of the air purifier."""
        return self.set_value(
            {ATTR_AIR_PURIFIER_LEDS_OFF: 1 if leds_off else 0}, index=index
        )

    def set_value(
        self, value: dict[str, bool | int], *, index: int = 0
    ) -> Command[None]:
        """Set values on air purifier control.

        Returns a Command.
        """
        assert len(self.raw) == 1, "Only devices with 1 air purifier supported"

        return Command("put", self._device.path, {ROOT_AIR_PURIFIER: [value]})
