"""Resources for devices."""
from __future__ import annotations

from abc import abstractmethod
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .command import Command, TypeProcessResultCb
from .const import (
    ATTR_APPLICATION_TYPE,
    ATTR_CREATED_AT,
    ATTR_DEVICE_BATTERY,
    ATTR_DEVICE_FIRMWARE_VERSION,
    ATTR_DEVICE_INFO,
    ATTR_DEVICE_MANUFACTURER,
    ATTR_DEVICE_MODEL_NUMBER,
    ATTR_DEVICE_POWER_SOURCE,
    ATTR_DEVICE_SERIAL,
    ATTR_ID,
    ATTR_LAST_SEEN,
    ATTR_LIGHT_CONTROL,
    ATTR_NAME,
    ATTR_OTA_UPDATE_STATE,
    ATTR_REACHABLE_STATE,
    ATTR_START_BLINDS,
    ATTR_SWITCH_PLUG,
    ROOT_AIR_PURIFIER,
    ROOT_SIGNAL_REPEATER,
)
from .typing import AirPurifierResponse, BlindResponse

# type alias
TypeRaw = Dict[str, Union[str, int, List[Dict[str, Union[str, int]]]]]
TypeRawSimple = Dict[str, Union[str, int]]
TypeRawList = Dict[str, List[Dict[str, Union[str, int]]]]


class ApiResourceResponse(BaseModel):
    """Represent a resource response."""

    id: int = Field(alias=ATTR_ID)
    name: str = Field(alias=ATTR_NAME)
    created_at: Optional[int] = Field(alias=ATTR_CREATED_AT)
    ota_update_state: Optional[int] = Field(alias=ATTR_OTA_UPDATE_STATE)


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

    # Type with Any for now to allow smaller typing work chunks

    air_purifier_control: Optional[List[AirPurifierResponse]] = Field(
        alias=ROOT_AIR_PURIFIER
    )
    application_type: int = Field(alias=ATTR_APPLICATION_TYPE)
    blind_control: Optional[List[BlindResponse]] = Field(alias=ATTR_START_BLINDS)
    device_info: DeviceInfoResponse = Field(alias=ATTR_DEVICE_INFO)
    last_seen: Optional[int] = Field(alias=ATTR_LAST_SEEN)
    light_control: Optional[List[Dict[str, Any]]] = Field(alias=ATTR_LIGHT_CONTROL)
    reachable: int = Field(alias=ATTR_REACHABLE_STATE)
    signal_repeater_control: Optional[List[Dict[str, Any]]] = Field(
        alias=ROOT_SIGNAL_REPEATER
    )
    socket_control: Optional[List[Dict[str, Any]]] = Field(alias=ATTR_SWITCH_PLUG)


class ApiResource:
    """Base object for resources returned from the gateway."""

    _model_class: type[ApiResourceResponse] | None = None
    raw: TypeRaw | ApiResourceResponse

    def __init__(self, raw: TypeRaw) -> None:
        """Initialize base object."""
        if self._model_class:
            self.raw = self._model_class(**raw)
        else:
            self.raw = raw

    @property
    def id(self) -> int | None:
        """Id."""
        if self._model_class:
            resource_id = self.raw.id  # type: ignore[union-attr]
        else:
            resource_id = self.raw[ATTR_ID]  # type: ignore[index]
        return resource_id

    @property
    def name(self) -> str | None:
        """Name."""
        if self._model_class:
            name = self.raw.name  # type: ignore[union-attr]
        else:
            name = self.raw[ATTR_NAME]  # type: ignore[index]
        return name

    @property
    def created_at(self) -> datetime | None:
        """Return timestamp of creation."""
        if self._model_class:
            created_at = self.raw.created_at  # type: ignore[union-attr]
        else:
            created_at = self.raw[ATTR_CREATED_AT]  # type: ignore[index]

        if created_at is None:
            return None
        return datetime.utcfromtimestamp(created_at)

    @property
    @abstractmethod
    def path(self) -> list[str]:
        """Path to resource."""

    def observe(
        self,
        callback: TypeProcessResultCb,
        err_callback: Callable[[Exception], None] | None,
        duration: int = 60,
    ) -> Command:
        """Observe resource and call callback when updated."""

        def observe_callback(value: TypeRaw) -> None:
            """Call when end point is updated.

            Returns a Command.
            """
            if self._model_class:
                self.raw = self._model_class(**value)
            else:
                self.raw = value
            if callback:
                callback(self)

        return Command(
            "get",
            self.path,
            process_result=observe_callback,
            err_callback=err_callback,
            observe=True,
            observe_duration=duration,
        )

    def set_name(self, name: str) -> Command:
        """Set group name."""
        return self.set_values({ATTR_NAME: name})

    def set_values(self, values: Any) -> Command:
        """Help to set values for group.

        Helper to set values for group.
        Returns a Command.
        """
        return Command("put", self.path, values)

    def update(self) -> Command:
        """
        Update the group.

        Returns a Command.
        """

        def process_result(result: TypeRaw) -> None:
            if self._model_class:
                self.raw = self._model_class(**result)
            else:
                self.raw = result

        return Command("get", self.path, process_result=process_result)
