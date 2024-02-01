"""Devices: Retrieved from Gateway running on 1.2.42."""

LIGHT_W = {
    "3": {
        "0": "IKEA of Sweden",
        "1": "TRADFRI bulb E27 W opal 1000lm",
        "2": "",
        "3": "1.2.214",
        "6": 1,
    },
    "3311": [{"5850": 1, "5851": 254, "9003": 0}],
    "5750": 2,
    "9001": "Hall 1",
    "9002": 1509923551,
    "9003": 65537,
    "9019": 1,
    "9020": 1510009959,
    "9054": 0,
}

#  Retrieved from Gateway running on 1.2.42
LIGHT_WS = {
    "3": {
        "0": "IKEA of Sweden",
        "1": "TRADFRI bulb E27 WS opal 980lm",
        "2": "",
        "3": "1.2.217",
        "6": 1,
    },
    "3311": [
        {
            "5706": "0",
            "5709": 31103,
            "5710": 27007,
            "5711": 400,
            "5850": 1,
            "5851": 254,
            "9003": 0,
        }
    ],
    "5750": 2,
    "9001": "Löng name containing viking lättårs [letters]",
    "9002": 1509923713,
    "9003": 65539,
    "9019": 1,
    "9020": 1510010121,
    "9054": 0,
}

#  Not updated after 1.2.42
LIGHT_WS_CUSTOM_COLOR = {
    "3": {
        "6": 1,
        "0": "IKEA of Sweden",
        "1": "TRADFRI bulb E27 WS opal 980lm",
        "2": "",
        "3": "1.2.217",
    },
    "3311": [
        {
            "5706": "0",
            "5707": 0,
            "5708": 0,
            "5709": 32228,
            "5710": 27203,
            "5711": 454,
            "5850": 1,
            "5851": 157,
            "9003": 0,
        }
    ],
    "5750": 2,
    "9001": "Light WS name",
    "9002": 1491149680,
    "9003": 65537,
    "9019": 1,
    "9020": 1507986461,
    "9054": 0,
}

#  Retrieved from Gateway running on 1.2.42
LIGHT_CWS = {
    "3": {
        "0": "IKEA of Sweden",
        "1": "TRADFRI bulb E27 CWS opal 600lm",
        "2": "",
        "3": "1.3.002",
        "6": 1,
    },
    "3311": [
        {
            "5706": "f1e0b5",
            "5707": 5427,
            "5708": 42596,
            "5709": 30015,
            "5710": 26870,
            "5850": 0,
            "5851": 101,
            "9003": 0,
        }
    ],
    "5750": 2,
    "9001": "Läslampa",
    "9002": 1509924799,
    "9003": 65541,
    "9019": 1,
    "9020": 1510011206,
    "9054": 0,
}

#  Not updated after 1.2.42
LIGHT_CWS_CUSTOM_COLOR = {
    "3": {
        "0": "IKEA of Sweden",
        "1": "TRADFRI bulb E27 CWS opal 600lm",
        "2": "",
        "3": "1.3.002",
        "6": 1,
    },
    "3311": [
        {
            "5706": "0",
            "5707": 0,
            "5708": 0,
            "5709": 23327,
            "5710": 33940,
            "5850": 1,
            "5851": 254,
            "9003": 0,
        }
    ],
    "5750": 2,
    "9001": "Light CWS name",
    "9002": 1506114735,
    "9003": 65544,
    "9019": 1,
    "9020": 1507970551,
    "9054": 0,
}

#  Retrieved from Gateway running on 1.3.14
LIGHT_PHILIPS = {
    "3": {"0": "Philips", "1": "LCT012", "2": "", "3": "1.15.2_r19181", "6": 1},
    "3311": [
        {
            "5706": "0",
            "5707": 13653,
            "5708": 0,
            "5709": 20413,
            "5710": 21477,
            "5711": 0,
            "5717": 0,
            "5850": 1,
            "5851": 254,
            "9003": 0,
        }
    ],
    "5750": 2,
    "9001": "Hue Bulb",
    "9002": 1524306939,
    "9003": 65551,
    "9019": 1,
    "9020": 1525025378,
    "9054": 0,
}

