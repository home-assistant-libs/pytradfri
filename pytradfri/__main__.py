"""Provide a CLI for Tradfri."""
import logging
from pprint import pprint
import sys

from .const import *  # noqa
from pytradfri.api.libcoap_api import APIFactory
from .gateway import Gateway
from .command import Command


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Call with {} <host> <key>'.format(sys.argv[0]))
        sys.exit(1)

    logging.basicConfig(level=logging.DEBUG)

    api_factory = APIFactory(sys.argv[1])
    with open('gateway_psk.txt', 'a+') as file:
        file.seek(0)
        psk = file.read()
        if psk:
            api_factory.psk = psk.strip()
        else:
            psk = api_factory.generate_psk(sys.argv[2])
            print('Generated PSK: ', psk)
            file.write(psk)

    api = api_factory.request

    gateway = Gateway()
    devices_commands = api(gateway.get_devices())
    devices = api(devices_commands)
    lights = [dev for dev in devices if dev.has_light_control]
    light = lights[0]
    groups = api(gateway.get_groups())
    group = groups[0]
    moods = api(gateway.get_moods())
    mood = moods[0]
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
    print("> light.light_control.lights")
    print("> api(light.light_control.set_dimmer(10))")
    print("> api(light.light_control.set_dimmer(254))")
    print("> api(light.light_control.set_xy_color(254))")
    print("> api(lights[1].light_control.set_dimmer(20))")
    print("> tasks[0].repeat_days_list")
    print("> api(gateway.reboot())")
    print("> groups")
    print("> moods")
    print("> tasks")
    print("> dump_devices()")
    print("> dump_all()")
