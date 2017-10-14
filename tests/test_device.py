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

LIGHT_W = {
    '9054': 0,
    '9001': 'Light W name',
    '9002': 1494695583,
    '9020': 1507969307,
    '9003': 65545,
    '5750': 2,
    '9019': 1,
    '3': {
        '6': 1,
        '0': 'IKEA of Sweden',
        '1': 'TRADFRI bulb E27 opal 1000lm',
        '2': '',
        '3': '1.2.214'
    },
    '3311': [
        {
            '5850': 1,
            '5851': 96,
            '9003': 0
        }
    ]
}

LIGHT_WS = {
    '9054': 0,
    '9001': 'Light WS name',
    '9002': 1491149680,
    '9020': 1507970265,
    '9003': 65537,
    '5750': 2,
    '9019': 1,
    '3': {
        '6': 1,
        '0': 'IKEA of Sweden',
        '1': 'TRADFRI bulb E27 WS opal 980lm',
        '2': '',
        '3': '1.2.217'
    },
    '3311': [
        {
            '5850': 1,
            '5709': 30138,
            '5851': 157,
            '5707': 0,
            '5708': 0,
            '5710': 26909,
            '5711': 0,
            '5706': 'f1e0b5',
            '9003': 0
        }
    ]
}

LIGHT_CWS = {
    '9054': 0,
    '9001': 'Light CWS name',
    '9002': 1506114735,
    '9020': 1507970551,
    '9003': 65544,
    '5750': 2,
    '9019': 1,
    '3': {
        '6': 1,
        '0': 'IKEA of Sweden',
        '1': 'TRADFRI bulb E27 CWS opal 600lm',
        '2': '',
        '3': '1.3.002'
    },
    '3311': [
        {
            '5850': 1,
            '5709': 32768,
            '5851': 254,
            '5707': 0,
            '5708': 0,
            '5710': 15729,
            '5711': 0,
            '5706': 'd9337c',
            '9003': 0
        }
    ]
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
