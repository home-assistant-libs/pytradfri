"""Classes to interact with devices."""
from datetime import datetime

from ..const import (
    ATTR_APPLICATION_TYPE,
    ATTR_DEVICE_INFO,
    ATTR_LAST_SEEN,
    ATTR_LIGHT_CONTROL,
    ATTR_REACHABLE_STATE,
    ATTR_START_BLINDS,
    ATTR_SWITCH_PLUG,
    ROOT_AIR_PURIFIER,
    ROOT_DEVICES,
    ROOT_SIGNAL_REPEATER,
)
from ..resource import ApiResource
from .air_purifier_control import AirPurifierControl
from .blind_control import BlindControl
from .light_control import LightControl
from .signal_repeater_control import SignalRepeaterControl
from .socket_control import SocketControl


class Device(ApiResource):
    """Base class for devices."""

    @property
    def application_type(self):
        """Return application type."""
        return self.raw.get(ATTR_APPLICATION_TYPE)

    @property
    def path(self):
        """Return path."""
        return [ROOT_DEVICES, self.id]

    @property
    def device_info(self):
        """Return Device information."""
        return DeviceInfo(self)

    @property
    def last_seen(self):
        """Return timestamp when last seen."""
        if ATTR_LAST_SEEN not in self.raw:
            return None
        return datetime.utcfromtimestamp(self.raw[ATTR_LAST_SEEN])

    @property
    def reachable(self):
        """Check if gateway is reachable."""
        return self.raw.get(ATTR_REACHABLE_STATE) == 1

    @property
    def has_light_control(self):
        """Check if light_control is present."""
        return self.raw is not None and len(self.raw.get(ATTR_LIGHT_CONTROL, "")) > 0

    @property
    def light_control(self):
        """Return light_control."""
        return LightControl(self)

    @property
    def has_socket_control(self):
        """Check if socket_control is present."""
        return self.raw is not None and len(self.raw.get(ATTR_SWITCH_PLUG, "")) > 0

    @property
    def socket_control(self):
        """Return socket_control."""
        if self.has_socket_control:
            return SocketControl(self)
        return None

    @property
    def has_blind_control(self):
        """Check if blind_control is present."""
        return self.raw is not None and len(self.raw.get(ATTR_START_BLINDS, "")) > 0

    @property
    def blind_control(self):
        """Return blind_control."""
        if self.has_blind_control:
            return BlindControl(self)
        return None

    @property
    def has_signal_repeater_control(self):
        """Check if signal_repeater_control is present."""
        return self.raw is not None and len(self.raw.get(ROOT_SIGNAL_REPEATER, "")) > 0

    @property
    def signal_repeater_control(self):
        """Return signal_repeater control, if any."""
        if self.has_signal_repeater_control:
            return SignalRepeaterControl(self)
        return None

    @property
    def has_air_purifier_control(self):
        """Check if air_purifier_control is present."""
        return self.raw is not None and len(self.raw.get(ROOT_AIR_PURIFIER, "")) > 0

    @property
    def air_purifier_control(self):
        """Return air_purifier control, if any."""
        if self.has_air_purifier_control:
            return AirPurifierControl(self)
        return None

    def __repr__(self):
        """Return representation of class object."""
        return f"<{self.id} - {self.name} ({self.device_info.model_number})>"


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
        """Create object of class."""
        self._device = device

    @property
    def manufacturer(self):
        """Human readable manufacturer name."""
        return self.raw.get(DeviceInfo.ATTR_MANUFACTURER)

    @property
    def model_number(self):
        """Return model identifier string (manufacturer specified string)."""
        return self.raw.get(DeviceInfo.ATTR_MODEL_NUMBER)

    @property
    def serial(self):
        """Return serial string."""
        return self.raw.get(DeviceInfo.ATTR_SERIAL)

    @property
    def firmware_version(self):
        """Return current firmware version of device."""
        return self.raw.get(DeviceInfo.ATTR_FIRMWARE_VERSION)

    @property
    def power_source(self):
        """Power source."""
        return self.raw.get(DeviceInfo.ATTR_POWER_SOURCE)

    @property
    def power_source_str(self):
        """Represent current power source."""
        if DeviceInfo.ATTR_POWER_SOURCE not in self.raw:
            return None
        return DeviceInfo.VALUE_POWER_SOURCES.get(self.power_source, "Unknown")

    @property
    def battery_level(self):
        """Battery in 0..100."""
        return self.raw.get(DeviceInfo.ATTR_BATTERY)

    @property
    def raw(self):
        """Return raw data that it represents."""
        return self._device.raw[ATTR_DEVICE_INFO]