#  Retrieved from Gateway running on 1.2.42
REMOTE_CONTROL = {
    "3": {
        "0": "IKEA of Sweden",
        "1": "TRADFRI remote control",
        "2": "",
        "3": "1.2.214",
        "6": 3,
        "9": 87,
    },
    "5750": 0,
    "9001": "TRADFRI remote control",
    "9002": 1509923521,
    "9003": 65536,
    "9019": 1,
    "9020": 1510010209,
    "9054": 0,
}

#  Retrieved from Gateway running on 1.2.42
MOTION_SENSOR = {
    "3": {
        "0": "IKEA of Sweden",
        "1": "TRADFRI motion sensor",
        "2": "",
        "3": "1.2.214",
        "6": 3,
        "9": 87,
    },
    "3300": [{"9003": 0}],
    "5750": 4,
    "9001": "TRADFRI motion sensor",
    "9002": 1509923782,
    "9003": 65540,
    "9019": 1,
    "9020": 1510012563,
    "9054": 0,
}

#  Retrieved from Gateway running on 1.4.15
OUTLET = {
    "9001": "Audioset",
    "9002": 1536968250,
    "9020": 1536968280,
    "9003": 65548,
    "9054": 0,
    "5750": 3,
    "9019": 1,
    "9084": " 43 86 6e b5 6a df dc da d6 ce 9c 5a b4 63 a4 2a",
    "3": {
        "0": "IKEA of Sweden",
        "1": "TRADFRI control outlet",
        "3": "1.4.020",
        "2": "",
        "6": 1,
    },
    "3312": [{"9003": 0, "5850": 0, "5851": 254}],
}

# Retrieved from Gateway running on 1.8.26
GROUP = {
    "9001": "Stue",
    "5851": 0,
    "9002": 1549993265,
    "9003": 131073,
    "5850": 0,
    "9039": 196608,
    "9108": 0,
    "9018": {"15002": {"9003": [65536, 65537, 65538, 65539]}},
}

# Retrieved from Gateway running on 1.x.x
BLIND = {
    "15015": [{"5536": 50.0, "9003": 0}],
    "3": {
        "0": "IKEA of Sweden",
        "1": "FYRTUR block-out roller blind",
        "2": "",
        "3": "2.2.007",
        "6": 3,
        "9": 77,
    },
    "5750": 7,
    "9001": "Roller blind",
    "9002": 1566141494,
    "9003": 65601,
    "9019": 1,
    "9020": 1566402653,
    "9054": 0,
    "9084": " 9d 58 b0 2 4 6a df be 77 e5 c1 e0 a2 26 2e 57",
}

# Retrieved from Gateway running on 1.15.55
AIR_PURIFIER = {
    "3": {
        "0": "IKEA of Sweden",
        "1": "STARKVIND Air purifier",
        "2": "",
        "3": "1.0.033",
        "6": 1,
        "7": 4364,
    },
    "5750": 10,
    "9001": "Luftreiniger",
    "9002": 1633096623,
    "9003": 65551,
    "9019": 1,
    "9020": 1633096633,
    "9054": 0,
    "15025": [
        {
            "5900": 1,
            "5902": 2,
            "5903": 0,
            "5904": 259200,
            "5905": 0,
            "5906": 0,
            "5907": 5,
            "5908": 10,
            "5909": 2,
            "5910": 259198,
            "9003": 0,
        }
    ],
}

SIGNAL_REPEATER = {
    "15014": [{"9003": 0}],
    "3": {
        "0": "IKEA of Sweden",
        "1": "TRADFRI signal repeater",
        "2": "",
        "3": "2.0.019",
        "6": 1,
    },
    "5750": 6,
    "9001": "Signalforstaerker",
    "9002": 1566141249,
    "9003": 65600,
    "9019": 1,
    "9020": 1566401800,
    "9054": 0,
    "9084": " 83 6f b7 c 7a f4 8a 14 4a 94 4a 94 41 e0 a2 4f",
}
