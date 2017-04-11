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

PATH_ROOT = "15001"

# Spec:
# A: http://www.openmobilealliance.org/wp/OMNA/LwM2M/LwM2MRegistry.html

ATTR_APPLICATION_TYPE = "5750"
ATTR_DEVICE_INFO = "3"
ATTR_NAME = "9001"
ATTR_CREATED_AT = "9002"
ATTR_ID = "9003"
ATTR_REACHABLE_STATE = "9019"
ATTR_LAST_SEEN = "9020"
ATTR_OTA_UPDATE_STATE = "9054"
ATTR_LIGHT_CONTROL = "3311"  # array

_LOGGER = logging.getLogger(__name__)


class PyTradFriError(Exception):
    """Base Error"""
    pass


class CommandError(PyTradFriError):
    """An error happened sending or receiving a command."""
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
            _LOGGER.debug('Executing %s %s %s: %s', host, method, path, data)
        else:
            _LOGGER.debug('Executing %s %s %s', host, method, path)

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

    def get_devices(self):
        """Returns the devices linked to the gateway"""
        devices = self._api('get', [PATH_ROOT])

        return [Device(self._api, self._api('get', [PATH_ROOT, dev]))
                for dev in devices]

    def get_lights(self):
        """Return devices that contain lights connected to this hub."""
        return [dev for dev in self.get_devices() if dev.has_light_control]


class Device(object):
    """Base class for devices."""

    def __init__(self, api, raw):
        self.api = api
        self.raw = raw

    @property
    def id(self):
        return self.raw.get(ATTR_ID)

    @property
    def name(self):
        return self.raw.get(ATTR_NAME)

    @property
    def device_info(self):
        return DeviceInfo(self)

    @property
    def created_at(self):
        if ATTR_CREATED_AT not in self.raw:
            return None
        return datetime.utcfromtimestamp(self.raw[ATTR_CREATED_AT])

    @property
    def last_seen(self):
        if ATTR_LAST_SEEN not in self.raw:
            return None
        return datetime.utcfromtimestamp(self.raw[ATTR_LAST_SEEN])

    @property
    def reachable(self):
        return self.raw.get(ATTR_REACHABLE_STATE) == 1

    @property
    def has_light_control(self):
        return (ATTR_LIGHT_CONTROL in self.raw and
                len(self.raw.get(ATTR_LIGHT_CONTROL)) > 0)

    @property
    def light_control(self):
        return LightControl(self)

    def update(self):
        self.raw = self.api('get', [PATH_ROOT, self.id])

    def __repr__(self):
        return "<{} - {} ({})>".format(self.id, self.name,
                                       self.device_info.model_number)


