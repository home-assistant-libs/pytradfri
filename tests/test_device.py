"""Test Device."""

from copy import deepcopy
from datetime import datetime, timezone

import pytest

from pytradfri import error
from pytradfri.const import (
    ATTR_DEVICE_INFO,
    ATTR_DEVICE_STATE,
    ATTR_LAST_SEEN,
    ATTR_LIGHT_COLOR_HEX,
    ATTR_LIGHT_COLOR_HUE,
    ATTR_LIGHT_COLOR_SATURATION,
    ATTR_LIGHT_COLOR_X,
    ATTR_LIGHT_COLOR_Y,
    ATTR_LIGHT_CONTROL,
    ATTR_LIGHT_DIMMER,
    ATTR_LIGHT_MIREDS,
    ATTR_NAME,
    ATTR_SWITCH_PLUG,
    ATTR_TRANSITION_TIME,
    ROOT_DEVICES,
)
from pytradfri.device import Device

from .devices import (
    BLIND,
    DEVICE_WITHOUT_FIRMWARE_VERSION,
    LIGHT_CWS,
    LIGHT_PHILIPS,
    LIGHT_W,
    LIGHT_WS,
    MOTION_SENSOR,
    OUTLET,
    REMOTE_CONTROL,
)


@pytest.fixture(name="device")
def device_fixture(request: pytest.FixtureRequest) -> Device:
    """Return device."""
    if hasattr(request, "param"):
        response = deepcopy(request.param)
    else:
        response = deepcopy(LIGHT_WS)
    return Device(response)


input_devices = (
    ("comment", "device"),
    [
        ("Remote control", REMOTE_CONTROL),
        ("Motion sensor", MOTION_SENSOR),
    ],
)

output_devices = (
    ("comment", "device"),
    [
        ("White fixed color bulb", Device(LIGHT_W)),
        ("White spectrum bulb", Device(LIGHT_WS)),
        ("Full color bulb", Device(LIGHT_CWS)),
        ("Philips Hue bulb", Device(LIGHT_PHILIPS)),
    ],
)

wall_plugs = (("comment", "device"), [("Wall plug", Device(OUTLET))])

roller_blinds = (("comment", "device"), [("Blind", Device(BLIND))])

