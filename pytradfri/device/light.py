"""Represent a light."""
from __future__ import annotations

from typing import TYPE_CHECKING, cast

from ..color import supported_features
from ..const import (
    ATTR_DEVICE_STATE,
    ATTR_LIGHT_COLOR_HEX,
    ATTR_LIGHT_COLOR_HUE,
    ATTR_LIGHT_COLOR_SATURATION,
    ATTR_LIGHT_COLOR_X,
    ATTR_LIGHT_COLOR_Y,
    ATTR_LIGHT_CONTROL,
    ATTR_LIGHT_DIMMER,
    ATTR_LIGHT_MIREDS,
    SUPPORT_BRIGHTNESS,
    SUPPORT_COLOR_TEMP,
    SUPPORT_HEX_COLOR,
    SUPPORT_XY_COLOR,
)
from ..resource import TYPE_RAW, TYPE_RAW_LIST, TYPE_RAW_SIMPLE

if TYPE_CHECKING:
    # avoid cyclic import at runtime.
    from . import Device
else:
    Device = dict


class Light:
    """Represent a light.

    https://github.com/IPSO-Alliance/pub/blob/master/docs/IPSO-Smart-Objects.
    pdf
    """

    def __init__(self, device: Device, index: int) -> None:
        """Create object of class."""
        self.device = device
        self.index = index

    @property
    def supported_features(self) -> int:
        """Return supported features."""
        return supported_features(cast(TYPE_RAW_SIMPLE, self.raw))

    @property
    def state(self) -> bool:
        """Return device state."""
        return cast(TYPE_RAW_SIMPLE, self.raw).get(ATTR_DEVICE_STATE) == 1

    @property
    def dimmer(self) -> int | None:
        """Return dimmer if present."""
        if self.supported_features & SUPPORT_BRIGHTNESS:
            return cast(int, cast(TYPE_RAW_SIMPLE, self.raw).get(ATTR_LIGHT_DIMMER))
        return None

    @property
    def color_temp(self) -> int | None:
        """Return color temperature."""
        if self.supported_features & SUPPORT_COLOR_TEMP:
            if self.raw.get(ATTR_LIGHT_MIREDS) != 0:
                return cast(int, cast(TYPE_RAW_SIMPLE, self.raw).get(ATTR_LIGHT_MIREDS))
        return None

    @property
    def hex_color(self) -> str | None:
        """Return hex color."""
        if self.supported_features & SUPPORT_HEX_COLOR:
            return cast(str, cast(TYPE_RAW_SIMPLE, self.raw).get(ATTR_LIGHT_COLOR_HEX))
        return None

    @property
    def xy_color(self) -> tuple[int, int] | None:
        """Return xy color."""
        if self.supported_features & SUPPORT_XY_COLOR:
            return cast(
                int, cast(TYPE_RAW_SIMPLE, self.raw).get(ATTR_LIGHT_COLOR_X)
            ), cast(int, cast(TYPE_RAW_SIMPLE, self.raw).get(ATTR_LIGHT_COLOR_Y))
        return None

    @property
    def hsb_xy_color(self) -> tuple[int, int, int, int, int]:
        """Return hsb xy color."""
        return (
            cast(int, self.raw.get(ATTR_LIGHT_COLOR_HUE)),
            cast(int, self.raw.get(ATTR_LIGHT_COLOR_SATURATION)),
            cast(int, self.raw.get(ATTR_LIGHT_DIMMER)),
            cast(int, self.raw.get(ATTR_LIGHT_COLOR_X)),
            cast(int, self.raw.get(ATTR_LIGHT_COLOR_Y)),
        )

    @property
    def raw(self) -> TYPE_RAW:
        """Return raw data that it represents."""
        return cast(
            TYPE_RAW,
            cast(TYPE_RAW_LIST, self.device.raw)[ATTR_LIGHT_CONTROL][self.index],
        )

    def __repr__(self) -> str:
        """Return representation of class object."""
        state = "on" if self.state else "off"
        return (
            f"<Light #{self.index} - name: {self.device.name}, state: {state}, "
            "dimmer: {self.dimmer}, "
            "hex_color: {self.hex_color}, "
            "xy_color: {self.xy_color}, "
            "hsb_xy_color: {self.hsb_xy_color}, "
            "supported features: {self.supported_features} "
            ">"
        )
