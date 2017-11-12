#!/usr/bin/env python3
"""
This is a file to give examples on how to work with colors
The gateway supports _some_ hex values, otherwise colors stored as XY
A guess is that IKEA uses the CIE XYZ space

You need to install colormath from pypi in order to this example:
% pip install colormath

Alternatively, as 2.2 of colormath hasn't been released to pypi yet
% pip install git+git://github.com/gtaylor/python-colormath

The gateway returns:
    Hue (a guess)
    Saturation (a guess)
    Brignthess
    X
    Y
    Hex (for some colors)
"""

import sys

from pytradfri import Gateway
from pytradfri.api.libcoap_api import APIFactory

from colormath.color_conversions import convert_color
from colormath.color_objects import sRGBColor, XYZColor


def run():
    # Assign configuration variables.
    # The configuration check takes care they are present.
    api_factory = APIFactory(sys.argv[1])
    with open('gateway_psk.txt', 'a+') as file:
        file.seek(0)
        psk = file.read()
        if psk:
            api_factory.psk = psk.strip()
        else:
            psk = api_factory.generate_psk(sys.argv[2])
            print('Generated PSK: ', psk)
            file.write(psk)
    api = api_factory.request

    gateway = Gateway()

    devices_command = gateway.get_devices()
    devices_commands = api(devices_command)
    devices = api(devices_commands)
    lights = [dev for dev in devices if dev.has_light_control]

    rgb = (0, 0, 102)

    # Convert RGB to XYZ using a D50 illuminant.
    xyz = convert_color(sRGBColor(rgb[0], rgb[1], rgb[2]), XYZColor,
                        observer='2', target_illuminant='d65')
    xy = int(xyz.xyz_x), int(xyz.xyz_y)

    #  Assuming lights[3] is a RGB bulb
    api(lights[3].light_control.set_xy_color(xy[0], xy[1]))

    #  Assuming lights[3] is a RGB bulb
    xy = lights[3].light_control.lights[0].xy_color

    #  Normalize Z
    Z = int(lights[3].light_control.lights[0].dimmer/254*65535)
    xyZ = xy+(Z,)
    rgb = convert_color(XYZColor(xyZ[0], xyZ[1], xyZ[2]), sRGBColor,
                        observer='2', target_illuminant='d65')
    rgb = (int(rgb.rgb_r), int(rgb.rgb_g), int(rgb.rgb_b))
    print(rgb)


run()
