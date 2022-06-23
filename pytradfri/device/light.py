"""Represent a light."""
from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from pydantic import Field

from ..color import supported_features
from ..const import (
    ATTR_DEVICE_STATE,
    ATTR_LIGHT_COLOR_HEX,
    ATTR_LIGHT_COLOR_HUE,
    ATTR_LIGHT_COLOR_SATURATION,
    ATTR_LIGHT_COLOR_X,
    ATTR_LIGHT_COLOR_Y,
    ATTR_LIGHT_DIMMER,
    ATTR_LIGHT_MIREDS,
    SUPPORT_BRIGHTNESS,
    SUPPORT_COLOR_TEMP,
    SUPPORT_HEX_COLOR,
    SUPPORT_RGB_COLOR,
    SUPPORT_XY_COLOR,
)
from ..resource import BaseResponse

if TYPE_CHECKING:
    # avoid cyclic import at runtime.
    from . import Device


class LightResponse(BaseResponse):
    """Represent API response for a blind."""

    color_mireds: Optional[int] = Field(alias=ATTR_LIGHT_MIREDS)
    color_hex: Optional[str] = Field(alias=ATTR_LIGHT_COLOR_HEX)
    color_xy_x: Optional[int] = Field(alias=ATTR_LIGHT_COLOR_X)
    color_xy_y: Optional[int] = Field(alias=ATTR_LIGHT_COLOR_Y)
    color_hue: Optional[int] = Field(alias=ATTR_LIGHT_COLOR_HUE)
    color_saturation: Optional[int] = Field(alias=ATTR_LIGHT_COLOR_SATURATION)
    dimmer: Optional[int] = Field(alias=ATTR_LIGHT_DIMMER)
    state: int = Field(alias=ATTR_DEVICE_STATE)


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
        return supported_features(self.raw)

    @property
    def supports_dimmer(self) -> bool:
        """Return True if light supports dimmer."""
        return bool(self.supported_features & SUPPORT_BRIGHTNESS)

    @property
    def supports_color_temp(self) -> bool:
        """Return True if light supports color temperature."""
        return bool(self.supported_features & SUPPORT_COLOR_TEMP)

    @property
    def supports_hex_color(self) -> bool:
        """Return True if light supports hex color."""
        return bool(self.supported_features & SUPPORT_HEX_COLOR)

    @property
    def supports_xy_color(self) -> bool:
        """Return True if light supports xy color."""
        return bool(self.supported_features & SUPPORT_XY_COLOR)

    @property
    def supports_hsb_xy_color(self) -> bool:
        """Return True if light supports hsb xy color."""
        return bool(self.supported_features & SUPPORT_RGB_COLOR)

    @property
    def state(self) -> bool:
        """Return device state."""
        return self.raw.state == 1

    @property
    def dimmer(self) -> int | None:
        """Return dimmer if present."""
        return self.raw.dimmer

    @property
    def color_temp(self) -> int | None:
        """Return color temperature."""
        return self.raw.color_mireds

    @property
    def hex_color(self) -> str | None:
        """Return hex color."""
        return self.raw.color_hex

    @property
    def xy_color(self) -> tuple[int, int] | None:
        """Return xy color."""
        if self.raw.color_xy_x is not None and self.raw.color_xy_y is not None:
            return (self.raw.color_xy_x, self.raw.color_xy_y)
        return None

    @property
    def hsb_xy_color(
        self,
    ) -> tuple[int, int, int, int, int] | None:
        """Return hsb xy color."""
        if (
            self.raw.color_hue is not None
            and self.raw.color_saturation is not None
            and self.raw.dimmer is not None
            and self.raw.color_xy_x is not None
            and self.raw.color_xy_y is not None
        ):
            return (
                self.raw.color_hue,
                self.raw.color_saturation,
                self.raw.dimmer,
                self.raw.color_xy_x,
                self.raw.color_xy_y,
            )

        return None

    @property
    def raw(self) -> LightResponse:
        """Return raw data that it represents."""
        light_control_response = self.device.raw.light_control
        assert light_control_response is not None
        return light_control_response[self.index]

    def __repr__(self) -> str:
        """Return representation of class object."""
        state = "on" if self.state else "off"
        return (
            f"<Light #{self.index} - name: {self.device.name}, state: {state}, "
            f"dimmer: {self.dimmer}, "
            f"hex_color: {self.hex_color}, "
            f"xy_color: {self.xy_color}, "
            f"hsb_xy_color: {self.hsb_xy_color}, "
            f"supported features: {self.supported_features} "
            ">"
        )
