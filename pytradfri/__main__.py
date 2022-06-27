"""Provide a CLI for Tradfri."""
from __future__ import annotations

import argparse
import logging
from pprint import pprint
import uuid

from pytradfri.api.libcoap_api import APIFactory
from pytradfri.device import Device
from pytradfri.error import PytradfriError
from pytradfri.group import Group
from pytradfri.util import load_json, save_json

from .command import Command
from .gateway import Gateway

CONFIG_FILE = "tradfri_standalone_psk.conf"

# pylint: disable=invalid-name


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

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
    org_args = parser.parse_args()

    if org_args.host not in load_json(CONFIG_FILE) and org_args.key is None:
        print(
            "Please provide the 'Security Code' on the back of your "
            "Tradfri gateway:",
            end=" ",
        )
        key = input().strip()
        if len(key) != 16:
            raise PytradfriError(
                "'Security Code' has to be exactly" + "16 characters long."
            )
        org_args.key = key

    conf = load_json(CONFIG_FILE)

    try:
        identity = conf[org_args.host].get("identity")
        psk = conf[org_args.host].get("key")
        api_factory = APIFactory(host=org_args.host, psk_id=identity, psk=psk)
    except KeyError:
        identity = uuid.uuid4().hex
        api_factory = APIFactory(host=org_args.host, psk_id=identity)

        try:
            psk = api_factory.generate_psk(org_args.key)
            print("Generated PSK: ", psk)

            conf[org_args.host] = {"identity": identity, "key": psk}
            save_json(CONFIG_FILE, conf)
        except AttributeError as exc:
            raise PytradfriError(
                "Please provide the 'Security Code' on the "
                "back of your Tradfri gateway using the "
                "-K flag."
            ) from exc

    api = api_factory.request

    gateway = Gateway()
    devices_commands = api(gateway.get_devices())
    devices = api(devices_commands)
    lights = [dev for dev in devices if dev.has_light_control]
    if lights:
        light: Device | None = lights[0]
    else:
        print("No lights found!")
        light = None
    groups_commands = api(gateway.get_groups())
    groups = api(groups_commands)
    moods = []
    if groups:
        group: Group | None = groups[0]
        for group in groups:
            moods_commands = api(group.moods())
            group_moods = api(moods_commands)
            moods.extend(group_moods)
    else:
        print("No groups found!")
        group = None
    tasks_commands = api(gateway.get_smart_tasks())
    tasks = api(tasks_commands)
    homekit_id = api(gateway.get_gateway_info()).homekit_id

    def dump_all() -> None:
        """Dump all endpoints."""
        endpoints = api(gateway.get_endpoints())

        for endpoint in endpoints:
            parts = endpoint[1:].split("/")

            if not all(part.isdigit() for part in parts):
                continue

            pprint(api(Command("get", parts)))
            print()
            print()

    def dump_devices() -> None:
        """Dump devices."""
        pprint([d.raw for d in devices])

    print()
    print("Example commands:")
    print("> devices")
    print("> homekit_id")
    if light:
        print("> light.light_control.lights")
        print("> api(light.light_control.set_dimmer(10))")
        print("> api(light.light_control.set_dimmer(254))")
        print("> api(light.light_control.set_xy_color(30015, 26870))")
        print("> api(light.light_control.set_predefined_color('Warm Amber'))")
        print("> api(lights[1].light_control.set_dimmer(20))")
    if tasks:
        print("> tasks[0].repeat_days_list")
    print("> api(gateway.reboot())")
    print("> groups")
    print("> moods")
    print("> tasks")
    print("> dump_devices()")
    print("> dump_all()")