lamp_value_setting_test_cases = [
    ["function_name", "comment", "test_input", "expected_result"],
    [
        [
            "set_hsb",
            "valid",
            {"hue": 300, "saturation": 200, "brightness": 100},
            {
                ATTR_LIGHT_COLOR_HUE: 300,
                ATTR_LIGHT_COLOR_SATURATION: 200,
                ATTR_LIGHT_DIMMER: 100,
            },
        ],
        [
            "set_hsb",
            "without_setting_brightness",
            {"hue": 300, "saturation": 200},
            {ATTR_LIGHT_COLOR_HUE: 300, ATTR_LIGHT_COLOR_SATURATION: 200},
        ],
        [
            "set_hsb",
            "setting_brightness_none",
            {"hue": 300, "saturation": 200, "brightness": None},
            {ATTR_LIGHT_COLOR_HUE: 300, ATTR_LIGHT_COLOR_SATURATION: 200},
        ],
        [
            "set_hsb",
            "setting_hue_none",
            {"hue": None, "saturation": 200},
            {ATTR_LIGHT_COLOR_HUE: None, ATTR_LIGHT_COLOR_SATURATION: 200},
        ],
        [
            "set_hsb",
            "with_transition_time",
            {"hue": 300, "saturation": 200, "brightness": 100, "transition_time": 2},
            {
                ATTR_LIGHT_COLOR_HUE: 300,
                ATTR_LIGHT_COLOR_SATURATION: 200,
                ATTR_LIGHT_DIMMER: 100,
                ATTR_TRANSITION_TIME: 2,
            },
        ],
        [
            "set_hsb",
            "with_faulty_transition_time",
            {"hue": 300, "saturation": 200, "transition_time": -2},
            {
                ATTR_LIGHT_COLOR_HUE: 300,
                ATTR_LIGHT_COLOR_SATURATION: 200,
                ATTR_TRANSITION_TIME: -2,
            },
        ],
        [
            "set_xy_color",
            "valid",
            {
                "color_x": 300,
                "color_y": 200,
            },
            {
                ATTR_LIGHT_COLOR_X: 300,
                ATTR_LIGHT_COLOR_Y: 200,
            },
        ],
        [
            "set_xy_color",
            "without_x",
            {
                "color_x": None,
                "color_y": 200,
            },
            {
                ATTR_LIGHT_COLOR_X: None,
                ATTR_LIGHT_COLOR_Y: 200,
            },
        ],
        [
            "set_xy_color",
            "without_xy",
            {
                "color_x": None,
                "color_y": None,
            },
            {
                ATTR_LIGHT_COLOR_X: None,
                ATTR_LIGHT_COLOR_Y: None,
            },
        ],
        [
            "set_xy_color",
            "with_transition_time",
            {"color_x": 300, "color_y": 200, "transition_time": 2},
            {ATTR_LIGHT_COLOR_X: 300, ATTR_LIGHT_COLOR_Y: 200, ATTR_TRANSITION_TIME: 2},
        ],
        [
            "set_color_temp",
            "valid",
            {
                "color_temp": 300,
            },
            {
                ATTR_LIGHT_MIREDS: 300,
            },
        ],
        [
            "set_color_temp",
            "none",
            {
                "color_temp": None,
            },
            {
                ATTR_LIGHT_MIREDS: None,
            },
        ],
        [
            "set_color_temp",
            "with_transition_time",
            {"color_temp": 300, "transition_time": 2},
            {ATTR_LIGHT_MIREDS: 300, ATTR_TRANSITION_TIME: 2},
        ],
        [
            "set_dimmer",
            "valid",
            {
                "dimmer": 200,
            },
            {
                ATTR_LIGHT_DIMMER: 200,
            },
        ],
        [
            "set_dimmer",
            "none",
            {
                "dimmer": None,
            },
            {
                ATTR_LIGHT_DIMMER: None,
            },
        ],
        [
            "set_dimmer",
            "with_transition_time",
            {"dimmer": 200, "transition_time": 2},
            {ATTR_LIGHT_DIMMER: 200, ATTR_TRANSITION_TIME: 2},
        ],
        [
            "set_state",
            "true",
            {
                "state": True,
            },
            {
                ATTR_DEVICE_STATE: True,
            },
        ],
        [
            "set_state",
            "false",
            {
                "state": False,
            },
            {
                ATTR_DEVICE_STATE: False,
            },
        ],
        [
            "set_hex_color",
            "valid",
            {
                "color": "4a418a",
            },
            {
                ATTR_LIGHT_COLOR_HEX: "4a418a",
            },
        ],
        [
            "set_hex_color",
            "invalid",
            {
                "color": "RandomString",
            },
            {
                ATTR_LIGHT_COLOR_HEX: "RandomString",
            },
        ],
        [
            "set_hex_color",
            "with_transition_time",
            {"color": "4a418a", "transition_time": 2},
            {ATTR_LIGHT_COLOR_HEX: "4a418a", ATTR_TRANSITION_TIME: 2},
        ],
        [
            "set_predefined_color",
            "valid",
            {"colorname": "Saturated Purple"},
            {
                ATTR_LIGHT_COLOR_HEX: "8f2686",
            },
        ],
        [
            "set_predefined_color",
            "with_transition_time",
            {"colorname": "Saturated Purple", "transition_time": 2},
            {ATTR_LIGHT_COLOR_HEX: "8f2686", ATTR_TRANSITION_TIME: 2},
        ],
    ],
]

# Combine lamp_value_setting_test_cases and output_devices where:
# len(new) = len(a) * len(b)
src = lamp_value_setting_test_cases[1] * len(output_devices[1])
new_list = []
for i, src_item in enumerate(src):
    index = int((i / len(src)) * len(output_devices[1]))
    new_list.append(
        [src_item[0], src_item[1], src_item[2], src_item[3], output_devices[1][index]]
    )
