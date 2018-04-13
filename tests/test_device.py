from datetime import datetime
import pytest

from pytradfri.const import (
    ROOT_DEVICES,
    ATTR_NAME,
    ATTR_LIGHT_CONTROL,
    ATTR_LAST_SEEN,
    ATTR_LIGHT_COLOR_SATURATION,
    ATTR_LIGHT_COLOR_HUE,
    ATTR_LIGHT_DIMMER,
    ATTR_TRANSITION_TIME,
    ATTR_LIGHT_COLOR_X,
    ATTR_LIGHT_COLOR_Y,
    ATTR_LIGHT_MIREDS,
    ATTR_LIGHT_STATE,
    ATTR_LIGHT_COLOR_HEX
)
from pytradfri.device import Device
from devices import (
    LIGHT_WS, LIGHT_CWS, REMOTE_CONTROL)


@pytest.fixture
def device():
    return Device(LIGHT_WS)


@pytest.fixture
def device_remote():
    return Device(REMOTE_CONTROL)


def test_device_properties():
    dev = Device(LIGHT_WS)

    assert dev.application_type == 2
    assert dev.name == 'Löng name containing viking lättårs [letters]'
    assert dev.id == 65539
    assert dev.created_at == datetime.utcfromtimestamp(1509923713)
    assert dev.reachable
    assert dev.path == [ROOT_DEVICES, 65539]


def test_device_info_properties():
    info = Device(LIGHT_WS).device_info

    assert info.manufacturer == 'IKEA of Sweden'
    assert info.model_number == 'TRADFRI bulb E27 WS opal 980lm'
    assert info.firmware_version == '1.2.217'
    assert info.power_source == 1
    assert info.power_source_str == 'Internal Battery'


def test_set_name():
    dev = Device(LIGHT_WS)
    command = dev.set_name('New name')

    assert command.method == 'put'
    assert command.path == dev.path
    assert command.data == {ATTR_NAME: 'New name'}


def test_binary_division():
    dev_ws = Device(LIGHT_WS).light_control.lights[0]
    dev_color = Device(LIGHT_CWS).light_control.lights[0]

    assert dev_ws.dimmer == 254
    assert dev_ws.color_temp == 400
    assert dev_color.hex_color == 'f1e0b5'
    assert dev_color.xy_color == (30015, 26870)


# Testing set_hsb function
def test_set_hsb_valid(device):
    expected = {
        ATTR_LIGHT_COLOR_HUE: 300,
        ATTR_LIGHT_COLOR_SATURATION: 200,
        ATTR_LIGHT_DIMMER: 100
    }
    command = device.light_control.set_hsb(300, 200, 100)
    data = command.data[ATTR_LIGHT_CONTROL][0]
    assert data == expected


def test_set_hsb_without_setting_brightness(device):
    expected = {
        ATTR_LIGHT_COLOR_HUE: 300,
        ATTR_LIGHT_COLOR_SATURATION: 200
    }
    command = device.light_control.set_hsb(300, 200)
    data = command.data[ATTR_LIGHT_CONTROL][0]
    assert data == expected


def test_set_hsb_setting_brightness_none(device):
    expected = {
        ATTR_LIGHT_COLOR_HUE: 300,
        ATTR_LIGHT_COLOR_SATURATION: 200
    }
    command = device.light_control.set_hsb(300, 200, None)
    data = command.data[ATTR_LIGHT_CONTROL][0]
    assert data == expected


def test_set_hsb_setting_hue_none(device):
    expected = {
        ATTR_LIGHT_COLOR_HUE: None,
        ATTR_LIGHT_COLOR_SATURATION: 200
    }
    command = device.light_control.set_hsb(None, 200)
    data = command.data[ATTR_LIGHT_CONTROL][0]
    assert data == expected


def test_set_hsb_with_transitiontime(device):
    expected = {
        ATTR_LIGHT_COLOR_HUE: 300,
        ATTR_LIGHT_COLOR_SATURATION: 200,
        ATTR_LIGHT_DIMMER: 100,
        ATTR_TRANSITION_TIME: 2
    }
    command = device.light_control.set_hsb(300, 200, 100, transition_time=2)
    data = command.data[ATTR_LIGHT_CONTROL][0]
    assert data == expected


