"""Provide a CLI for Tradfri."""
import logging
from pprint import pprint

from .const import *  # noqa
from pytradfri.api.libcoap_api import APIFactory
from pytradfri.util import load_json, save_json
from pytradfri.error import PytradfriError
from .gateway import Gateway
from .command import Command

import argparse
import uuid

if __name__ == '__main__':
    CONFIG_FILE = 'tradfri_standalone_psk.conf'

    logging.basicConfig(level=logging.DEBUG)

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
            raise PytradfriError("'Security Code' has to be exactly" +
                                 "16 characters long.")
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
    devices_commands = api(gateway.get_devices())
    devices = api(devices_commands)
    lights = [dev for dev in devices if dev.has_light_control]
    if lights:
        light = lights[0]
    else:
        print("No lights found!")
        light = None
    groups = api(gateway.get_groups())
    if groups:
        group = groups[0]
    else:
        print("No groups found!")
        group = None
    moods = api(gateway.get_moods())
    if moods:
        mood = moods[0]
    else:
        print("No moods found!")
        mood = None
    tasks = api(gateway.get_smart_tasks())
    homekit_id = api(gateway.get_gateway_info()).homekit_id

    def dump_all():
        endpoints = api(gateway.get_endpoints())

        for endpoint in endpoints:
            parts = endpoint[1:].split('/')

            if not all(part.isdigit() for part in parts):
                continue

            pprint(api(Command('get', parts)))
            print()
            print()

    def dump_devices():
        pprint([d.raw for d in devices])

    print()
    print("Example commands:")
    print("> devices")
    print("> homekit_id")
    if light:
        print("> light.light_control.lights")
        print("> api(light.light_control.set_dimmer(10))")
        print("> api(light.light_control.set_dimmer(254))")
        print("> api(light.light_control.set_xy_color(254))")
        print("> api(lights[1].light_control.set_dimmer(20))")
    if tasks:
        print("> tasks[0].repeat_days_list")
    print("> api(gateway.reboot())")
    print("> groups")
    print("> moods")
    print("> tasks")
    print("> dump_devices()")
    print("> dump_all()")
