from pytradfri.device import Device
import pytest
from pytradfri import error
from devices import (
    LIGHT_W,
    LIGHT_WS,
    LIGHT_WS_CUSTOM_COLOR,
    LIGHT_CWS,
    LIGHT_CWS_CUSTOM_COLOR,
)


def light(raw):
    return Device(raw).light_control.lights[0]


def test_white_bulb():
    bulb = light(LIGHT_W)

    assert bulb.hex_color is None
    assert bulb.xy_color is None


def test_spectrum_bulb():
    bulb = light(LIGHT_WS)

    assert bulb.hex_color == "0"
    assert bulb.xy_color == (31103, 27007)
    assert bulb.color_temp == 400


def test_spectrum_bulb_custom_color():
    bulb = light(LIGHT_WS_CUSTOM_COLOR)

    assert bulb.hex_color == "0"
    assert bulb.xy_color == (32228, 27203)


def test_color_bulb():
    bulb = light(LIGHT_CWS)

    assert bulb.hex_color == "f1e0b5"
    #  assert bulb.xy_color == (32768, 15729) # temporarily disable


def test_color_bulb_custom_color():
    bulb = light(LIGHT_CWS_CUSTOM_COLOR)

    assert bulb.hex_color == "0"
    #  assert bulb.xy_color == (23327, 33940) # temporarily disable


def test_setters():
    cmd = Device(LIGHT_CWS).light_control.set_predefined_color("Warm glow")
    assert cmd.data == {"3311": [{"5706": "efd275"}]}

    with pytest.raises(error.ColorError):
        Device(LIGHT_CWS).light_control.set_predefined_color("Ggravlingen")