def test_set_hsb_with_faulty_transitiontime(device):
    expected = {
        ATTR_LIGHT_COLOR_HUE: 300,
        ATTR_LIGHT_COLOR_SATURATION: 200,
        ATTR_LIGHT_DIMMER: 100,
        ATTR_TRANSITION_TIME: -2
    }
    command = device.light_control.set_hsb(300, 200, 100, transition_time=-2)
    data = command.data[ATTR_LIGHT_CONTROL][0]
    assert data == expected


# Testing set_xy_color function
def test_set_xy_color_with_xy_valid(device):
    expected = {
        ATTR_LIGHT_COLOR_X: 300,
        ATTR_LIGHT_COLOR_Y: 200,
    }
    command = device.light_control.set_xy_color(300, 200)
    data = command.data[ATTR_LIGHT_CONTROL][0]
    assert data == expected


def test_set_xy_color_without_x(device):
    expected = {
        ATTR_LIGHT_COLOR_X: None,
        ATTR_LIGHT_COLOR_Y: 200,
    }
    command = device.light_control.set_xy_color(None, 200)
    data = command.data[ATTR_LIGHT_CONTROL][0]
    assert data == expected


def test_set_xy_color_without_xy(device):
    expected = {
        ATTR_LIGHT_COLOR_X: None,
        ATTR_LIGHT_COLOR_Y: None,
    }
    command = device.light_control.set_xy_color(None, None)
    data = command.data[ATTR_LIGHT_CONTROL][0]
    assert data == expected


def test_set_xy_color_with_transitiontime(device):
    expected = {
        ATTR_LIGHT_COLOR_X: 300,
        ATTR_LIGHT_COLOR_Y: 200,
        ATTR_TRANSITION_TIME: 2
    }
    command = device.light_control.set_xy_color(300, 200, transition_time=2)
    data = command.data[ATTR_LIGHT_CONTROL][0]
    assert data == expected


# Testing set_color_temp function
def test_set_color_temp_valid(device):
    expected = {
        ATTR_LIGHT_MIREDS: 300,
    }
    command = device.light_control.set_color_temp(300)
    data = command.data[ATTR_LIGHT_CONTROL][0]
    assert data == expected


def test_set_color_temp_none(device):
    expected = {
        ATTR_LIGHT_MIREDS: None,
    }
    command = device.light_control.set_color_temp(None)
    data = command.data[ATTR_LIGHT_CONTROL][0]
    assert data == expected


def test_set_color_temp_with_transitiontime(device):
    expected = {
        ATTR_LIGHT_MIREDS: 300,
        ATTR_TRANSITION_TIME: 2
    }
    command = device.light_control.set_color_temp(300, transition_time=2)
    data = command.data[ATTR_LIGHT_CONTROL][0]
    assert data == expected


# Testing set_dimmer function
def test_set_dimmer_valid(device):
    expected = {
        ATTR_LIGHT_DIMMER: 200,
    }
    command = device.light_control.set_dimmer(200)
    data = command.data[ATTR_LIGHT_CONTROL][0]
    assert data == expected


def test_set_dimmer_none(device):
    expected = {
        ATTR_LIGHT_DIMMER: None,
    }
    command = device.light_control.set_dimmer(None)
    data = command.data[ATTR_LIGHT_CONTROL][0]
    assert data == expected


def test_set_dimmer_with_transitiontime(device):
    expected = {
        ATTR_LIGHT_DIMMER: 200,
        ATTR_TRANSITION_TIME: 2
    }
    command = device.light_control.set_dimmer(200, transition_time=2)
    data = command.data[ATTR_LIGHT_CONTROL][0]
    assert data == expected


# Test set_state function
def test_set_state_true(device):
    expected = {
        ATTR_LIGHT_STATE: True,
    }
    command = device.light_control.set_state(True)
    data = command.data[ATTR_LIGHT_CONTROL][0]
    assert data == expected


def test_set_state_false(device):
    expected = {
        ATTR_LIGHT_STATE: False,
    }
    command = device.light_control.set_state(False)
    data = command.data[ATTR_LIGHT_CONTROL][0]
    assert data == expected


def test_set_state_none(device):
    with pytest.raises(TypeError):
        device.light_control.set_state(None)


