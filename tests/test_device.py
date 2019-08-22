from datetime import datetime
import pytest

from pytradfri import error
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
    ATTR_DEVICE_STATE,
    ATTR_LIGHT_COLOR_HEX,
    ATTR_SWITCH_PLUG
)
from pytradfri.device import Device
from devices import (
    LIGHT_W, LIGHT_WS, LIGHT_CWS, LIGHT_PHILIPS, REMOTE_CONTROL,
    MOTION_SENSOR, OUTLET, BLIND)


@pytest.fixture
def device():
    return Device(LIGHT_WS)


input_devices = (
    ("comment", "device"),
    [
        ("Remote control", Device(REMOTE_CONTROL)),
        ("Motion sensor", Device(MOTION_SENSOR)),
    ]
)

output_devices = (
    ("comment", "device"),
    [
        ("White fixed color bulb", Device(LIGHT_W)),
        ("White spectrum bulb", Device(LIGHT_WS)),
        ("Full color bulb", Device(LIGHT_CWS)),
        ("Philips Hue bulb", Device(LIGHT_PHILIPS)),
    ]
)

wall_plugs = (
    ("comment", "device"),
    [
        ("Wall plug", Device(OUTLET))
    ]
)

roller_blinds = (
    ("comment", "device"),
    [
        ("Blind", Device(BLIND))
    ]
)

