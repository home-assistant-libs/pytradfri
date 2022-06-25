"""Classes to interact with devices."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from ..const import (
    ATTR_APPLICATION_TYPE,
    ATTR_DEVICE_BATTERY,
    ATTR_DEVICE_FIRMWARE_VERSION,
    ATTR_DEVICE_INFO,
    ATTR_DEVICE_MANUFACTURER,
    ATTR_DEVICE_MODEL_NUMBER,
    ATTR_DEVICE_POWER_SOURCE,
    ATTR_DEVICE_SERIAL,
    ATTR_LAST_SEEN,
    ATTR_LIGHT_CONTROL,
    ATTR_REACHABLE_STATE,
    ATTR_START_BLINDS,
    ATTR_SWITCH_PLUG,
    ROOT_AIR_PURIFIER,
    ROOT_DEVICES,
    ROOT_SIGNAL_REPEATER,
)
from ..device.light import LightResponse
from ..resource import ApiResource, ApiResourceResponse
from .air_purifier import AirPurifierResponse
from .air_purifier_control import AirPurifierControl
from .blind import BlindResponse
from .blind_control import BlindControl
from .light_control import LightControl
from .signal_repeater import SignalRepeaterResponse
from .signal_repeater_control import SignalRepeaterControl
from .socket import SocketResponse
from .socket_control import SocketControl


class DeviceInfoResponse(BaseModel):
    """Represent the device info part of the device response."""

    manufacturer: str = Field(alias=ATTR_DEVICE_MANUFACTURER)
    model_number: str = Field(alias=ATTR_DEVICE_MODEL_NUMBER)
    serial: str = Field(alias=ATTR_DEVICE_SERIAL)
    firmware_version: str = Field(alias=ATTR_DEVICE_FIRMWARE_VERSION)
    power_source: Optional[int] = Field(alias=ATTR_DEVICE_POWER_SOURCE)
    battery_level: Optional[int] = Field(alias=ATTR_DEVICE_BATTERY)


class DeviceResponse(ApiResourceResponse):
    """Represent a device response."""

    air_purifier_control: Optional[list[AirPurifierResponse]] = Field(
        alias=ROOT_AIR_PURIFIER
    )
    application_type: int = Field(alias=ATTR_APPLICATION_TYPE)
    blind_control: Optional[list[BlindResponse]] = Field(alias=ATTR_START_BLINDS)
    device_info: DeviceInfoResponse = Field(alias=ATTR_DEVICE_INFO)
    last_seen: Optional[int] = Field(alias=ATTR_LAST_SEEN)
    light_control: Optional[list[LightResponse]] = Field(alias=ATTR_LIGHT_CONTROL)
    reachable: int = Field(alias=ATTR_REACHABLE_STATE)
    signal_repeater_control: Optional[list[SignalRepeaterResponse]] = Field(
        alias=ROOT_SIGNAL_REPEATER
    )
    socket_control: Optional[list[SocketResponse]] = Field(alias=ATTR_SWITCH_PLUG)


class Device(ApiResource):
    """Base class for devices."""

    _model_class: type[DeviceResponse] = DeviceResponse
    raw: DeviceResponse

    @property
    def application_type(self) -> int:
        """Return application type."""
        return self.raw.application_type

    @property
    def path(self) -> list[str]:
        """Return path."""
        return [ROOT_DEVICES, str(self.id)]

    @property
    def device_info(self) -> "DeviceInfo":
        """Return Device information."""
        return DeviceInfo(self)

    @property
    def last_seen(self) -> datetime | None:
        """Return timestamp when last seen."""
        last_seen = self.raw.last_seen

        if last_seen is not None:
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
        return f"<{self.id} - {self.name} ({self.device_info.model_number})>"


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
    def manufacturer(self) -> str:
        """Human readable manufacturer name."""
        return self.raw.manufacturer

    @property
    def model_number(self) -> str:
        """Return model identifier string (manufacturer specified string)."""
        return self.raw.model_number

    @property
    def serial(self) -> str:
        """Return serial string."""
        return self.raw.serial

    @property
    def firmware_version(self) -> str:
        """Return current firmware version of device."""
        return self.raw.firmware_version

    @property
    def power_source(self) -> int | None:
        """Power source."""
        return self.raw.power_source

    @property
    def power_source_str(self) -> str | None:
        """Represent current power source."""
        if self.raw.power_source is not None:
            return self.VALUE_POWER_SOURCES.get(self.raw.power_source, "Unknown")

        return None

    @property
    def battery_level(self) -> int | None:
        """Battery in 0..100."""
        return self.raw.battery_level

    @property
    def raw(self) -> DeviceInfoResponse:
        """Return raw data that it represents."""
        return self._device.raw.device_info
