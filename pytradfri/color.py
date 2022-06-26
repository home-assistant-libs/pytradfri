"""Test Color."""
from __future__ import annotations

from typing import TYPE_CHECKING

from .const import (
    SUPPORT_BRIGHTNESS,
    SUPPORT_COLOR_TEMP,
    SUPPORT_HEX_COLOR,
    SUPPORT_RGB_COLOR,
    SUPPORT_XY_COLOR,
)

if TYPE_CHECKING:
    from .device.light import LightResponse

# Extracted from Tradfri Android App string.xml
COLOR_NAMES = {
    "4a418a": "Blue",
    "6c83ba": "Light Blue",
    "8f2686": "Saturated Purple",
    "a9d62b": "Lime",
    "c984bb": "Light Purple",
    "d6e44b": "Yellow",
    "d9337c": "Saturated Pink",
    "da5d41": "Dark Peach",
    "dc4b31": "Saturated Red",
    "dcf0f8": "Cold sky",
    "e491af": "Pink",
    "e57345": "Peach",
    "e78834": "Warm Amber",
    "e8bedd": "Light Pink",
    "eaf6fb": "Cool daylight",
    "ebb63e": "Candlelight",
    "efd275": "Warm glow",
    "f1e0b5": "Warm white",
    "f2eccf": "Sunrise",
    "f5faf6": "Cool white",
}
# When setting colors by name via the API,
# lowercase strings with no spaces are preferred
COLORS = {name.lower().replace(" ", "_"): hex for hex, name in COLOR_NAMES.items()}


def supported_features(data: LightResponse) -> int:
    """Return supported features."""
    supported_color_features = 0

    if data.dimmer is not None:
        supported_color_features = supported_color_features + SUPPORT_BRIGHTNESS

    if data.color_hex:
        supported_color_features = supported_color_features + SUPPORT_HEX_COLOR

    if data.color_mireds is not None:
        supported_color_features = supported_color_features + SUPPORT_COLOR_TEMP

    if None not in (data.color_xy_x, data.color_xy_y):
        supported_color_features = supported_color_features + SUPPORT_XY_COLOR

    if (
        data.color_mireds is None
        and data.color_xy_x is not None
        and data.color_xy_y is not None
        and data.color_saturation is not None
        and data.color_hue is not None
        and data.dimmer is not None
    ):
        supported_color_features = supported_color_features + SUPPORT_RGB_COLOR

    return supported_color_features
