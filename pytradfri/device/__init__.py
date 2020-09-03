"""Classes to interact with devices."""
from datetime import datetime

from pytradfri.const import (
    ATTR_APPLICATION_TYPE,
    ROOT_DEVICES,
    ATTR_LAST_SEEN,
    ATTR_REACHABLE_STATE,
    ATTR_LIGHT_CONTROL,
    ATTR_SWITCH_PLUG,
    ATTR_DEVICE_INFO,
    ATTR_START_BLINDS,
    ROOT_SIGNAL_REPEATER,
)
from pytradfri.device.blind_control import BlindControl
from pytradfri.device.light_control import LightControl
from pytradfri.device.signal_repeater_control import SignalRepeaterControl
from pytradfri.device.socket_control import SocketControl
from pytradfri.resource import ApiResource


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
        return self.raw is not None and len(self.raw.get(ATTR_LIGHT_CONTROL, "")) > 0

    @property
    def light_control(self):
        return LightControl(self)

    @property
    def has_socket_control(self):
        return self.raw is not None and len(self.raw.get(ATTR_SWITCH_PLUG, "")) > 0

    @property
    def socket_control(self):
        if self.has_socket_control:
            return SocketControl(self)

    @property
    def has_blind_control(self):
        return self.raw is not None and len(self.raw.get(ATTR_START_BLINDS, "")) > 0

    @property
    def blind_control(self):
        if self.has_blind_control:
            return BlindControl(self)

    @property
    def has_signal_repeater_control(self):
        return self.raw is not None and len(self.raw.get(ROOT_SIGNAL_REPEATER, "")) > 0

    @property
    def signal_repeater_control(self):
        if self.has_signal_repeater_control:
            return SignalRepeaterControl(self)

    def __repr__(self):
        return "<{} - {} ({})>".format(
            self.id, self.name, self.device_info.model_number
        )


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
        1: "Internal Battery",
        2: "External Battery",
        3: "Battery",  # Not in spec, used by remote
        4: "Power over Ethernet",
        5: "USB",
        6: "AC (Mains) power",
        7: "Solar",
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
        """A model identifier string (manufacturer specified string)."""
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
        return DeviceInfo.VALUE_POWER_SOURCES.get(self.power_source, "Unknown")

    @property
    def battery_level(self):
        """Battery in 0..100"""
        return self.raw.get(DeviceInfo.ATTR_BATTERY)

    @property
    def raw(self):
        """Return raw data that it represents."""
        return self._device.raw[ATTR_DEVICE_INFO]
