"""Classes to interact with devices."""
from datetime import datetime

from .command import Command
from .const import (
    ROOT_DEVICES,
    ATTR_APPLICATION_TYPE,
    ATTR_DEVICE_INFO,
    ATTR_REACHABLE_STATE,
    ATTR_LAST_SEEN,
    ATTR_LIGHT_CONTROL,
    ATTR_LIGHT_STATE,
    ATTR_LIGHT_DIMMER,
    ATTR_LIGHT_COLOR_X,
    ATTR_LIGHT_COLOR_Y,
    ATTR_LIGHT_COLOR,
    ATTR_TRANSITION_TIME
)
from .resource import ApiResource


class Device(ApiResource):
    """Base class for devices."""

    @property
    def application_type(self):
        return self.raw.get(ATTR_APPLICATION_TYPE)

    @property
    def path(self):
        return [ROOT_DEVICES, self.id]

    @property
    def device_info(self):
        return DeviceInfo(self)

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
        return self.raw.get(DeviceInfo.ATTR_MANUFACTURER)

    @property
    def model_number(self):
        """A model identifier string (manufactuer specified string)."""
        return self.raw.get(DeviceInfo.ATTR_MODEL_NUMBER)

    @property
    def serial(self):
        """Serial number string."""
        return self.raw.get(DeviceInfo.ATTR_SERIAL)

    @property
    def firmware_version(self):
        """Current firmware version string of the device."""
        return self.raw.get(DeviceInfo.ATTR_FIRMWARE_VERSION)

    @property
    def power_source(self):
        """Power source."""
        return self.raw.get(DeviceInfo.ATTR_POWER_SOURCE)

    @property
    def power_source_str(self):
        """String representation of current power source."""
        if DeviceInfo.ATTR_POWER_SOURCE not in self.raw:
            return None
        return DeviceInfo.VALUE_POWER_SOURCES.get(self.power_source, 'Unknown')

    @property
    def battery_level(self):
        """Battery in 0..100"""
        return self.raw.get(DeviceInfo.ATTR_BATTERY)

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

    @property
    def raw(self):
        """Return raw data that it represents."""
        return self._device.raw[ATTR_LIGHT_CONTROL]

    def set_state(self, state, *, index=0):
        """Set state of a light."""
        return self.set_values({
            ATTR_LIGHT_STATE: int(state)
        }, index=index)

    def set_dimmer(self, dimmer, *, index=0, transition_time=None):
        """Set dimmer value of a light.

        dimmer: Integer between 0..255
        transition_time: Integer representing tenth of a second (default None)
        """
        values = {
            ATTR_LIGHT_DIMMER: dimmer
        }
        if transition_time is not None:
            values[ATTR_TRANSITION_TIME] = transition_time

        return self.set_values(values, index=index)

    def set_hex_color(self, color, *, index=0):
        """Set xy color of the light."""
        return self.set_values({
            ATTR_LIGHT_COLOR: color,
        }, index=index)

    def set_xy_color(self, color_x, color_y, *, index=0):
        """Set xy color of the light."""
        return self.set_values({
            ATTR_LIGHT_COLOR_X: color_x,
            ATTR_LIGHT_COLOR_Y: color_y
        }, index=index)

    def set_values(self, values, *, index=0):
        """
        Set values on light control.

        Returns a Command.
        """
        assert len(self.raw) == 1, \
            'Only devices with 1 light supported'

        return Command('put', self._device.path, {
            ATTR_LIGHT_CONTROL: [
                values
            ]
        })

    def __repr__(self):
        return '<LightControl for {} ({} lights)>'.format(self._device.name,
                                                          len(self.raw))


class Light:
    """Represent a light control.

    https://github.com/IPSO-Alliance/pub/blob/master/docs/IPSO-Smart-Objects.pdf
    """

    def __init__(self, device, index):
        self.device = device
        self.index = index

    @property
    def state(self):
        return self.raw.get(ATTR_LIGHT_STATE) == 1

    @property
    def dimmer(self):
        return self.raw.get(ATTR_LIGHT_DIMMER)

    @property
    def hex_color(self):
        return self.raw.get(ATTR_LIGHT_COLOR)

    @property
    def xy_color(self):
        return (self.raw.get(ATTR_LIGHT_COLOR_X),
                self.raw.get(ATTR_LIGHT_COLOR_Y))

    @property
    def raw(self):
        """Return raw data that it represents."""
        return self.device.raw[ATTR_LIGHT_CONTROL][self.index]

    def __repr__(self):
        state = "on" if self.state else "off"
        return "<Light #{} - " \
               "state: {}, " \
               "dimmer: {}, "\
               "hex_color: {}, " \
               "xy_color: {}" \
               ">".format(self.index, state, self.dimmer, self.hex_color,
                          self.xy_color)
