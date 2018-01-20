from datetime import datetime
import pytest

from pytradfri.const import ROOT_DEVICES, ATTR_NAME, ATTR_LIGHT_CONTROL
from pytradfri.device import Device
from devices import LIGHT_WS, LIGHT_CWS


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


def test_set_hsb():
    dev = Device(LIGHT_WS)

    with pytest.raises(ValueError):
        dev.light_control.set_hsb(-300, 200, 100)
    with pytest.raises(ValueError):
        dev.light_control.set_hsb(300, -200, 100)
    with pytest.raises(ValueError):
        dev.light_control.set_hsb(300, 200, -100)

    with pytest.raises(ValueError):
        dev.light_control.set_hsb(99999, 200, 100)
    with pytest.raises(ValueError):
        dev.light_control.set_hsb(300, 99999, 100)
    with pytest.raises(ValueError):
        dev.light_control.set_hsb(300, 200, 99999)

    command = dev.light_control.set_hsb(300, 200)
    data = command.data[ATTR_LIGHT_CONTROL][0]
    assert len(data) is 2

    command = dev.light_control.set_hsb(300, 200, None)
    data = command.data[ATTR_LIGHT_CONTROL][0]
    assert len(data) is 2

    command = dev.light_control.set_hsb(300, 200, 100)
    data = command.data[ATTR_LIGHT_CONTROL][0]
    assert len(data) is 3

    command = dev.light_control.set_hsb(300, 200, 100, transition_time=1)
    data = command.data[ATTR_LIGHT_CONTROL][0]
    assert len(data) is 4


def test_value_validate():
    dev = Device(LIGHT_WS)
    rnge = (10, 100)

    with pytest.raises(ValueError):
        dev.light_control._value_validate(9, rnge)
    with pytest.raises(ValueError):
        dev.light_control._value_validate(-1, rnge)
    with pytest.raises(ValueError):
        dev.light_control._value_validate(101, rnge)

    assert dev.light_control._value_validate(10, rnge) is None
    assert dev.light_control._value_validate(50, rnge) is None
    assert dev.light_control._value_validate(100, rnge) is None
    assert dev.light_control._value_validate(None, rnge) is None
