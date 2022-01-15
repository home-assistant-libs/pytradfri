#!/usr/bin/env python3
"""
This is an example of how the pytradfri-library can be used async to create a list in json format (e.g. for a webserver, to retrieve information about TRADFRI system).

To run the script, do the following:
$ pip3 install pytradfri
$ Download this file (example_jsonlist.py)
$ python3 example_jsonlist.py) <IP>

Where <IP> is the address to your IKEA gateway. The first time
running you will be asked to input the 'Security Code' found on
the back of your IKEA gateway.
"""

import os

# Hack to allow relative import above top level package
import sys

folder = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath("%s/.." % folder))

import argparse
import asyncio
import uuid

from pytradfri import Gateway
from pytradfri.api.aiocoap_api import APIFactory
from pytradfri.error import PytradfriError
from pytradfri.util import load_json, save_json

#CONFIG_FILE = "tradfri_standalone_psk.conf"

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
            "Please provide the 'Security Code' on the back of your " "Tradfri gateway:",
            end=" ",
            )
    key = input().strip()
    if len(key) != 16:
        raise PytradfriError("Invalid 'Security Code' provided.")
    else:
        args.key = key


async def run():
    """Run process."""
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
        except AttributeError:
            raise PytradfriError(
                    "Please provide the 'Security Code' on the "
                    "back of your Tradfri gateway using the "
                    "-K flag."
                    )

    api = api_factory.request

    gateway = Gateway()

    devices_command = gateway.get_devices()
    devices_commands = await api(devices_command)
    devices = await api(devices_commands)

    list_devices = [dev for dev in devices]
    #print("{\"DEVICES\":[", end= '');
    print("[", end= '');
    first=True;
    for device in list_devices:
        if first != True:
            print(",", end='');
        print("{\"ID\":\"" + str(device.id) + "\",\"NAME\":\"" + device.name + "\",\"STATE\":\"", end='');
        if device.has_socket_control:
            print(device.socket_control.sockets[0].state, end='');
            print("\",\"TYPE\":\"SOCKET\"", end='');
        elif device.has_light_control:
            print(device.light_control.lights[0].dimmer, end='');
            print("\",\"TYPE\":\"LIGHT\"", end='');
        else:
            print("\",\"TYPE\":\"UNKOWN\"", end='');
        print(",\"TYPENAME\":\"" + device.device_info.model_number + "\",\"REACHABLE\":\"" + str(device.reachable) + "\"}", end='');
        first=False;
    print("]");
    #print("]}");

    await api_factory.shutdown()


asyncio.get_event_loop().run_until_complete(run())
