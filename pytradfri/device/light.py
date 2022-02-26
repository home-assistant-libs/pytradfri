"""Represent a light."""
from __future__ import annotations

from typing import Any

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


class LightResponse(BaseModel):
    """Represent API response for a blind."""

    state: int = Field(alias=ATTR_DEVICE_STATE)
    id: int = Field(alias=ATTR_ID)


class Light:
    """Represent a light.

    https://github.com/IPSO-Alliance/pub/blob/master/docs/IPSO-Smart-Objects.
    pdf
    """

    def __init__(self, device, index):
        """Create object of class."""
        self.device = device
        self.index = index

    @property
    def supported_features(self):
        """Return supported features."""
        return supported_features(self.raw)

    @property
    def state(self):
        """Return device state."""
        return self.raw.state == 1

    @property
    def dimmer(self):
        """Return dimmer if present."""
        if self.supported_features & SUPPORT_BRIGHTNESS:
            return self.raw.get(ATTR_LIGHT_DIMMER)
        return None

    @property
    def color_temp(self):
        """Return color temperature."""
        if self.supported_features & SUPPORT_COLOR_TEMP:
            if self.raw.get(ATTR_LIGHT_MIREDS) != 0:
                return self.raw.get(ATTR_LIGHT_MIREDS)
        return None

    @property
    def hex_color(self):
        """Return hex color."""
        if self.supported_features & SUPPORT_HEX_COLOR:
            return self.raw.get(ATTR_LIGHT_COLOR_HEX)
        return None

    @property
    def xy_color(self):
        """Return xy color."""
        if self.supported_features & SUPPORT_XY_COLOR:
            return (self.raw.get(ATTR_LIGHT_COLOR_X), self.raw.get(ATTR_LIGHT_COLOR_Y))
        return None

    @property
    def hsb_xy_color(self):
        """Return hsb xy color."""
        return (
            self.raw.get(ATTR_LIGHT_COLOR_HUE),
            self.raw.get(ATTR_LIGHT_COLOR_SATURATION),
            self.raw.get(ATTR_LIGHT_DIMMER),
            self.raw.get(ATTR_LIGHT_COLOR_X),
            self.raw.get(ATTR_LIGHT_COLOR_Y),
        )

    @property
    def raw(self) -> LightResponse:
        """Return raw data that it represents."""
        light_control_response = self.device.raw.light_control
        assert light_control_response is not None
        return light_control_response[self.index]

    def __repr__(self):
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
