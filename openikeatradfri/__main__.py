"""Provide a CLI for Tradfri."""
import logging
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

    print()
    print("Example commands:")
    print("> hub.get_devices()")
    print("> light.lights")
    print("> light.set_light_brightness(10)")
    print("> light.set_light_brightness(254)")
    print("> light.set_light_xy_color(254)")
