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

    lights = [dev for dev in devices if dev.has_light_control]

    # Print all lights
    print(lights)

    # Lights can be accessed by its index, so lights[1] is the second light
    if lights:
        light = lights[0]
    else:
        print("No lights found!")
        light = None

    def observe_callback(updated_device):
        light = updated_device.light_control.lights[0]
        print("Received message for: %s" % light)

    def observe_err_callback(err):
        print('observe error:', err)

    for light in lights:
        observe_command = light.observe(observe_callback, observe_err_callback,
                                        duration=120)
        # Start observation as a second task on the loop.
        asyncio.ensure_future(api(observe_command))
        # Yield to allow observing to start.
        await asyncio.sleep(0)

    if light:
        # Example 1: checks state of the light (true=on)
        print("Is on:", light.light_control.lights[0].state)

        # Example 2: get dimmer level of the light
        print("Dimmer:", light.light_control.lights[0].dimmer)

        # Example 3: What is the name of the light
        print("Name:", light.name)

        # Example 4: Set the light level of the light
        dim_command = light.light_control.set_dimmer(254)
        await api(dim_command)

        # Example 5: Change color of the light
        # f5faf6 = cold | f1e0b5 = normal | efd275 = warm
        color_command = light.light_control.set_hex_color('efd275')
        await api(color_command)

    # Get all blinds
    blinds = [dev for dev in devices if dev.has_blind_control]

    # Print all blinds
    print(blinds)

    if blinds:
        blind = blinds[0]
    else:
        print("No blinds found!")
        blind = None

    if blind:
        blind_command = blinds[0].blind_control.set_state(50)
        await api(blind_command)

    tasks_command = gateway.get_smart_tasks()
    tasks_commands = await api(tasks_command)
    tasks = await api(tasks_commands)

    # Example 6: Return the transition time (in minutes) for task#1
    if tasks:
        print(tasks[0].task_control.tasks[0].transition_time)

        # Example 7: Set the dimmer stop value to 30 for light#1 in task#1
        dim_command_2 = tasks[0].start_action.devices[0].item_controller\
            .set_dimmer(30)
        await api(dim_command_2)

    print("Waiting for observation to end (2 mins)")
    print("Try altering any light in the app, and watch the events!")
    await asyncio.sleep(120)

    await api_factory.shutdown()


asyncio.get_event_loop().run_until_complete(run())
