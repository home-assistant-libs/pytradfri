#!/usr/bin/env python3
"""
This is an example of how the pytradfri-library can be used async.

To run the script, do the following:
$ pip3 install pytradfri
$ Download this file (example_sync.py)
$ python3 test_pytradfri.py <IP> <KEY>

Where <IP> is the address to your IKEA gateway and
<KEY> is found on the back of your IKEA gateway.
"""

import asyncio

from pytradfri import Gateway
from pytradfri.api.aiocoap_api import APIFactory
from pytradfri.error import PytradfriError
from pytradfri.util import load_json, save_json

from pathlib import Path
import uuid
import argparse

CONFIG_FILE = 'tradfri_standalone_psk.conf'


parser = argparse.ArgumentParser()
parser.add_argument('-H', '--hostname', dest='host', required=True,
                    help='IP Address of your Tradfri gateway')
parser.add_argument('-K', '--key', dest='key', required=False,
                    help='Key found on your Tradfri gateway')
args = parser.parse_args()


if Path(CONFIG_FILE).is_file() is False and args.key is None:
    raise PytradfriError("Please provide they key found on your "
                         "Tradfri gateway using the -K flag to this script.")


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
            raise PytradfriError("Please provide your Key")

    api = api_factory.request

    gateway = Gateway()

    devices_command = gateway.get_devices()
    devices_commands = yield from api(devices_command)
    devices = yield from api(devices_commands)

    lights = [dev for dev in devices if dev.has_light_control]

    # Print all lights
    print(lights)

    # Lights can be accessed by its index, so lights[1] is the second light
    light = lights[0]

    def observe_callback(updated_device):
        light = updated_device.light_control.lights[0]
        print("Received message for: %s" % light)

    def observe_err_callback(err):
        print('observe error:', err)

    for light in lights:
        observe_command = light.observe(observe_callback, observe_err_callback,
                                        duration=120)
        # Start observation as a second task on the loop.
        ensure_future(api(observe_command))
        # Yield to allow observing to start.
        yield from asyncio.sleep(0)

    # Example 1: checks state of the light 0 (true=on)
    print("Is on:", light.light_control.lights[0].state)

    # Example 2: get dimmer level of light 0
    print("Dimmer:", light.light_control.lights[0].dimmer)

    # Example 3: What is the name of light 0
    print("Name:", light.name)

    # Example 4: Set the light level of light 0
    dim_command = light.light_control.set_dimmer(254)
    yield from api(dim_command)

    # Example 5: Change color of light 0
    # f5faf6 = cold | f1e0b5 = normal | efd275 = warm
    color_command = light.light_control.set_hex_color('efd275')
    yield from api(color_command)

    tasks_command = gateway.get_smart_tasks()
    tasks_commands = yield from api(tasks_command)
    tasks = yield from api(tasks_commands)

    # Example 6: Return the transition time (in minutes) for task#1
    if tasks:
        print(tasks[0].task_control.tasks[0].transition_time)

        # Example 7: Set the dimmer stop value to 30 for light#1 in task#1
        dim_command_2 = tasks[0].start_action.devices[0].item_controller\
            .set_dimmer(30)
        yield from api(dim_command_2)

    print("Waiting for observation to end (2 mins)")
    print("Try altering any light in the app, and watch the events!")
    yield from asyncio.sleep(120)


asyncio.get_event_loop().run_until_complete(run())
