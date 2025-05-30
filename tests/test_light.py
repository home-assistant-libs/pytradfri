"""Test Light."""

import pytest

from pytradfri import error
from pytradfri.device import Device
from pytradfri.device.light import Light
from pytradfri.resource import TypeRaw

from .devices import (
    LIGHT_CWS,
    LIGHT_CWS_CUSTOM_COLOR,
    LIGHT_W,
    LIGHT_WS,
    LIGHT_WS_CUSTOM_COLOR,
)


def light(raw: TypeRaw) -> Light:
    """Return Light."""
    light_control = Device(raw).light_control
    assert light_control is not None
    return light_control.lights[0]


def test_white_bulb() -> None:
    """Test white bulb."""
    bulb = light(LIGHT_W)

    assert bulb.hex_color is None
    assert bulb.xy_color is None
    assert bulb.supports_dimmer
    assert not bulb.supports_color_temp
    assert not bulb.supports_hex_color
    assert not bulb.supports_xy_color
    assert not bulb.supports_hsb_xy_color


def test_spectrum_bulb() -> None:
    """Test spectrum bulb."""
    bulb = light(LIGHT_WS)

    assert bulb.hex_color == "0"
    assert bulb.xy_color == (31103, 27007)
    assert bulb.color_temp == 400
    assert bulb.supports_dimmer
    assert bulb.supports_color_temp
    assert bulb.supports_hex_color
    assert bulb.supports_xy_color
    assert not bulb.supports_hsb_xy_color


def test_spectrum_bulb_custom_color() -> None:
    """Test spectrum custom color."""
    bulb = light(LIGHT_WS_CUSTOM_COLOR)

    assert bulb.hex_color == "0"
    assert bulb.xy_color == (32228, 27203)
    assert bulb.supports_dimmer
    assert bulb.supports_color_temp
    assert bulb.supports_hex_color
    assert bulb.supports_xy_color
    assert not bulb.supports_hsb_xy_color


def test_color_bulb() -> None:
    """Test color."""
    bulb = light(LIGHT_CWS)

    assert bulb.hex_color == "f1e0b5"
    assert bulb.xy_color == (30015, 26870)
    assert bulb.supports_dimmer
    assert not bulb.supports_color_temp
    assert bulb.supports_hex_color
    assert bulb.supports_xy_color
    assert bulb.supports_hsb_xy_color


def test_color_bulb_custom_color() -> None:
    """Test custom color."""
    bulb = light(LIGHT_CWS_CUSTOM_COLOR)

    assert bulb.hex_color == "0"
    assert bulb.xy_color == (23327, 33940)
    assert bulb.supports_dimmer
    assert not bulb.supports_color_temp
    assert bulb.supports_hex_color
    assert bulb.supports_xy_color
    assert bulb.supports_hsb_xy_color


def test_setters() -> None:
    """Test light setters."""
    light_control = Device(LIGHT_CWS).light_control
    assert light_control is not None
    cmd = light_control.set_predefined_color("Warm glow")
    assert cmd.data == {"3311": [{"5706": "efd275"}]}

    light_control = Device(LIGHT_CWS).light_control
    assert light_control is not None
    with pytest.raises(error.ColorError):
        light_control.set_predefined_color("Ggravlingen")


def test_combine_command() -> None:
    """Test light control combine command."""
    device = Device(LIGHT_CWS)

    assert device.light_control is not None

    dimmer_cmd = device.light_control.set_dimmer(100)

    assert dimmer_cmd.data == {"3311": [{"5851": 100}]}

    hsb_xy_color_cmd = device.light_control.set_hsb(
        hue=100, saturation=75, brightness=50, transition_time=60
    )

    assert hsb_xy_color_cmd.data == {
        "3311": [{"5707": 100, "5708": 75, "5712": 60, "5851": 50}]
    }

    combined_cmd = device.light_control.combine_commands([dimmer_cmd, hsb_xy_color_cmd])

    assert combined_cmd.data == {
        "3311": [{"5707": 100, "5708": 75, "5712": 60, "5851": 50}]
    }

    combined_cmd = device.light_control.combine_commands([combined_cmd, dimmer_cmd])

    assert combined_cmd.data == {
        "3311": [{"5707": 100, "5708": 75, "5712": 60, "5851": 100}]
    }

    combined_cmd.data.clear()

    with pytest.raises(TypeError):
        device.light_control.combine_commands([dimmer_cmd, combined_cmd])
