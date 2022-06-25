#!/usr/bin/env python3
"""Color examples.

This is a file to give examples on how to work with colors
The gateway supports _some_ hex values, otherwise colors stored as XY
A guess is that IKEA uses the CIE XYZ space

You need to install colormath from pypi in order to make this example work:
$ pip3 install colormath

To run the script, do the following:
$ pip3 install pytradfri
$ Download this file (example_color.py)
$ python3 example_color.py <IP>

Where <IP> is the address to your IKEA gateway. The first time
running you will be asked to input the 'Security Code' found on
the back of your IKEA gateway.

The gateway returns:
    Hue (a guess)
    Saturation (a guess)
    Brightness
    X
    Y
    Hex (for some colors)
"""

import argparse
import asyncio
import os
import sys
import uuid

from colormath.color_conversions import convert_color
from colormath.color_objects import XYZColor, sRGBColor

# Hack to allow relative import above top level package

folder = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(f"{folder}/.."))

# pylint: disable=wrong-import-position

from pytradfri import Gateway
from pytradfri.api.aiocoap_api import APIFactory
from pytradfri.error import PytradfriError
from pytradfri.util import load_json, save_json

CONFIG_FILE = "tradfri_standalone_psk.conf"


parser = argparse.ArgumentParser()
parser.add_argument(
    "host", metavar="IP", type=str, help="IP Address of your Tradfri gateway"
)
parser.add_argument(
    "-K", "--key", dest="key", required=False, help="Key found on your Tradfri gateway"
)
args = parser.parse_args()


if args.host not in load_json(CONFIG_FILE) and args.key is None:
    print(
        "Please provide the 'Security Code' on the back of your Tradfri gateway:",
        end=" ",
    )
    key = input().strip()
    if len(key) != 16:
        raise PytradfriError("Invalid 'Security Code' provided.")

    args.key = key


async def run() -> None:
    """Run."""
    # Assign configuration variables.
    # The configuration check takes care they are present.
    conf = load_json(CONFIG_FILE)

    try:
        identity = conf[args.host].get("identity")
        psk = conf[args.host].get("key")
        api_factory = await APIFactory.init(host=args.host, psk_id=identity, psk=psk)
    except KeyError:
        identity = uuid.uuid4().hex
        api_factory = await APIFactory.init(host=args.host, psk_id=identity)

        try:
            psk = await api_factory.generate_psk(args.key)
            print("Generated PSK: ", psk)

            conf[args.host] = {"identity": identity, "key": psk}
            save_json(CONFIG_FILE, conf)
        except AttributeError as err:
            raise PytradfriError(
                "Please provide the 'Security Code' on the "
                "back of your Tradfri gateway using the "
                "-K flag."
            ) from err

    api = api_factory.request

    gateway = Gateway()

    devices_command = gateway.get_devices()
    devices_commands = await api(devices_command)
    devices = await api(devices_commands)

    lights = [dev for dev in devices if dev.has_light_control]

    rgb_tuple = (0, 0, 102)

    # Convert RGB to XYZ using a D50 illuminant.
    xyz = convert_color(
        sRGBColor(rgb_tuple[0], rgb_tuple[1], rgb_tuple[2]),
        XYZColor,
        observer="2",
        target_illuminant="d65",
    )
    xy_tuple = int(xyz.xyz_x), int(xyz.xyz_y)

    light = None
    # Find a bulb that can set color
    for dev in lights:
        light_control = dev.light_control
        assert light_control is not None
        if light_control.lights[0].supports_hsb_xy_color:
            light = dev
            break

    if not light:
        print("No color bulbs found")
        return

    light_control = light.light_control
    assert light_control is not None
    xy_command = light_control.set_xy_color(xy_tuple[0], xy_tuple[1])
    await api(xy_command)

    xy_color = light_control.lights[0].xy_color
    dimmer = light_control.lights[0].dimmer

    if xy_color is None or dimmer is None:
        print("Light color properties are missing")
        return

    #  Normalize Z

    z_color = int(dimmer / 254 * 65535)
    xyz = xy_color + (z_color,)
    rgb = convert_color(
        XYZColor(xyz[0], xyz[1], xyz[2]),
        sRGBColor,
        observer="2",
        target_illuminant="d65",
    )
    rgb_tuple = (int(rgb.rgb_r), int(rgb.rgb_g), int(rgb.rgb_b))
    print(rgb_tuple)

    await asyncio.sleep(120)

    await api_factory.shutdown()


asyncio.run(run())