lamp_value_setting_test_cases[0].append("device")
lamp_value_setting_test_cases[1] = new_list


@pytest.mark.parametrize(*lamp_value_setting_test_cases)
def test_lamp_value_setting(
    function_name, comment, test_input, expected_result, device
):
    """Test lamp value."""
    function = getattr(device[1].light_control, function_name)
    command = function(**test_input)
    data = command.data[ATTR_LIGHT_CONTROL][0]
    assert data == expected_result


@pytest.mark.parametrize(
    ["function_name", "comment", "test_input", "expected_result"],
    [
        [
            "set_state",
            "true",
            {
                "state": True,
            },
            {
                ATTR_DEVICE_STATE: True,
            },
        ],
        [
            "set_state",
            "false",
            {
                "state": False,
            },
            {
                ATTR_DEVICE_STATE: False,
            },
        ],
    ],
)
def test_socket_value_setting(function_name, comment, test_input, expected_result):
    """Test socket values."""
    function = getattr(Device(deepcopy(OUTLET)).socket_control, function_name)
    command = function(**test_input)
    data = command.data[ATTR_SWITCH_PLUG][0]
    assert data == expected_result


def test_socket_state_off():
    """Test socket off."""
    socket_response = deepcopy(OUTLET)
    socket_response[ATTR_SWITCH_PLUG][0][ATTR_DEVICE_STATE] = 0

    socket = Device(socket_response).socket_control.sockets[0]
    assert socket.state is False


def test_socket_state_on():
    """Test socket on."""
    socket_response = deepcopy(OUTLET)
    socket_response[ATTR_SWITCH_PLUG][0][ATTR_DEVICE_STATE] = 1

    socket = Device(socket_response).socket_control.sockets[0]
    assert socket.state is True


def test_set_predefined_color_invalid(device):
    """Test set invalid color."""
    with pytest.raises(error.ColorError):
        device.light_control.set_predefined_color("RandomString")


def test_device_properties(device):
    """Test device properties."""
    assert device.application_type == 2
    assert device.name == "Löng name containing viking lättårs [letters]"
    assert device.id == 65539
    assert device.created_at == datetime.fromtimestamp(1509923713, tz=timezone.utc)
    assert device.reachable
    assert device.path == [ROOT_DEVICES, "65539"]


def test_device_info_properties(device):
    """Test device info."""
    info = device.device_info

    assert info.manufacturer == "IKEA of Sweden"
    assert info.model_number == "TRADFRI bulb E27 WS opal 980lm"
    assert info.firmware_version == "1.2.217"
    assert info.power_source == 1
    assert info.power_source_str == "Internal Battery"


@pytest.mark.parametrize(
    "device", [DEVICE_WITHOUT_FIRMWARE_VERSION], indirect=["device"]
)
def test_device_without_firmware_version(device):
    """Test device without firmware version."""
    assert device.device_info.firmware_version is None


def test_set_name(device):
    """Test set name."""
    command = device.set_name("New name")

    assert command.method == "put"
    assert command.path == device.path
    assert command.data == {ATTR_NAME: "New name"}


def test_binary_division():
    """Test binary division."""
    dev_ws = Device(LIGHT_WS).light_control.lights[0]
    dev_color = Device(LIGHT_CWS).light_control.lights[0]

    assert dev_ws.dimmer == 254
    assert dev_ws.color_temp == 400
    assert dev_color.hex_color == "f1e0b5"
    assert dev_color.xy_color == (30015, 26870)


# Test has_light_control function
def test_has_light_control_true():
    """Test light has control."""
    response = deepcopy(LIGHT_WS)
    dev = Device(response)

    assert dev.has_light_control is True


def test_has_light_control_false():
    """Test light do not have control."""
    response = deepcopy(LIGHT_WS)
    response.pop(ATTR_LIGHT_CONTROL)
    dev = Device(response)

    assert dev.has_light_control is False


