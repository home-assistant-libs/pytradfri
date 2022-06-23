"""Test Light."""
import pytest

from pytradfri import error
from pytradfri.device import Device

from .devices import (
    LIGHT_CWS,
    LIGHT_CWS_CUSTOM_COLOR,
    LIGHT_W,
    LIGHT_WS,
    LIGHT_WS_CUSTOM_COLOR,
)


def light(raw):
    """Return Light."""
    return Device(raw).light_control.lights[0]


def test_white_bulb():
    """Test white bulb."""
    bulb = light(LIGHT_W)

    assert bulb.hex_color is None
    assert bulb.xy_color is None
    assert bulb.supports_dimmer
    assert not bulb.supports_color_temp
    assert not bulb.supports_hex_color
    assert not bulb.supports_xy_color
    assert not bulb.supports_hsb_xy_color


def test_spectrum_bulb():
    """Test sprectrum bulb."""
    bulb = light(LIGHT_WS)

    assert bulb.hex_color == "0"
    assert bulb.xy_color == (31103, 27007)
    assert bulb.color_temp == 400
    assert bulb.supports_dimmer
    assert bulb.supports_color_temp
    assert bulb.supports_hex_color
    assert bulb.supports_xy_color
    assert not bulb.supports_hsb_xy_color


def test_spectrum_bulb_custom_color():
    """Test spectrum custom color."""
    bulb = light(LIGHT_WS_CUSTOM_COLOR)

    assert bulb.hex_color == "0"
    assert bulb.xy_color == (32228, 27203)
    assert bulb.supports_dimmer
    assert bulb.supports_color_temp
    assert bulb.supports_hex_color
    assert bulb.supports_xy_color
    assert not bulb.supports_hsb_xy_color


def test_color_bulb():
    """Test color."""
    bulb = light(LIGHT_CWS)

    assert bulb.hex_color == "f1e0b5"
    assert bulb.xy_color == (30015, 26870)
    assert bulb.supports_dimmer
    assert not bulb.supports_color_temp
    assert bulb.supports_hex_color
    assert bulb.supports_xy_color
    assert bulb.supports_hsb_xy_color


def test_color_bulb_custom_color():
    """Test custom color."""
    bulb = light(LIGHT_CWS_CUSTOM_COLOR)

    assert bulb.hex_color == "0"
    assert bulb.xy_color == (23327, 33940)
    assert bulb.supports_dimmer
    assert not bulb.supports_color_temp
    assert bulb.supports_hex_color
    assert bulb.supports_xy_color
    assert bulb.supports_hsb_xy_color


def test_setters():
    """Test light setters."""
    cmd = Device(LIGHT_CWS).light_control.set_predefined_color("Warm glow")
    assert cmd.data == {"3311": [{"5706": "efd275"}]}

    with pytest.raises(error.ColorError):
        Device(LIGHT_CWS).light_control.set_predefined_color("Ggravlingen")
