#!/usr/bin/env python3
"""
This file generates debug information about your Tradfri network.

To run the script, do the following:
$ pip3 install pytradfri
$ Download this file (debug_info.py)
$ python3 debug_info.py <IP>

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
from pytradfri.api.libcoap_api import APIFactory
from pytradfri.error import PytradfriError
from pytradfri.util import load_json, save_json
import json
import uuid
import argparse

CONFIG_FILE = 'tradfri_standalone_psk.conf'


parser = argparse.ArgumentParser()
parser.add_argument('host', metavar='IP', type=str,
                    help='IP Address of your Tradfri gateway')
parser.add_argument('-K', '--key', dest='key', required=False,
                    help='Security code found on your Tradfri gateway')
args = parser.parse_args()


if args.host not in load_json(CONFIG_FILE) and args.key is None:
    print("Please provide the 'Security Code' on the back of your "
          "Tradfri gateway:", end=" ")
    key = input().strip()
    if len(key) != 16:
        raise PytradfriError("Invalid 'Security Code' provided.")
    else:
        args.key = key


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
    except AttributeError:
        raise PytradfriError("Please provide the 'Security Code' on the "
                             "back of your Tradfri gateway using the "
                             "-K flag.")

api = api_factory.request

gateway = Gateway()

devices_command = gateway.get_devices()
devices_commands = api(devices_command)
devices = api(devices_commands)


def jsonify(input):
    return json.dumps(
        input,
        sort_keys=True,
        indent=4,
        ensure_ascii=False,
    ).encode('utf8')


def bold(str):
    return "\033[1;30m%s\033[0;0m" % str


def print_gateway():
    """Print gateway info as JSON"""
    print("Printing information about the Gateway")
    data = api(gateway.get_gateway_info()).raw
    print(jsonify(data))


def print_gateway_endpoints():
    """Print all gateway endpoints as JSON"""
    print("Printing information about endpoints in the Gateway")
    data = api(gateway.get_endpoints())
    print(jsonify(data))


def print_all_devices():
    """Print all devices as JSON"""
    print("Printing information about all devices paired to the Gateway")
    if len(devices) == 0:
        exit(bold("No devices paired"))

    container = []
    for dev in devices:
        container.append(dev.raw)
    print(jsonify(container))


def print_lamps():
    """Print all lamp devices as JSON"""
    print("Printing information about all lamps paired to the Gateway")
    lights = [dev for dev in devices if dev.has_light_control]
    if len(lights) == 0:
        exit(bold("No lamps paired"))

    container = []
    for l in lights:
        container.append(l.raw)
    print(jsonify(container))


def print_smart_tasks():
    """Print smart tasks as JSON"""
    print("Printing information about smart tasks")
    tasks = api(gateway.get_smart_tasks())
    if len(tasks) == 0:
        exit(bold("No smart tasks defined"))

    container = []
    for task in tasks:
        container.append(api(task).task_control.raw)
    print(jsonify(container))


def print_groups():
    """Print all groups as JSON"""
    print("Printing information about all groups defined in the Gateway")
    groups = api(gateway.get_groups())
    if len(groups) == 0:
        exit(bold("No groups defined"))

    container = []
    for group in groups:
        container.append(api(group).raw)
    print(jsonify(container))


# Choosing the right print function
print(bold("What information about your Tradfri network do you need?"))
print("1. Gateway")
print("2. Gateway endpoints")
print("3. All paired devices")
print("4. All paired lamps")
print("5. All smart tasks")
print("6. All groups")
choice = input("Make a choice: ").strip()
print()

if choice == "1":
    print_gateway()
elif choice == "2":
    print_gateway_endpoints()
elif choice == "3":
    print_all_devices()
elif choice == "4":
    print_lamps()
elif choice == "5":
    print_smart_tasks()
elif choice == "6":
    print_groups()
else:
    exit(bold("I don't understand '%s'" % choice))
