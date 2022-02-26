"""Classes to interact with devices."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from ..const import ROOT_DEVICES
from ..resource import ApiResource, DeviceInfoResponse, DeviceResponse
from .air_purifier_control import AirPurifierControl
from .blind_control import BlindControl
from .light_control import LightControl
from .signal_repeater_control import SignalRepeaterControl
from .socket_control import SocketControl


class Device(ApiResource):
    """Base class for devices."""

    _model_class: type[DeviceResponse] = DeviceResponse
    raw: DeviceResponse

    @property
    def application_type(self) -> int | None:
        """Return application type."""
        return self.raw.application_type

    @property
    def path(self):
        """Return path."""
        return [ROOT_DEVICES, self.id]

    @property
    def device_info(self) -> Optional["DeviceInfo"]:
        """Return Device information."""
        if self._model_class:
            return DeviceInfo(self)

        return None

    @property
    def last_seen(self) -> datetime | None:
        """Return timestamp when last seen."""
        last_seen = self.raw.last_seen

        if last_seen:
            return datetime.utcfromtimestamp(last_seen)

        return None

    @property
    def reachable(self) -> bool:
        """Check if gateway is reachable."""
        return self.raw.reachable == 1

    @property
    def has_light_control(self) -> bool:
        """Check if light_control is present."""
        return self.raw.light_control is not None

    @property
    def light_control(self) -> LightControl | None:
        """Return light_control."""
        if self.has_light_control:
            return LightControl(self)

        return None

    @property
    def has_socket_control(self) -> bool:
        """Check if socket_control is present."""
        return self.raw.socket_control is not None

    @property
    def socket_control(self) -> SocketControl | None:
        """Return socket_control."""
        if self.has_socket_control:
            return SocketControl(self)
        return None

    @property
    def has_blind_control(self) -> bool:
        """Check if blind_control is present."""
        return self.raw.blind_control is not None

    @property
    def blind_control(self) -> BlindControl | None:
        """Return blind_control."""
        if self.has_blind_control:
            return BlindControl(self)
        return None

    @property
    def has_signal_repeater_control(self) -> bool:
        """Check if signal_repeater_control is present."""
        return self.raw.signal_repeater_control is not None

    @property
    def signal_repeater_control(self) -> SignalRepeaterControl | None:
        """Return signal_repeater control, if any."""
        if self.has_signal_repeater_control:
            return SignalRepeaterControl(self)
        return None

    @property
    def has_air_purifier_control(self) -> bool:
        """Check if air_purifier_control is present."""
        return self.raw.air_purifier_control is not None

    @property
    def air_purifier_control(self) -> AirPurifierControl | None:
        """Return air_purifier control, if any."""
        if self.has_air_purifier_control:
            return AirPurifierControl(self)
        return None

    def __repr__(self) -> str:
        """Return representation of class object."""
        if self.device_info:
            return f"<{self.id} - {self.name} ({self.device_info.model_number})>"

        return f"<{self.id} - {self.name})>"


class DeviceInfo:
    """Represent device information.

    http://www.openmobilealliance.org/tech/profiles/LWM2M_Device-v1_0.xml
    """

    VALUE_POWER_SOURCES = {
        1: "Internal Battery",
        2: "External Battery",
        3: "Battery",  # Not in spec, used by remote
        4: "Power over Ethernet",
        5: "USB",
        6: "AC (Mains) power",
        7: "Solar",
    }

    def __init__(self, device: Device) -> None:
        """Create object of class."""
        self._device = device

    @property
    def manufacturer(self) -> str | None:
        """Human readable manufacturer name."""
        if self.raw:
            return self.raw.manufacturer

        return None

    @property
    def model_number(self) -> str | None:
        """Return model identifier string (manufacturer specified string)."""
        if self.raw:
            return self.raw.model_number

        return None

    @property
    def serial(self) -> str | None:
        """Return serial string."""
        if self.raw:
            return self.raw.serial

        return None

    @property
    def firmware_version(self) -> str | None:
        """Return current firmware version of device."""
        if self.raw:
            return self.raw.firmware_version

        return None

    @property
    def power_source(self) -> int | None:
        """Power source."""
        if self.raw:
            return self.raw.power_source

        return None

    @property
    def power_source_str(self) -> Optional[str]:
        """Represent current power source."""
        if self.raw and self.raw.power_source:
            return self.VALUE_POWER_SOURCES.get(self.raw.power_source, "Unknown")

        return None

    @property
    def battery_level(self) -> Optional[int]:
        """Battery in 0..100."""
        if self.raw and self.raw.battery_level:
            return self.raw.battery_level

        return None

    @property
    def raw(self) -> DeviceInfoResponse | None:
        """Return raw data that it represents."""
        if self._device.raw.device_info:
            return self._device.raw.device_info

        return None
