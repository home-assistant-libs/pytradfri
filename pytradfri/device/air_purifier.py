"""Represent an air purifier."""
from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict, cast

from ..const import ATTR_AIR_PURIFIER_MODE_AUTO, ROOT_AIR_PURIFIER
from ..resource import TypeRawList

if TYPE_CHECKING:
    # avoid cyclic import at runtime.
    from . import Device


TypeAirPurifier = TypedDict(
    # Alternative syntax required due to the need of using strings as keys:
    # https://www.python.org/dev/peps/pep-0589/#alternative-syntax
    "TypeAirPurifier",
    {
        "5900": int,  # Mode
        "5902": int,  # Filter runtume
        "5903": int,  # Filter status
        "5904": int,  # Filter lifetime total
        "5905": int,  # Manual controls locked
        "5906": int,  # Led light on/off
        "5907": int,  # Air quality level
        "5908": int,  # Fan speed
        "5909": int,  # Motor runtime total
        "5910": int,  # Filter lifetime remaining
        "9003": int,  # ID
    },
)


class AirPurifier:
    """Represent an air purifier."""

    def __init__(self, device: Device, index: int) -> None:
        """Create object of class."""
        self.device = device
        self.index = index

    @property
    def raw(self) -> TypeAirPurifier:
        """Return raw data that it represents."""
        return cast(
            TypeAirPurifier,
            cast(TypeRawList, self.device.raw)[ROOT_AIR_PURIFIER][self.index],
        )

    @property
    def is_auto_mode(self) -> bool:
        """
        Return auto mode on or off.

        Auto mode sets the fan speed automatically based on the air quality.
        """
        return self.raw["5900"] == ATTR_AIR_PURIFIER_MODE_AUTO

    @property
    def state(self) -> bool:
        """Return device state, ie on or off."""
        return self.raw["5900"] > 0

    @property
    def fan_speed(self) -> int:
        """Get the current fan speed of the air purifier.

        0: Device is off
        2..50: Fan speed with a step size of 1.
        """
        return self.raw["5908"]

    @property
    def controls_locked(self) -> bool:
        """Return True if physical controls on the air purifier are locked."""
        return self.raw["5905"] == 1

    @property
    def leds_off(self) -> bool:
        """Return True if led's on the air purifier are turned off."""
        return self.raw["5906"] == 1

    @property
    def air_quality(self) -> int:
        """Get the current air quality measured by the air purifier.

        0..35: Good
        36..85: OK
        86..: Not good
        65535: If the fan is off or during measuring time after turning on
        """
        return self.raw["5907"]
