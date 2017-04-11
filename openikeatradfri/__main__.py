"""Provide a CLI for Tradfri."""
import logging
from pprint import pprint
import sys

from . import api_factory, Hub

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Call with {} <host> <key>'.format(sys.argv[0]))
        sys.exit(1)

    logging.basicConfig(level=logging.DEBUG)

    api = api_factory(sys.argv[1], sys.argv[2])
    hub = Hub(api)
    lights = hub.get_lights()
    light = lights[0]

    def show_all():
        pprint([d.raw for d in hub.get_devices()])

    print()
    print("Example commands:")
    print("> show_all()")
    print("> hub.get_devices()")
    print("> light.light_control.lights")
    print("> light.light_control.set_brightness(10)")
    print("> light.light_control.set_brightness(254)")
    print("> light.light_control.set_xy_color(254)")
