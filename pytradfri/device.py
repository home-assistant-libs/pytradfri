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
    ATTR_LIGHT_DIMMER,
    ATTR_LIGHT_COLOR_X,
    ATTR_LIGHT_COLOR_Y,
    ATTR_LIGHT_COLOR_SATURATION,
    ATTR_LIGHT_COLOR_HUE,
    ATTR_LIGHT_COLOR_HEX,
    ATTR_LIGHT_MIREDS,
    ATTR_TRANSITION_TIME,
    RANGE_MIREDS,
    RANGE_HUE,
    RANGE_SATURATION,
    RANGE_BRIGHTNESS,
    RANGE_X,
    RANGE_Y,
    SUPPORT_BRIGHTNESS,
    SUPPORT_COLOR_TEMP,
    SUPPORT_HEX_COLOR,
    SUPPORT_XY_COLOR,
    ATTR_SWITCH_PLUG,
    ATTR_DEVICE_STATE)
from .color import COLORS, supported_features
from .resource import ApiResource
from .error import ColorError


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
        return (self.raw is not None and
                len(self.raw.get(ATTR_LIGHT_CONTROL, "")) > 0)

    @property
    def light_control(self):
        return LightControl(self)

    @property
    def has_socket_control(self):
        return (self.raw is not None and
                len(self.raw.get(ATTR_SWITCH_PLUG, "")) > 0)

    @property
    def socket_control(self):
        if self.has_socket_control:
            return SocketControl(self)

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

        self.can_set_dimmer = None
        self.can_set_temp = None
        self.can_set_xy = None
        self.can_set_color = None
        self.can_combine_commands = None

        if ATTR_LIGHT_DIMMER in self.raw[0]:
            self.can_set_dimmer = True

        if ATTR_LIGHT_MIREDS in self.raw[0]:
            self.can_set_temp = True

        if ATTR_LIGHT_COLOR_X in self.raw[0]:
            self.can_set_xy = True

        if ATTR_LIGHT_COLOR_HUE in self.raw[0]:
            self.can_set_color = True

        # Currently uncertain which bulbs are capable of setting
        # multiple values simultaneously. As of gateway firmware
        # 1.3.14 1st party bulbs do not seem to support this properly,
        # but (at least some) hue bulbs do.
        if 'Philips' in self._device.device_info.manufacturer:
            self.can_combine_commands = True

        self.min_mireds = RANGE_MIREDS[0]
        self.max_mireds = RANGE_MIREDS[1]

        self.min_hue = RANGE_HUE[0]
        self.max_hue = RANGE_HUE[1]

        self.min_saturation = RANGE_SATURATION[0]
        self.max_saturation = RANGE_SATURATION[1]

    @property
    def raw(self):
        """Return raw data that it represents."""
        return self._device.raw[ATTR_LIGHT_CONTROL]

    @property
    def lights(self):
        """Return light objects of the light control."""
        return [Light(self._device, i) for i in range(len(self.raw))]

    def set_state(self, state, *, index=0):
        """Set state of a light."""
        return self.set_values({
            ATTR_DEVICE_STATE: int(state)
        }, index=index)

    def set_dimmer(self, dimmer, *, index=0, transition_time=None):
        """Set dimmer value of a light.
        transition_time: Integer representing tenth of a second (default None)
        """
        self._value_validate(dimmer, RANGE_BRIGHTNESS, "Dimmer")

        values = {
            ATTR_LIGHT_DIMMER: dimmer
        }

        if transition_time is not None:
            values[ATTR_TRANSITION_TIME] = transition_time

        return self.set_values(values, index=index)

    def set_color_temp(self, color_temp, *, index=0, transition_time=None):
        """Set color temp a light."""
        self._value_validate(color_temp, RANGE_MIREDS, "Color temperature")

        values = {
            ATTR_LIGHT_MIREDS: color_temp
        }

        if transition_time is not None:
            values[ATTR_TRANSITION_TIME] = transition_time

        return self.set_values(values, index=index)

    def set_hex_color(self, color, *, index=0, transition_time=None):
        """Set hex color of the light."""
        values = {
            ATTR_LIGHT_COLOR_HEX: color,
        }

        if transition_time is not None:
            values[ATTR_TRANSITION_TIME] = transition_time

        return self.set_values(values, index=index)

    def set_xy_color(self, color_x, color_y, *, index=0, transition_time=None):
        """Set xy color of the light."""
        self._value_validate(color_x, RANGE_X, "X color")
        self._value_validate(color_y, RANGE_Y, "Y color")

        values = {
            ATTR_LIGHT_COLOR_X: color_x,
            ATTR_LIGHT_COLOR_Y: color_y
        }

        if transition_time is not None:
            values[ATTR_TRANSITION_TIME] = transition_time

        return self.set_values(values, index=index)

    def set_hsb(self, hue, saturation, brightness=None, *, index=0,
                transition_time=None):
        """Set HSB color settings of the light."""
        self._value_validate(hue, RANGE_HUE, "Hue")
        self._value_validate(saturation, RANGE_SATURATION, "Saturation")

        values = {
            ATTR_LIGHT_COLOR_SATURATION: saturation,
            ATTR_LIGHT_COLOR_HUE: hue
        }

        if brightness is not None:
            values[ATTR_LIGHT_DIMMER] = brightness
            self._value_validate(brightness, RANGE_BRIGHTNESS, "Brightness")

        if transition_time is not None:
            values[ATTR_TRANSITION_TIME] = transition_time

        return self.set_values(values, index=index)

    def set_predefined_color(self, colorname, *, index=0,
                             transition_time=None):
        try:
            color = COLORS[colorname.lower().replace(" ", "_")]
            return self.set_hex_color(color, index=index,
                                      transition_time=transition_time)
        except KeyError:
            raise ColorError('Invalid color specified: %s',
                             colorname)

    def _value_validate(self, value, rnge, identifier="Given"):
        """
        Make sure a value is within a given range
        """
        if value is not None and (value < rnge[0] or value > rnge[1]):
            raise ValueError('%s value must be between %d and %d.'
                             % (identifier, rnge[0], rnge[1]))

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
    """Represent a light.

    https://github.com/IPSO-Alliance/pub/blob/master/docs/IPSO-Smart-Objects.pdf
    """

    def __init__(self, device, index):
        self.device = device
        self.index = index

    @property
    def supported_features(self):
        return supported_features(self.raw)

    @property
    def state(self):
        return self.raw.get(ATTR_DEVICE_STATE) == 1

    @property
    def dimmer(self):
        if self.supported_features & SUPPORT_BRIGHTNESS:
            return self.raw.get(ATTR_LIGHT_DIMMER)

    @property
    def color_temp(self):
        if self.supported_features & SUPPORT_COLOR_TEMP:
            if self.raw.get(ATTR_LIGHT_MIREDS) != 0:
                return self.raw.get(ATTR_LIGHT_MIREDS)

    @property
    def hex_color(self):
        if self.supported_features & SUPPORT_HEX_COLOR:
            return self.raw.get(ATTR_LIGHT_COLOR_HEX)

    @property
    def xy_color(self):
        if self.supported_features & SUPPORT_XY_COLOR:
            return (self.raw.get(ATTR_LIGHT_COLOR_X),
                    self.raw.get(ATTR_LIGHT_COLOR_Y))

    @property
    def hsb_xy_color(self):
        return (self.raw.get(ATTR_LIGHT_COLOR_HUE),
                self.raw.get(ATTR_LIGHT_COLOR_SATURATION),
                self.raw.get(ATTR_LIGHT_DIMMER),
                self.raw.get(ATTR_LIGHT_COLOR_X),
                self.raw.get(ATTR_LIGHT_COLOR_Y))

    @property
    def raw(self):
        """Return raw data that it represents."""
        return self.device.raw[ATTR_LIGHT_CONTROL][self.index]

    def __repr__(self):
        state = "on" if self.state else "off"
        return "<Light #{} - " \
               "name: {}, " \
               "state: {}, " \
               "dimmer: {}, "\
               "hex_color: {}, " \
               "xy_color: {}, " \
               "hsb_xy_color: {}, "\
               "supported features: {} " \
               ">".format(self.index, self.device.name, state, self.dimmer,
                          self.hex_color, self.xy_color,
                          self.hsb_xy_color, self.supported_features)


