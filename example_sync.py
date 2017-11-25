#!/usr/bin/env python3
"""
This is an example of how the pytradfri-library can be used.

To run the script, do the following:
$ pip3 install pytradfri
$ Download this file (example_sync.py)
$ python3 test_pytradfri.py <IP> <KEY>

Where <IP> is the address to your IKEA gateway and
<KEY> is found on the back of your IKEA gateway.
"""

import threading

import time

from pytradfri import Gateway
from pytradfri.api.libcoap_api import APIFactory
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


def observe(api, device):
    def callback(updated_device):
        light = updated_device.light_control.lights[0]
        print("Received message for: %s" % light)

    def err_callback(err):
        print(err)

    def worker():
        api(device.observe(callback, err_callback, duration=120))

    threading.Thread(target=worker, daemon=True).start()
    print('Sleeping to start observation task')
    time.sleep(1)


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
            psk = api_factory.generate_psk(args.key)
            print('Generated PSK: ', psk)

            conf[args.host] = {'identity': identity,
                               'key': psk}
            save_json(CONFIG_FILE, conf)

            api_factory = APIFactory(host=args.host, psk_id=identity, psk=psk)
        except AttributeError:
            raise PytradfriError("Please provide your Key")

    api = api_factory.request

    gateway = Gateway()

    devices_command = gateway.get_devices()
    devices_commands = api(devices_command)
    devices = api(devices_commands)

    lights = [dev for dev in devices if dev.has_light_control]

    # Print all lights
    print(lights)

    # Lights can be accessed by its index, so lights[1] is the second light
    light = lights[0]

    observe(api, light)

    # Example 1: checks state of the light 2 (true=on)
    print(light.light_control.lights[0].state)

    # Example 2: get dimmer level of light 2
    print(light.light_control.lights[0].dimmer)

    # Example 3: What is the name of light 2
    print(light.name)

    # Example 4: Set the light level of light 2
    dim_command = light.light_control.set_dimmer(254)
    api(dim_command)

    # Example 5: Change color of light 2
    # f5faf6 = cold | f1e0b5 = normal | efd275 = warm
    color_command = light.light_control.set_hex_color('efd275')
    api(color_command)

    tasks_command = gateway.get_smart_tasks()
    tasks_commands = api(tasks_command)
    tasks = api(tasks_commands)

    # Example 6: Return the transition time (in minutes) for task#1
    if tasks:
        print(tasks[0].task_control.tasks[0].transition_time)

        # Example 7: Set the dimmer stop value to 30 for light#1 in task#1
        dim_command_2 = tasks[0].start_action.devices[0].item_controller\
            .set_dimmer(30)
        api(dim_command_2)

    print("Sleeping for 2 min to receive the rest of the observation events")
    print("Try altering the light (%s) in the app, and watch the events!" %
          light.name)
    time.sleep(120)


run()
