from pytradfri.const import ROOT_DEVICES, ATTR_NAME
from pytradfri.device import Device

LIGHT = {
    '3': {
        '0': 'IKEA of Sweden',
        '1': 'TRADFRI bulb E26 WS opal 980lm',
        '2': '',
        '3': '1.1.1.1-5.7.2.0',
        '6': 1
    },
    '3311': [
        {
            '5706': 'efd275',
            '5707': 0,
            '5708': 0,
            '5709': 33135,
            '5710': 27211,
            '5711': 0,
            '5850': 1,
            '5851': 25,
            '9003': 0
        }
    ],
    '5750': 2,
    '9001': 'Light name',
    '9002': 1491771330,
    '9003': 65537,
    '9019': 1,
    '9020': 1491895812,
    '9054': 0
}


def test_device_properties():
    dev = Device(LIGHT)

    assert dev.application_type == 2
    assert dev.name == 'Light name'
    assert dev.id == 65537
    assert dev.reachable
    assert dev.path == [ROOT_DEVICES, 65537]


def test_device_info_properties():
    info = Device(LIGHT).device_info

    assert info.manufacturer == 'IKEA of Sweden'
    assert info.model_number == 'TRADFRI bulb E26 WS opal 980lm'
    assert info.firmware_version == '1.1.1.1-5.7.2.0'
    assert info.power_source == 1
    assert info.power_source_str == 'Internal Battery'


def test_set_name():
    dev = Device(LIGHT)
    command = dev.set_name('New name')

    assert command.method == 'put'
    assert command.path == dev.path
    assert command.data == {ATTR_NAME: 'New name'}
