#!/usr/bin/env python3
"""
This is an example of how the pytradfri-library can be used async.

To run the script, do the following:
$ pip3 install pytradfri
$ Download this file (example_air_purifier_async.py)
$ python3 example_air_purifier_async.py <IP>

Where <IP> is the address to your IKEA gateway. The first time
running you will be asked to input the 'Security Code' found on
the back of your IKEA gateway.
"""

import argparse
import asyncio
import os
import sys
import uuid

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

    air_purifiers = [dev for dev in devices if dev.has_air_purifier_control]

    # Print all air purifiers
    print(air_purifiers)

    for air_purifier in air_purifiers:
        control = air_purifier.air_purifier_control
        assert control is not None
        print(control.air_purifiers[0].air_quality)
        # Set mode auto
        command = control.turn_on_auto_mode()
        await api(command)

    await api_factory.shutdown()


asyncio.run(run())
