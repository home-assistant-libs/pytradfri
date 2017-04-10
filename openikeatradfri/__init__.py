"""
Run with python3 -i pytradfri.py IP KEY

Will give you an interactive Python shell:
 - 'api' is method to call the hub
 - 'hub' is hub object
 - 'lights' is all devices that have lights
 - 'light' is the first device that has a light
"""
from datetime import datetime
import json
import logging
import subprocess
import sys

PATH_ROOT = "15001"

ATTR_DEVICE_INFO = "3"
ATTR_MANUFACTURER = "0"
ATTR_MODEL_NAME = "1"
ATTR_NAME = "9001"
ATTR_CREATED_AT = "9002"
ATTR_ID = "9003"
ATTR_REACHABLE_STATE = "9019"
ATTR_LAST_SEEN = "9020"
ATTR_OTA_UPDATE_STATE = "9054"

ATTR_SWITCHES = "15009"

ATTR_LIGHTS = "3311"  # array
ATTR_COLOR_X = "5709"
ATTR_COLOR_Y = "5710"
ATTR_BRIGHTNESS = "5851"  # 0..254
ATTR_STATE = "5850"  # 0 / 1
ATTR_DIMMER = "5851"

_LOGGER = logging.getLogger(__name__)


class PyTradFriError(Exception):
    """Base Error"""
    pass


class CommandError(PyTradFriError):
    pass


def api_factory(host, security_code):
    """Generate a request method."""
    def request(method, path, data=None):
        """Make a request."""
        path = '/'.join(str(v) for v in path)
        command_string = 'coaps://{}:5684/{}'.format(host, path)

        command = [
            '/usr/local/bin/coap-client',
            '-u',
            'Client_identity',
            '-k',
            security_code,
            '-v',
            '0',
            '-m',
            method,
            command_string
        ]

        kwargs = {
            'timeout': 10,
            'stderr': subprocess.STDOUT,
        }

        if data is not None:
            kwargs['input'] = json.dumps(data).encode('utf-8')
            command.append('-f')
            command.append('-')
            _LOGGER.debug('Executing {} {} {}: {}'.format(
                host, method, path, data))
        else:
            _LOGGER.debug('Executing {} {} {}'.format(host, method, path))

        try:
            return_value = subprocess.check_output(command, **kwargs)
            out = return_value.strip().decode('utf-8')
        except subprocess.CalledProcessError:
            raise CommandError() from None

        # Return only the last line, where there's JSON
        lines = out.split('\n')

        if len(lines) < 4:
            return None

        output = lines[3]
        _LOGGER.debug('Received: %s', output)
        return json.loads(output)

    return request


class Hub(object):
    """This class connects to the IKEA Tradfri Gateway"""

    def __init__(self, api):
        self._api = api
        self._devices = None

    def get_devices(self):
        """Returns the devices linked to the gateway"""
        devices = self._api('get', [PATH_ROOT])

        return [Device(self._api, self._api('get', [PATH_ROOT, dev]))
                for dev in devices]

    def get_lights(self):
        """Return devices that contain lights connected to this hub."""
        return [dev for dev in self.get_devices() if dev.has_lights]


class Device(object):
    """Base class for devices."""

    def __init__(self, api, info):
        self._api = api
        self._info = info

    @property
    def id(self):
        return self._info[ATTR_ID]

    @property
    def manufacturer(self):
        return self._info[ATTR_DEVICE_INFO][ATTR_MANUFACTURER]

    @property
    def model_name(self):
        return self._info[ATTR_DEVICE_INFO][ATTR_MODEL_NAME]

    @property
    def name(self):
        return self._info[ATTR_NAME]

    @property
    def created_at(self):
        return datetime.utcfromtimestamp(self._info[ATTR_CREATED_AT])

    @property
    def last_seen(self):
        return datetime.utcfromtimestamp(self._info[ATTR_LAST_SEEN])

    @property
    def has_switches(self):
        return ATTR_SWITCHES in self._info

    @property
    def has_lights(self):
        return ATTR_LIGHTS in self._info

    @property
    def lights(self):
        return [Light(self._api, self.id, index, light) for index, light
                in enumerate(self._info.get(ATTR_LIGHTS, []))]

    def set_light_brightness(self, brightness, *, index=0):
        assert len(self._info.get(ATTR_LIGHTS, [])) == 1, \
            'Only devices with 1 light supported'

        self._api('put', [PATH_ROOT, self.id], {
            ATTR_LIGHTS: [
                {
                    ATTR_BRIGHTNESS: brightness
                }
            ]
        })

    def set_light_xy_color(self, color_x, color_y, *, index=0):
        assert len(self._info.get(ATTR_LIGHTS, [])) == 1, \
            'Only devices with 1 light supported'

        # TODO doesn't work yet

        self._api('put', [PATH_ROOT, self.id], {
            ATTR_LIGHTS: [
                {
                    ATTR_COLOR_X: color_x,
                    ATTR_COLOR_Y: color_y,
                }
            ]
        })

    def update(self):
        self._info = self._api('get', [PATH_ROOT, self.id])

    def __repr__(self):
        return "<{} - {} ({})>".format(self.id, self.name, self.model_name)


class Light:
    def __init__(self, api, parent_id, index, info):
        self._api = api
        self.parent_id = parent_id
        self.index = index
        self._info = info

    @property
    def is_on(self):
        return self._info.get(ATTR_STATE) == 1

    @property
    def brightness(self):
        return self._info.get(ATTR_BRIGHTNESS)

    @property
    def xy_color(self):
        return self._info.get(ATTR_COLOR_X), self._info.get(ATTR_COLOR_Y)

    def __repr__(self):
        state = "on" if self.is_on else "off"
        return "<Light #{} - {}>".format(self.index, state)


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
