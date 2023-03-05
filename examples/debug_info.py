#!/usr/bin/env python3
"""Generates debug information about your Tradfri network.

To run the script, do the following:
$ pip3 install pytradfri
$ Download this file (debug_info.py)
$ python3 debug_info.py <IP>

Where <IP> is the address to your IKEA gateway. The first time
running you will be asked to input the 'Security Code' found on
the back of your IKEA gateway.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any
import uuid

# Hack to allow relative import above top level package

folder = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(f"{folder}/.."))

# pylint: disable=import-error, wrong-import-position, useless-suppression

from pytradfri import Gateway
from pytradfri.api.libcoap_api import APIFactory
from pytradfri.error import PytradfriError
from pytradfri.util import load_json, save_json

CONFIG_FILE = "tradfri_standalone_psk.conf"

# pylint: disable=invalid-name


parser = argparse.ArgumentParser()
parser.add_argument(
    "host", metavar="IP", type=str, help="IP Address of your Tradfri gateway"
)
parser.add_argument(
    "-K",
    "--key",
    dest="key",
    required=False,
    help="Security code found on your Tradfri gateway",
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


conf = load_json(CONFIG_FILE)

try:
    identity = conf[args.host].get("identity")
    psk = conf[args.host].get("key")
    api_factory = APIFactory(host=args.host, psk_id=identity, psk=psk)
except KeyError:
    identity = uuid.uuid4().hex
    api_factory = APIFactory(host=args.host, psk_id=identity)

    try:
        psk = api_factory.generate_psk(args.key)
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
devices_commands = api(devices_command)
devices = api(devices_commands)


def jsonify(data: dict[str, Any] | list[Any]) -> str:
    """Convert to json."""
    return json.dumps(
        data,
        sort_keys=True,
        indent=4,
        ensure_ascii=False,
    )


def bold(string: str) -> str:
    """Bold."""
    return f"\033[1;30m{string}\033[0;0m"


def print_gateway() -> None:
    """Print gateway info as JSON."""
    print("Printing information about the Gateway")
    data = api(gateway.get_gateway_info()).raw.dict()
    print(jsonify(data))


def print_gateway_endpoints() -> None:
    """Print all gateway endpoints as JSON."""
    print("Printing information about endpoints in the Gateway")
    data = api(gateway.get_endpoints())
    print(jsonify(data))


def print_all_devices() -> None:
    """Print all devices as JSON."""
    print("Printing information about all devices paired to the Gateway")
    if not devices:
        sys.exit(bold("No devices paired"))

    container: list[dict[str, Any]] = []
    for dev in devices:
        container.append(dev.raw.dict())
    print(jsonify(container))


def print_lamps() -> None:
    """Print all lamp devices as JSON."""
    print("Printing information about all lamps paired to the Gateway")
    lights = [dev for dev in devices if dev.has_light_control]
    if not lights:
        sys.exit(bold("No lamps paired"))

    container: list[dict[str, Any]] = []
    for light in lights:
        container.append(light.raw.dict())
    print(jsonify(container))


def print_smart_tasks() -> None:
    """Print smart tasks as JSON."""
    print("Printing information about smart tasks")
    if not (tasks := api(gateway.get_smart_tasks())):
        sys.exit(bold("No smart tasks defined"))

    container: list[dict[str, Any]] = []
    for task in tasks:
        container.append(api(task).task_control.raw.dict())
    print(jsonify(container))


def print_groups() -> None:
    """Print all groups as JSON."""
    print("Printing information about all groups defined in the Gateway")
    if not (groups := api(gateway.get_groups())):
        sys.exit(bold("No groups defined"))

    container: list[dict[str, Any]] = []
    for group in groups:
        container.append(api(group).raw.dict())
    print(jsonify(container))


def print_moods() -> None:
    """Print all moods as JSON."""
    print("Printing information about all moods defined in the Gateway")
    if not (groups := api(gateway.get_groups())):
        sys.exit(bold("No groups defined"))

    container = []

    for group_command in groups:
        group = api(group_command)
        moods = api(gateway.get_moods(group.id))

        for mood in moods:
            container.append(api(mood).raw.dict())

    if not container:
        sys.exit(bold("No moods defined"))

    print(jsonify(container))


# Choosing the right print function
print(bold("What information about your Tradfri network do you need?"))
print("1. Gateway")
print("2. Gateway endpoints")
print("3. All paired devices")
print("4. All paired lamps")
print("5. All smart tasks")
print("6. All groups")
print("7. All moods")
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
elif choice == "7":
    print_moods()
else:
    sys.exit(bold(f"I don't understand '{choice}'"))