class SocketControl:
    """Class to control the sockets."""

    def __init__(self, device):
        self._device = device

    @property
    def raw(self):
        """Return raw data that it represents."""
        return self._device.raw[ATTR_SWITCH_PLUG]

    @property
    def sockets(self):
        """Return socket objects of the socket control."""
        return [Socket(self._device, i) for i in range(len(self.raw))]

    def set_state(self, state, *, index=0):
        """Set state of a socket."""
        return self.set_values({
            ATTR_DEVICE_STATE: int(state)
        }, index=index)

    def set_values(self, values, *, index=0):
        """
        Set values on socket control.
        Returns a Command.
        """
        assert len(self.raw) == 1, \
            'Only devices with 1 socket supported'

        return Command('put', self._device.path, {
            ATTR_SWITCH_PLUG: [
                values
            ]
        })

    def __repr__(self):
        return '<SocketControl for {} ({} sockets)>'.format(self._device.name,
                                                            len(self.raw))


class Socket:
    """Represent a socket."""

    def __init__(self, device, index):
        self.device = device
        self.index = index

    @property
    def state(self):
        return self.raw.get(ATTR_DEVICE_STATE) == 1

    @property
    def raw(self):
        """Return raw data that it represents."""
        return self.device.raw[ATTR_SWITCH_PLUG][self.index]

    def __repr__(self):
        state = "on" if self.state else "off"
        return "<Socket #{} - " \
               "name: {}, " \
               "state: {}" \
               ">".format(self.index, self.device.name, state)
