"""Represent a light."""
from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

from ..color import supported_features
from ..const import (
    ATTR_DEVICE_STATE,
    ATTR_ID,
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
    SUPPORT_XY_COLOR,
)

if TYPE_CHECKING:
    # avoid cyclic import at runtime.
    from . import Device


class LightResponse(BaseModel):
    """Represent API response for a blind."""

    color_mireds: int | None = Field(alias=ATTR_LIGHT_MIREDS)
    color_hex: str | None = Field(alias=ATTR_LIGHT_COLOR_HEX)
    color_xy_x: int | None = Field(alias=ATTR_LIGHT_COLOR_X)
    color_xy_y: int | None = Field(alias=ATTR_LIGHT_COLOR_Y)
    color_hue: int | None = Field(alias=ATTR_LIGHT_COLOR_HUE)
    color_saturation: int | None = Field(alias=ATTR_LIGHT_COLOR_SATURATION)
    dimmer: int = Field(alias=ATTR_LIGHT_DIMMER)
    id: int = Field(alias=ATTR_ID)
    state: int = Field(alias=ATTR_DEVICE_STATE)


class Light:
    """Represent a light.

    https://github.com/IPSO-Alliance/pub/blob/master/docs/IPSO-Smart-Objects.
    pdf
    """

    def __init__(self, device: Device, index: int):
        """Create object of class."""
        self.device = device
        self.index = index

    @property
    def supported_features(self) -> int:
        """Return supported features."""
        return supported_features(self.raw.dict())

    @property
    def state(self) -> bool:
        """Return device state."""
        return self.raw.state == 1

    @property
    def dimmer(self) -> int | None:
        """Return dimmer if present."""
        if self.supported_features & SUPPORT_BRIGHTNESS:
            return self.raw.dimmer
        return None

    @property
    def color_temp(self) -> int | None:
        """Return color temperature."""
        if self.supported_features & SUPPORT_COLOR_TEMP and self.raw.color_mireds:
            return self.raw.color_mireds
        return None

    @property
    def hex_color(self) -> str | None:
        """Return hex color."""
        if self.supported_features & SUPPORT_HEX_COLOR:
            return self.raw.color_hex
        return None

    @property
    def xy_color(self) -> tuple[int | None, int | None] | None:
        """Return xy color."""
        if self.supported_features & SUPPORT_XY_COLOR:
            return (self.raw.color_xy_x, self.raw.color_xy_y)
        return None

    @property
    def hsb_xy_color(
        self,
    ) -> tuple[int | None, int | None, int, int | None, int | None]:
        """Return hsb xy color."""
        return (
            self.raw.color_hue,
            self.raw.color_saturation,
            self.raw.dimmer,
            self.raw.color_xy_x,
            self.raw.color_xy_y,
        )

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
