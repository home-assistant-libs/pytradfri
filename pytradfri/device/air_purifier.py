"""Represent an air purifier."""
from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

from ..const import (
    ATTR_AIR_PURIFIER_AIR_QUALITY,
    ATTR_AIR_PURIFIER_CONTROLS_LOCKED,
    ATTR_AIR_PURIFIER_FAN_SPEED,
    ATTR_AIR_PURIFIER_FILTER_LIFETIME_REMAINING,
    ATTR_AIR_PURIFIER_FILTER_LIFETIME_TOTAL,
    ATTR_AIR_PURIFIER_FILTER_RUNTIME,
    ATTR_AIR_PURIFIER_FILTER_STATUS,
    ATTR_AIR_PURIFIER_LEDS_OFF,
    ATTR_AIR_PURIFIER_MODE,
    ATTR_AIR_PURIFIER_MODE_AUTO,
    ATTR_AIR_PURIFIER_MOTOR_RUNTIME_TOTAL,
    ATTR_ID,
)

if TYPE_CHECKING:
    # avoid cyclic import at runtime.
    from . import Device


class AirPurifierResponse(BaseModel):
    """Represent the air purifier part of the device response."""

    air_quality: int = Field(alias=ATTR_AIR_PURIFIER_AIR_QUALITY)
    controls_locked: int = Field(alias=ATTR_AIR_PURIFIER_CONTROLS_LOCKED)
    fan_speed: int = Field(alias=ATTR_AIR_PURIFIER_FAN_SPEED)
    filter_lifetime_remaining: int = Field(
        alias=ATTR_AIR_PURIFIER_FILTER_LIFETIME_REMAINING
    )
    filter_lifetime_total: int = Field(alias=ATTR_AIR_PURIFIER_FILTER_LIFETIME_TOTAL)
    filter_runtime: int = Field(alias=ATTR_AIR_PURIFIER_FILTER_RUNTIME)
    filter_status: int = Field(alias=ATTR_AIR_PURIFIER_FILTER_STATUS)
    id: int = Field(alias=ATTR_ID)
    leds_off: int = Field(alias=ATTR_AIR_PURIFIER_LEDS_OFF)
    mode: int = Field(alias=ATTR_AIR_PURIFIER_MODE)
    motor_runtime_total: int = Field(alias=ATTR_AIR_PURIFIER_MOTOR_RUNTIME_TOTAL)


class AirPurifier:
    """Represent an air purifier."""

    _model_class: type[AirPurifierResponse] = AirPurifierResponse
    raw: AirPurifierResponse

    def __init__(self, device: Device, index: int) -> None:
        """Create object of class."""
        self.device = device
        self.index = index
        self.raw = self.device.raw.air_purifier[index]

    @property
    def air_quality(self) -> int:
        """Get the current air quality measured by the air purifier.

        0..35: Good
        36..85: OK
        86..: Not good
        65535: If the fan is off or during measuring time after turning on
        """
        return self.raw.air_quality

    @property
    def controls_locked(self) -> bool:
        """Return True if physical controls on the air purifier are locked."""
        return self.raw.controls_locked == 1

    @property
    def fan_speed(self) -> int:
        """Get the current fan speed of the air purifier.

        0: Device is off
        2..50: Fan speed with a step size of 1.
        """
        return self.raw.fan_speed

    @property
    def filter_lifetime_remaining(self) -> int:
        """Return remaining lifetime of filter, expressed in minutes."""
        return self.raw.filter_lifetime_remaining

    @property
    def filter_lifetime_total(self) -> int:
        """Return total lifetime of filter, expressed in minutes."""
        return self.raw.filter_lifetime_total

    @property
    def filter_runtime(self) -> int:
        """Return filter runtime, expressed in minutes."""
        return self.raw.filter_runtime

    @property
    def filter_status(self) -> int:
        """Return filter status."""
        return self.raw.filter_status

    @property
    def is_auto_mode(self) -> bool:
        """
        Return auto mode on or off.

        Auto mode sets the fan speed automatically based on the air quality.
        """
        return self.raw.mode == ATTR_AIR_PURIFIER_MODE_AUTO

    @property
    def leds_off(self) -> bool:
        """Return True if led's on the air purifier are turned off."""
        return self.raw.leds_off == 1

    @property
    def motor_runtime_total(self) -> int:
        """Return runtime of fan motor, expressed in minutes."""
        return self.raw.motor_runtime_total

    @property
    def state(self) -> bool:
        """Return device state, ie on or off."""
        return self.raw.mode > 0
