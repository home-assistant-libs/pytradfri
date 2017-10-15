from pytradfri.device import Device

LIGHT_W = {
    '3': {
        '0': 'IKEA of Sweden',
        '1': 'TRADFRI bulb E27 opal 1000lm',
        '2': '',
        '3': '1.2.214',
        '6': 1
    },
    '3311': [
        {
            '5850': 1,
            '5851': 96,
            '9003': 0
        }
    ],
    '5750': 2,
    '9001': 'Light W name',
    '9002': 1494695583,
    '9003': 65545,
    '9019': 1,
    '9020': 1507969307,
    '9054': 0
}

LIGHT_WS = {
    '3': {
        '0': 'IKEA of Sweden',
        '1': 'TRADFRI bulb E27 WS opal 980lm',
        '2': '',
        '3': '1.2.217',
        '6': 1
    },
    '3311': [
        {
            '5706': 'f1e0b5',
            '5707': 0,
            '5708': 0,
            '5709': 30138,
            '5710': 26909,
            '5711': 0,
            '5850': 1,
            '5851': 157,
            '9003': 0
        }
    ],
    '5750': 2,
    '9001': 'Light WS name',
    '9002': 1491149680,
    '9003': 65537,
    '9019': 1,
    '9020': 1507970265,
    '9054': 0
}

LIGHT_WS_CUSTOM_COLOR = {
    '3': {
        '6': 1,
        '0': 'IKEA of Sweden',
        '1': 'TRADFRI bulb E27 WS opal 980lm',
        '2': '',
        '3': '1.2.217'
    },
    '3311': [
        {
            '5706': '0',
            '5707': 0,
            '5708': 0,
            '5709': 32228,
            '5710': 27203,
            '5711': 0,
            '5850': 1,
            '5851': 157,
            '9003': 0
        }
    ],
    '5750': 2,
    '9001': 'Light WS name',
    '9002': 1491149680,
    '9003': 65537,
    '9019': 1,
    '9020': 1507986461,
    '9054': 0
}


LIGHT_CWS = {
    '3': {
        '6': 1,
        '0': 'IKEA of Sweden',
        '1': 'TRADFRI bulb E27 CWS opal 600lm',
        '2': '',
        '3': '1.3.002'
    },
    '3311': [
        {
            '5706': 'd9337c',
            '5707': 0,
            '5708': 0,
            '5709': 32768,
            '5710': 15729,
            '5711': 0,
            '5850': 1,
            '5851': 254,
            '9003': 0
        }
    ],
    '5750': 2,
    '9001': 'Light CWS name',
    '9002': 1506114735,
    '9003': 65544,
    '9019': 1,
    '9020': 1507970551,
    '9054': 0
}

LIGHT_CWS_CUSTOM_COLOR = {
    '3': {
        '0': 'IKEA of Sweden',
        '1': 'TRADFRI bulb E27 CWS opal 600lm',
        '2': '',
        '3': '1.3.002',
        '6': 1
    },
    '3311': [
        {
            '5706': '0',
            '5707': 0,
            '5708': 0,
            '5709': 23327,
            '5710': 33940,
            '5711': 0,
            '5850': 1,
            '5851': 254,
            '9003': 0
        }
    ],
    '5750': 2,
    '9001': 'Light CWS name',
    '9002': 1506114735,
    '9003': 65544,
    '9019': 1,
    '9020': 1507970551,
    '9054': 0,
}


def light(raw):
    return Device(raw).light_control.lights[0]


def test_white_bulb():
    bulb = light(LIGHT_W)

    assert bulb.hex_color_raw is None
    assert bulb.hex_color == 'c19b57'
    assert bulb.xy_color_raw == (None, None)
    assert bulb.xy_color == (30101, 26913)
    assert bulb.kelvin_color == 2700


def test_spectrum_bulb():
    bulb = light(LIGHT_WS)

    assert bulb.hex_color_raw == 'f1e0b5'
    assert bulb.hex_color == 'f1e0b5'
    assert bulb.xy_color_raw == (30138, 26909)
    assert bulb.xy_color == (30138, 26909)
    assert bulb.kelvin_color == 2697


def test_spectrum_bulb_custom_color():
    bulb = light(LIGHT_WS_CUSTOM_COLOR)

    assert bulb.hex_color_raw == '0'
    assert bulb.hex_color == 'f9bc5a'
    assert bulb.xy_color_raw == (32228, 27203)
    assert bulb.xy_color == (32228, 27203)
    assert bulb.kelvin_color == 2325


def test_color_bulb():
    bulb = light(LIGHT_CWS)

    assert bulb.hex_color_raw == 'd9337c'
    assert bulb.hex_color == 'd9337c'
    assert bulb.xy_color_raw == (32768, 15729)
    assert bulb.xy_color == (32768, 15729)
    assert bulb.kelvin_color == 4866


def test_color_bulb_custom_color():
    bulb = light(LIGHT_CWS_CUSTOM_COLOR)

    assert bulb.hex_color_raw == '0'
    assert bulb.hex_color == 'cdff67'
    assert bulb.xy_color_raw == (23327, 33940)
    assert bulb.xy_color == (23327, 33940)
    assert bulb.kelvin_color == 5046
