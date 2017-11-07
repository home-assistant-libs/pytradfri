from pytradfri.device import Device
import pytest
from pytradfri import error
from devices import LIGHT_W, LIGHT_WS, LIGHT_WS_CUSTOM_COLOR, LIGHT_CWS,\
    LIGHT_CWS_CUSTOM_COLOR


def light(raw):
    return Device(raw).light_control.lights[0]


def light_device_control(raw):
    return Device(raw).light_control


def test_white_bulb():
    bulb = light(LIGHT_W)

    assert bulb.hex_color is None
    assert bulb.xy_color == (None, None)


def test_spectrum_bulb():
    bulb = light(LIGHT_WS)

    assert bulb.hex_color == 'f1e0b5'
    assert bulb.xy_color == (30138, 26909)


def test_spectrum_bulb_custom_color():
    bulb = light(LIGHT_WS_CUSTOM_COLOR)

    assert bulb.hex_color == '0'
    assert bulb.xy_color == (32228, 27203)


def test_color_bulb():
    bulb = light(LIGHT_CWS)

    assert bulb.hex_color == 'd9337c'
    assert bulb.xy_color == (32768, 15729)


def test_color_bulb_custom_color():
    bulb = light(LIGHT_CWS_CUSTOM_COLOR)

    assert bulb.hex_color == '0'
    assert bulb.xy_color == (23327, 33940)


def test_white_device_control():
    light_control = light_device_control(LIGHT_W)

    assert not light_control.can_set_color
    assert not light_control.can_set_kelvin


def test_spectrum_device_control():
    light_control = light_device_control(LIGHT_WS)

    assert not light_control.can_set_color
    assert light_control.can_set_kelvin
    assert light_control.min_kelvin == 2200
    assert light_control.max_kelvin == 4000


def test_color_device_control():
    light_control = light_device_control(LIGHT_CWS)

    assert light_control.can_set_color
    assert light_control.can_set_kelvin
    assert light_control.min_kelvin == 1667
    assert light_control.max_kelvin == 25000


def test_setters():
    cmd = Device(LIGHT_CWS).light_control \
        .set_predefined_color('Warm glow')
    assert cmd.data == {'3311': [{'5706': 'efd275'}]}

    with pytest.raises(error.ColorError):
        Device(LIGHT_CWS).light_control \
            .set_predefined_color('Ggravlingen')