# Test light state function
def test_light_state_on():
    """Test light on."""
    device_data = deepcopy(LIGHT_WS)
    device_data[ATTR_LIGHT_CONTROL][0][ATTR_DEVICE_STATE] = 1
    device = Device(device_data)
    light = device.light_control.lights[0]
    assert light.state is True


def test_light_state_off():
    """Test light off."""
    device_data = deepcopy(LIGHT_WS)
    device_data[ATTR_LIGHT_CONTROL][0][ATTR_DEVICE_STATE] = 0
    device = Device(device_data)
    light = device.light_control.lights[0]
    assert light.state is False


def test_light_state_mangled():
    """Test mangled light state."""
    device_data = deepcopy(LIGHT_WS)
    device_data[ATTR_LIGHT_CONTROL][0][ATTR_DEVICE_STATE] = "RandomString"
    with pytest.raises(ValueError):
        device = Device(device_data)
        light = device.light_control.lights[0]
        assert light.state is False


# Test light hsb_xy_color function
def test_light_hsb_xy_color():
    """Very basic test, just to touch it."""
    device_data = deepcopy(LIGHT_CWS)
    device = Device(device_data)
    light = device.light_control.lights[0]
    assert len(light.hsb_xy_color) == 5


# Test last_seen function
def test_last_seen_valid(device):
    """Test last seen."""
    assert device.last_seen is not None


def test_last_seen_none():
    """Test last seen none."""
    response = deepcopy(LIGHT_WS)
    del response[ATTR_LAST_SEEN]
    dev = Device(response)
    assert dev.last_seen is None


# Test _value_validate function
def test_value_validate_lower_edge(device):
    """Test value lower edge."""
    # pylint: disable=protected-access
    rnge = (10, 100)
    with pytest.raises(ValueError):
        device.light_control._value_validate(9, rnge)
    assert device.light_control._value_validate(10, rnge) is None
    assert device.light_control._value_validate(11, rnge) is None


def test_value_validate_upper_edge(device):
    """Test value upper edge."""
    # pylint: disable=protected-access
    rnge = (10, 100)
    assert device.light_control._value_validate(99, rnge) is None
    assert device.light_control._value_validate(100, rnge) is None
    with pytest.raises(ValueError):
        device.light_control._value_validate(101, rnge)


def test_value_validate_none(device):
    """Test value none."""
    # pylint: disable=protected-access
    rnge = (10, 100)
    assert device.light_control._value_validate(None, rnge) is None


# Test deviceInfo serial function
def test_device_info_serial():
    """Test serial number."""
    response = deepcopy(LIGHT_WS)
    response[ATTR_DEVICE_INFO]["2"] = "SomeRandomSerial"
    info = Device(response).device_info

    assert info.serial == "SomeRandomSerial"


# Test deviceInfo power_source_str function
def test_device_info_power_source_str_known():
    """Test power source known."""
    info = Device(deepcopy(LIGHT_WS)).device_info
    assert info.power_source_str is not None
    assert info.power_source_str != "Unknown"


def test_device_info_power_source_str_unknown():
    """Test power source unknown."""
    response = deepcopy(LIGHT_WS)
    response[ATTR_DEVICE_INFO]["6"] = 99999
    info = Device(response).device_info

    assert info.power_source_str == "Unknown"


def test_device_info_power_source_not_present():
    """Test power source not present."""
    response = deepcopy(LIGHT_WS)
    del response[ATTR_DEVICE_INFO]["6"]
    info = Device(response).device_info

    assert info.power_source_str is None


# Test deviceInfo battery_level function
@pytest.mark.parametrize(*input_devices, indirect=["device"])
def test_device_info_battery_level(comment: str, device: Device) -> None:
    """Test battery level."""
    info = device.device_info
    assert isinstance(info.battery_level, int)
    assert info.battery_level >= 0
    assert info.battery_level <= 100


@pytest.mark.parametrize(*input_devices)
def test_device_info_battery_level_unknown(comment: str, device: Device) -> None:
    """Test battery level unknown."""
    response = deepcopy(device)
    response[ATTR_DEVICE_INFO].pop("9")
    info = Device(response).device_info

    assert info.battery_level is None