lamp_value_setting_test_cases = [
    ["function_name", "comment", "test_input", "expected_result"],
    [
        [
            "set_hsb", "valid", {
                'hue': 300,
                'saturation': 200,
                'brightness': 100
            }, {
                ATTR_LIGHT_COLOR_HUE: 300,
                ATTR_LIGHT_COLOR_SATURATION: 200,
                ATTR_LIGHT_DIMMER: 100
            }
        ],
        [
            "set_hsb", "without_setting_brightness", {
                'hue': 300,
                'saturation': 200
            }, {
                ATTR_LIGHT_COLOR_HUE: 300,
                ATTR_LIGHT_COLOR_SATURATION: 200
            },
        ],
        [
            "set_hsb", "setting_brightness_none", {
                'hue': 300,
                'saturation': 200,
                'brightness': None
            }, {
                ATTR_LIGHT_COLOR_HUE: 300,
                ATTR_LIGHT_COLOR_SATURATION: 200
            },
        ],
        [
            "set_hsb", "setting_hue_none", {
                'hue': None,
                'saturation': 200
            }, {
                ATTR_LIGHT_COLOR_HUE: None,
                ATTR_LIGHT_COLOR_SATURATION: 200
            },
        ],
        [
            "set_hsb", "with_transitiontime", {
                'hue': 300,
                'saturation': 200,
                'brightness': 100,
                'transition_time': 2
            }, {
                ATTR_LIGHT_COLOR_HUE: 300,
                ATTR_LIGHT_COLOR_SATURATION: 200,
                ATTR_LIGHT_DIMMER: 100,
                ATTR_TRANSITION_TIME: 2
            },
        ],
        [
            "set_hsb", "with_faulty_transitiontime", {
                'hue': 300,
                'saturation': 200,
                'transition_time': -2
            }, {
                ATTR_LIGHT_COLOR_HUE: 300,
                ATTR_LIGHT_COLOR_SATURATION: 200,
                ATTR_TRANSITION_TIME: -2
            },
        ],

        [
            "set_xy_color", "valid", {
                'color_x': 300,
                'color_y': 200,
            }, {
                ATTR_LIGHT_COLOR_X: 300,
                ATTR_LIGHT_COLOR_Y: 200,
            },
        ],
        [
            "set_xy_color", "without_x", {
                'color_x': None,
                'color_y': 200,
            }, {
                ATTR_LIGHT_COLOR_X: None,
                ATTR_LIGHT_COLOR_Y: 200,
            },
        ],
        [
            "set_xy_color", "without_xy", {
                'color_x': None,
                'color_y': None,
            }, {
                ATTR_LIGHT_COLOR_X: None,
                ATTR_LIGHT_COLOR_Y: None,
            },
        ],
        [
            "set_xy_color", "with_transitiontime", {
                'color_x': 300,
                'color_y': 200,
                'transition_time': 2
            }, {
                ATTR_LIGHT_COLOR_X: 300,
                ATTR_LIGHT_COLOR_Y: 200,
                ATTR_TRANSITION_TIME: 2
            },
        ],

        [
            "set_color_temp", "valid", {
                'color_temp': 300,
            }, {
                ATTR_LIGHT_MIREDS: 300,
            },
        ],
        [
            "set_color_temp", "none", {
                'color_temp': None,
            }, {
                ATTR_LIGHT_MIREDS: None,
            },
        ],
        [
            "set_color_temp", "with_transitiontime", {
                'color_temp': 300,
                'transition_time': 2
            }, {
                ATTR_LIGHT_MIREDS: 300,
                ATTR_TRANSITION_TIME: 2
            },
        ],

        [
            "set_dimmer", "valid", {
                'dimmer': 200,
            }, {
                ATTR_LIGHT_DIMMER: 200,
            },
        ],
        [
            "set_dimmer", "none", {
                'dimmer': None,
            }, {
                ATTR_LIGHT_DIMMER: None,
            },
        ],
        [
            "set_dimmer", "with_transitiontime", {
                'dimmer': 200,
                'transition_time': 2
            }, {
                ATTR_LIGHT_DIMMER: 200,
                ATTR_TRANSITION_TIME: 2
            },
        ],

        [
            "set_state", "true", {
                'state': True,
            }, {
                ATTR_DEVICE_STATE: True,
            },
        ],
        [
            "set_state", "false", {
                'state': False,
            }, {
                ATTR_DEVICE_STATE: False,
            },
        ],

        [
            "set_hex_color", "valid", {
                'color': '4a418a',
            }, {
                ATTR_LIGHT_COLOR_HEX: '4a418a',
            },
        ],
        [
            "set_hex_color", "invalid", {
                'color': 'RandomString',
            }, {
                ATTR_LIGHT_COLOR_HEX: 'RandomString',
            },
        ],
        [
            "set_hex_color", "with_transitiontime", {
                'color': '4a418a',
                'transition_time': 2
            }, {
                ATTR_LIGHT_COLOR_HEX: '4a418a',
                ATTR_TRANSITION_TIME: 2
            },
        ],

        [
            "set_predefined_color", "valid", {
                'colorname': 'Saturated Purple'
            }, {
                ATTR_LIGHT_COLOR_HEX: '8f2686',
            },
        ],
        [
            "set_predefined_color", "with_transitiontime", {
                'colorname': 'Saturated Purple',
                'transition_time': 2
            }, {
                ATTR_LIGHT_COLOR_HEX: '8f2686',
                ATTR_TRANSITION_TIME: 2
            },
        ],
    ]
]

socket_value_setting_test_cases = [
    ["function_name", "comment", "test_input", "expected_result"],
    [
        [
            "set_state", "true", {
                'state': True,
            }, {
                ATTR_DEVICE_STATE: True,
            },
        ],
        [
            "set_state", "false", {
                'state': False,
            }, {
                ATTR_DEVICE_STATE: False,
            },
        ],
    ]
]

# Combine lamp_value_setting_test_cases and output_devices where:
# len(new) = len(a) * len(b)
src = lamp_value_setting_test_cases[1] * len(output_devices[1])
newList = []
for i in range(len(src)):
    index = int((i / len(src)) * len(output_devices[1]))
    newList.append([
        src[i][0], src[i][1], src[i][2], src[i][3], output_devices[1][index]
    ])
lamp_value_setting_test_cases[0].append("device")
lamp_value_setting_test_cases[1] = newList


