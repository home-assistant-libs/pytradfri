#!/usr/bin/env python3
"""
This is an example of how the pytradfri-library can be used async.

To run the script, do the following:
$ pip3 install pytradfri
$ Download this file (example_async.py)
$ python3 example_async.py <IP>

Where <IP> is the address to your IKEA gateway. The first time
running you will be asked to input the 'Security Code' found on
the back of your IKEA gateway.
"""

# Hack to allow relative import above top level package
import sys
import os

folder = os.path.dirname(os.path.abspath(__file__))  # noqa
sys.path.insert(0, os.path.normpath("%s/.." % folder))  # noqa

from pytradfri import Gateway
from pytradfri.api.aiocoap_api import APIFactory
from pytradfri.error import PytradfriError
from pytradfri.util import load_json, save_json

import asyncio
import uuid
import argparse

CONFIG_FILE = 'tradfri_standalone_psk.conf'

parser = argparse.ArgumentParser()
parser.add_argument('host', metavar='IP', type=str,
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


async def run():
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
            psk = await api_factory.generate_psk(args.key)
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
    devices_commands = await api(devices_command)
    devices = await api(devices_commands)

    sockets = [dev for dev in devices if dev.has_socket_control]

    # Print all sockets
    print(sockets)

    # Sockets can be accessed by its index, so sockets[1] is the second socket
    if sockets:
        socket = sockets[0]
    else:
        print("No sockets found!")
        socket = None

    def observe_callback(updated_device):
        socket = updated_device.socket_control.sockets[0]
        print("Received message for: %s" % socket)

    def observe_err_callback(err):
        print('observe error:', err)

    for socket in sockets:
        observe_command = socket.observe(observe_callback,
                                         observe_err_callback,
                                         duration=120)
        # Start observation as a second task on the loop.
        asyncio.ensure_future(api(observe_command))
        # Yield to allow observing to start.
        await asyncio.sleep(0)

    if socket:
        # Example 1: checks state of the socket (true=on)
        print("Is on:", socket.socket_control.sockets[0].state)

        # Example 2: What is the name of the socket
        print("Name:", socket.name)

        # Example 3: Turn socket on
        state_command = socket.socket_control.set_state(True)
        await api(state_command)

    print("Waiting for observation to end (10 secs)")
    await asyncio.sleep(10)

    await api_factory.shutdown()


asyncio.get_event_loop().run_until_complete(run())
