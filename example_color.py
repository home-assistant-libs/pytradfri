#!/usr/bin/env python3
"""
This is a file to give examples on how to work with colors
The gateway supports _some_ hex values, otherwise colors stored as XY
A guess is that IKEA uses the CIE XYZ space

You need to install colormath from pypi in order to make this example work:
$ pip3 install colormath

To run the script, do the following:
$ pip3 install pytradfri
$ Download this file (example_color.py)
$ python3 example_color.py -H <IP>

Where <IP> is the address to your IKEA gateway. The first time
running you will be asked to input the 'Security Code' found on
the back of your IKEA gateway.

The gateway returns:
    Hue (a guess)
    Saturation (a guess)
    Brignthess
    X
    Y
    Hex (for some colors)
"""

import asyncio

from pytradfri import Gateway
from pytradfri.api.aiocoap_api import APIFactory
from pytradfri.error import PytradfriError
from pytradfri.util import load_json, save_json

from colormath.color_conversions import convert_color
from colormath.color_objects import sRGBColor, XYZColor

import uuid
import argparse

CONFIG_FILE = 'tradfri_standalone_psk.conf'


parser = argparse.ArgumentParser()
parser.add_argument('-H', '--hostname', dest='host', required=True,
                    help='IP Address of your Tradfri gateway')
parser.add_argument('-K', '--key', dest='key', required=False,
                    help='Key found on your Tradfri gateway')
args = parser.parse_args()


if args.host not in load_json(CONFIG_FILE) and args.key is None:
    print("Please provide the 'Security Code' on the back of your "
          "Tradfri gateway:", end=" ")
    key = input().strip()
    if len(key) != 16:
        raise PytradfriError("Invalid 'Security Code' provided.")
    else:
        args.key = key


try:
    # pylint: disable=ungrouped-imports
    from asyncio import ensure_future
except ImportError:
    # Python 3.4.3 and earlier has this as async
    # pylint: disable=unused-import
    from asyncio import async
    ensure_future = async


@asyncio.coroutine
def run():
    # Assign configuration variables.
    # The configuration check takes care they are present.
    conf = load_json(CONFIG_FILE)

    try:
        identity = conf[args.host].get('identity')
        psk = conf[args.host].get('key')
        api_factory = APIFactory(host=args.host, psk_id=identity, psk=psk)
    except KeyError:
        identity = uuid.uuid4().hex
        api_factory = APIFactory(host=args.host, psk_id=identity)

        try:
            psk = yield from api_factory.generate_psk(args.key)
            print('Generated PSK: ', psk)

            conf[args.host] = {'identity': identity,
                               'key': psk}
            save_json(CONFIG_FILE, conf)
        except AttributeError:
            raise PytradfriError("Please provide the 'Security Code' on the "
                                 "back of your Tradfri gateway using the "
                                 "-K flag.")

    api = api_factory.request

    gateway = Gateway()

    devices_command = gateway.get_devices()
    devices_commands = yield from api(devices_command)
    devices = yield from api(devices_commands)

    lights = [dev for dev in devices if dev.has_light_control]

    rgb = (0, 0, 102)

    # Convert RGB to XYZ using a D50 illuminant.
    xyz = convert_color(sRGBColor(rgb[0], rgb[1], rgb[2]), XYZColor,
                        observer='2', target_illuminant='d65')
    xy = int(xyz.xyz_x), int(xyz.xyz_y)

    #  Assuming lights[3] is a RGB bulb
    xy_command = lights[3].light_control.set_xy_color(xy[0], xy[1])
    yield from api(xy_command)

    #  Assuming lights[3] is a RGB bulb
    xy = lights[3].light_control.lights[0].xy_color

    #  Normalize Z
    Z = int(lights[3].light_control.lights[0].dimmer / 254 * 65535)
    xyZ = xy + (Z,)
    rgb = convert_color(XYZColor(xyZ[0], xyZ[1], xyZ[2]), sRGBColor,
                        observer='2', target_illuminant='d65')
    rgb = (int(rgb.rgb_r), int(rgb.rgb_g), int(rgb.rgb_b))
    print(rgb)

    yield from asyncio.sleep(120)


asyncio.get_event_loop().run_until_complete(run())