class DeviceInfo:
    """Represent device information.

    http://www.openmobilealliance.org/tech/profiles/LWM2M_Device-v1_0.xml
    """
    ATTR_MANUFACTURER = "0"
    ATTR_MODEL_NUMBER = "1"
    ATTR_SERIAL = "2"
    ATTR_FIRMWARE_VERSION = "3"
    ATTR_POWER_SOURCE = "6"
    VALUE_POWER_SOURCES = {
        1: 'Internal Battery',
        2: 'External Battery',
        3: 'Battery',  # Not in spec, used by remote
        4: 'Power over Ethernet',
        5: 'USB',
        6: 'AC (Mains) power',
        7: 'Solar'
    }
    ATTR_BATTERY = "9"

    def __init__(self, device):
        self._device = device

    @property
    def manufacturer(self):
        """Human readable manufacturer name."""
        return self._device.raw[ATTR_DEVICE_INFO].get(
            DeviceInfo.ATTR_MANUFACTURER)

    @property
    def model_number(self):
        """A model identifier string (manufactuer specified string)."""
        return self._device.raw[ATTR_DEVICE_INFO].get(
            DeviceInfo.ATTR_MODEL_NUMBER)

    @property
    def serial(self):
        """Serial number string."""
        return self._device.raw[ATTR_DEVICE_INFO].get(
            DeviceInfo.ATTR_SERIAL)

    @property
    def firmware_version(self):
        """Current firmware version string of the device."""
        return self._device.raw[ATTR_DEVICE_INFO].get(
            DeviceInfo.ATTR_FIRMWARE_VERSION)

    @property
    def power_source(self):
        """Power source."""
        return self._device.raw[ATTR_DEVICE_INFO].get(
            DeviceInfo.ATTR_POWER_SOURCE)

    @property
    def power_source_str(self):
        """String representation of current power source."""
        if (DeviceInfo.ATTR_POWER_SOURCE not in
                self._device.raw[ATTR_DEVICE_INFO]):
            return None
        return DeviceInfo.VALUE_POWER_SOURCES.get(
            self._device.raw[ATTR_DEVICE_INFO][DeviceInfo.ATTR_POWER_SOURCE],
            'Unknown')

    @property
    def battery_level(self):
        """Battery in 0..100"""
        return self._device.raw[ATTR_DEVICE_INFO].get(
            DeviceInfo.ATTR_BATTERY)

    @property
    def raw(self):
        """Return raw data that it represents."""
        return self._device.raw[ATTR_DEVICE_INFO]


class LightControl:
    """Class to control the lights."""

    def __init__(self, device):
        self._device = device

    @property
    def lights(self):
        """Return light objects of the light control."""
        return [Light(self._device, i) for i in range(len(self.raw))]

    def set_dimmer(self, dimmer, *, index=0):
        """Set dimmer value of a light.

        Integer between 0..255
        """
        assert len(self.raw.get(ATTR_LIGHT_CONTROL, [])) == 1, \
            'Only devices with 1 light supported'

        self._device.api('put', [PATH_ROOT, self._device.id], {
            ATTR_LIGHT_CONTROL: [
                {
                    Light.ATTR_DIMMER: dimmer
                }
            ]
        })

    def set_light_xy_color(self, color_x, color_y, *, index=0):
        """Set xy color of the light."""
        assert len(self.raw.get(ATTR_LIGHT_CONTROL, [])) == 1, \
            'Only devices with 1 light supported'

        # TODO doesn't work yet

        self._device.api('put', [PATH_ROOT, self._device.id], {
            ATTR_LIGHT_CONTROL: [
                {
                    Light.ATTR_COLOR_X: color_x,
                    Light.ATTR_COLOR_Y: color_y,
                }
            ]
        })

    @property
    def raw(self):
        """Return raw data that it represents."""
        return self._device[ATTR_LIGHT_CONTROL]

    def __repr__(self):
        return '<LightControl for {} ({} lights)>'.format(self._device.name,
                                                          len(self.raw))


class Light:
    """Represent a light control.

    https://github.com/IPSO-Alliance/pub/blob/master/docs/IPSO-Smart-Objects.pdf
    """

    ATTR_STATE = "5850"  # 0 / 1
    ATTR_DIMMER = "5851"  # Dimmer, not following spec: 0..255
    ATTR_COLOR = "5706"  # string representing a value in some color space
    ATTR_COLOR_X = "5709"
    ATTR_COLOR_Y = "5710"

    def __init__(self, device, index):
        self.device = device
        self.index = index

    @property
    def state(self):
        return self.raw.get(Light.ATTR_STATE) == 1

    @property
    def dimmer(self):
        return self.raw.get(Light.ATTR_DIMMER)

    @property
    def xy_color(self):
        return (self.raw.get(Light.ATTR_COLOR_X),
                self.raw.get(Light.ATTR_COLOR_Y))

    @property
    def raw(self):
        """Return raw data that it represents."""
        return self.device.raw[ATTR_LIGHT_CONTROL][self.index]

    def __repr__(self):
        state = "on" if self.state else "off"
        return "<Light #{} - {}>".format(self.index, state)