# Test set_hex_color function
def test_set_hex_color_valid(device):
    expected = {
        ATTR_LIGHT_COLOR_HEX: "4a418a",
    }
    command = device.light_control.set_hex_color("4a418a")
    data = command.data[ATTR_LIGHT_CONTROL][0]
    assert data == expected


def test_set_hex_color_invalid(device):
    expected = {
        ATTR_LIGHT_COLOR_HEX: "RandomString",
    }
    command = device.light_control.set_hex_color("RandomString")
    data = command.data[ATTR_LIGHT_CONTROL][0]
    assert data == expected


def test_set_hex_color_with_transitiontime(device):
    expected = {
        ATTR_LIGHT_COLOR_HEX: "4a418a",
        ATTR_TRANSITION_TIME: 2

    }
    command = device.light_control.set_hex_color("4a418a", transition_time=2)
    data = command.data[ATTR_LIGHT_CONTROL][0]
    assert data == expected


# Test has_light_control function
def test_has_light_control_true(device):
    dev = Device(device.raw.copy())
    dev.raw[ATTR_LIGHT_CONTROL] = {1: 2}
    assert dev.has_light_control is True


def test_has_light_control_false(device):
    dev = Device(device.raw.copy())
    dev.raw[ATTR_LIGHT_CONTROL] = {}
    assert dev.has_light_control is False


# Test light state function
def test_light_state_on(device):
    light = Device(device.raw.copy()).light_control.lights[0]
    light.raw[ATTR_LIGHT_STATE] = 1
    assert light.state is True


def test_light_state_off(device):
    light = Device(device.raw.copy()).light_control.lights[0]
    light.raw[ATTR_LIGHT_STATE] = 0
    assert light.state is False


def test_light_state_mangled(device):
    light = Device(device.raw.copy()).light_control.lights[0]
    light.raw[ATTR_LIGHT_STATE] = "RandomString"
    assert light.state is False


# Test light hsb_xy_color function
def test_light_hsb_xy_color(device):
    """
    Very basic test, just to touch it.
    """
    light = Device(device.raw.copy()).light_control.lights[0]
    assert len(light.hsb_xy_color) == 5


# Test last_seen function
def test_last_seen_valid(device):
    assert device.last_seen is not None


def test_last_seen_none():
    tmp = LIGHT_WS
    del tmp[ATTR_LAST_SEEN]
    dev = Device(tmp)
    assert dev.last_seen is None


# Test _value_validate function
def test_value_validate_lower_edge(device):
    rnge = (10, 100)
    with pytest.raises(ValueError):
        device.light_control._value_validate(9, rnge)
    assert device.light_control._value_validate(10, rnge) is None
    assert device.light_control._value_validate(11, rnge) is None


def test_value_validate_upper_edge(device):
    rnge = (10, 100)
    assert device.light_control._value_validate(99, rnge) is None
    assert device.light_control._value_validate(100, rnge) is None
    with pytest.raises(ValueError):
        device.light_control._value_validate(101, rnge)


def test_value_validate_none(device):
    rnge = (10, 100)
    assert device.light_control._value_validate(None, rnge) is None


# Test deviceInfo serial function
def test_deviceinfo_serial(device):
    info = Device(device.raw.copy()).device_info
    info.raw['2'] = "SomeRandomSerial"
    assert info.serial == "SomeRandomSerial"


# Test deviceInfo power_source_str function
def test_deviceinfo_power_source_str_known(device):
    info = Device(device.raw.copy()).device_info
    assert info.power_source_str is not None


def test_deviceinfo_power_source_str_unknown(device):
    info = Device(device.raw.copy()).device_info
    info.raw['6'] = None
    assert info.power_source_str is 'Unknown'


# Test deviceInfo battery_level function
def test_deviceinfo_battery_level_known(device_remote):
    info = Device(device_remote.raw.copy()).device_info
    assert type(info.battery_level) is int
    assert info.battery_level >= 0
    assert info.battery_level <= 100


# Test deviceInfo battery_level function
def test_deviceinfo_battery_level_unkown(device_remote):
    info = Device(device_remote.raw.copy()).device_info
    info.raw['9'] = None
    assert info.battery_level is None
