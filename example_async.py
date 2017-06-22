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
import logging
import sys

from pytradfri import Gateway
from pytradfri.api.aiocoap_api import api_factory

root = logging.getLogger()
root.setLevel(logging.INFO)

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
    api = yield from api_factory(sys.argv[1], sys.argv[2])

    gateway = Gateway()

    devices_command = gateway.get_devices()
    devices_commands = yield from api(devices_command)
    devices = yield from api(*devices_commands)

    lights = [dev for dev in devices if dev.has_light_control]

    tasks_command = gateway.get_smart_tasks()
    tasks = yield from api(tasks_command)

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
    dim_command = light.light_control.set_dimmer(255)
    yield from api(dim_command)

    # Example 5: Change color of light 0
    # f5faf6 = cold | f1e0b5 = normal | efd275 = warm
    color_command = light.light_control.set_hex_color('efd275')
    yield from api(color_command)

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