@pytest.mark.parametrize(*lamp_value_setting_test_cases)
def test_lamp_value_setting(function_name, comment,
                            test_input, expected_result, device):
    function = getattr(device[1].light_control, function_name)
    command = function(**test_input)
    data = command.data[ATTR_LIGHT_CONTROL][0]
    assert data == expected_result


@pytest.mark.parametrize(*socket_value_setting_test_cases)
def test_socket_value_setting(function_name, comment,
                              test_input, expected_result, device):
    if device.has_socket_control:
        function = getattr(device[0].socket_control, function_name)
        command = function(**test_input)
        data = command.data[ATTR_SWITCH_PLUG][0]
        assert data == expected_result


def test_socket_state_off(device):
    if device.has_socket_control:
        socket = Device(device.raw.copy()).socket_control.socket[0]
        socket.raw[ATTR_DEVICE_STATE] = 0
        assert socket.state is False


def test_socket_state_on(device):
    if device.has_socket_control:
        socket = Device(device.raw.copy()).socket_control.socket[0]
        socket.raw[ATTR_DEVICE_STATE] = 1
        assert socket.state is True


def test_set_state_none(device):
    with pytest.raises(TypeError):
        device.light_control.set_state(None)


def test_set_predefined_color_invalid(device):
    with pytest.raises(error.ColorError):
        device.light_control.set_predefined_color("RandomString")


def test_device_properties(device):
    assert device.application_type == 2
    assert device.name == 'Löng name containing viking lättårs [letters]'
    assert device.id == 65539
    assert device.created_at == datetime.utcfromtimestamp(1509923713)
    assert device.reachable
    assert device.path == [ROOT_DEVICES, 65539]


def test_device_info_properties(device):
    info = device.device_info

    assert info.manufacturer == 'IKEA of Sweden'
    assert info.model_number == 'TRADFRI bulb E27 WS opal 980lm'
    assert info.firmware_version == '1.2.217'
    assert info.power_source == 1
    assert info.power_source_str == 'Internal Battery'


def test_set_name(device):
    command = device.set_name('New name')

    assert command.method == 'put'
    assert command.path == device.path
    assert command.data == {ATTR_NAME: 'New name'}


def test_binary_division():
    dev_ws = Device(LIGHT_WS).light_control.lights[0]
    dev_color = Device(LIGHT_CWS).light_control.lights[0]

    assert dev_ws.dimmer == 254
    assert dev_ws.color_temp == 400
    assert dev_color.hex_color == 'f1e0b5'
    assert dev_color.xy_color == (30015, 26870)


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
    light.raw[ATTR_DEVICE_STATE] = 1
    assert light.state is True


def test_light_state_off(device):
    light = Device(device.raw.copy()).light_control.lights[0]
    light.raw[ATTR_DEVICE_STATE] = 0
    assert light.state is False


def test_light_state_mangled(device):
    light = Device(device.raw.copy()).light_control.lights[0]
    light.raw[ATTR_DEVICE_STATE] = "RandomString"
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
    assert info.power_source_str != 'Unknown'


def test_deviceinfo_power_source_str_unknown(device):
    info = Device(device.raw.copy()).device_info
    info.raw['6'] = None
    assert info.power_source_str == 'Unknown'


def test_deviceinfo_power_source_not_present(device):
    info = Device(device.raw.copy()).device_info
    del info.raw['6']
    assert info.power_source_str is None


# Test deviceInfo battery_level function
@pytest.mark.parametrize(*input_devices)
def test_deviceinfo_battery_level(comment, device):
    info = Device(device.raw.copy()).device_info
    assert type(info.battery_level) is int
    assert info.battery_level >= 0
    assert info.battery_level <= 100


@pytest.mark.parametrize(*input_devices)
def test_deviceinfo_battery_level_unkown(comment, device):
    info = Device(device.raw.copy()).device_info
    info.raw['9'] = None
    assert info.battery_level is None
