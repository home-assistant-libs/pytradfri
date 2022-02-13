"""Resources for devices."""
from __future__ import annotations

from abc import abstractmethod
from datetime import datetime
from typing import Any, Callable, Dict, List, Union

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
    ATTR_NAME,
    ATTR_OTA_UPDATE_STATE,
    ATTR_REACHABLE_STATE,
)

# type alias
TypeRaw = Dict[str, Union[str, int, List[Dict[str, Union[str, int]]]]]
TypeRawSimple = Dict[str, Union[str, int]]
TypeRawList = Dict[str, List[Dict[str, Union[str, int]]]]


class DeviceInfoResponse(BaseModel):
    """Represent the device info part of the device response."""

    manufacturer: str = Field(alias=ATTR_DEVICE_MANUFACTURER)
    model_number: str = Field(alias=ATTR_DEVICE_MODEL_NUMBER)
    serial: str = Field(alias=ATTR_DEVICE_SERIAL)
    firmware_version: str = Field(alias=ATTR_DEVICE_FIRMWARE_VERSION)
    power_source: int = Field(alias=ATTR_DEVICE_POWER_SOURCE)
    battery_level: int | None = Field(alias=ATTR_DEVICE_BATTERY)


class ApiResourceResponse(BaseModel):
    """Represent an API response."""

    application_type: int = Field(alias=ATTR_APPLICATION_TYPE)
    created_at: int = Field(alias=ATTR_CREATED_AT)
    device_info: DeviceInfoResponse = Field(alias=ATTR_DEVICE_INFO)
    id: int = Field(alias=ATTR_ID)
    last_seen: int = Field(alias=ATTR_LAST_SEEN)
    name: str = Field(alias=ATTR_NAME)
    ota_update_state: int = Field(alias=ATTR_OTA_UPDATE_STATE)
    reachable: int = Field(alias=ATTR_REACHABLE_STATE)

    """
    air_purifier: list[Any] = Field(alias=ROOT_AIR_PURIFIER)
    blind: list[Any] = Field(alias=ATTR_START_BLINDS)
    light: list[Any] = Field(alias=ATTR_LIGHT_CONTROL)
    signal_repeater: list[Any] = Field(alias=ROOT_SIGNAL_REPEATER)
    socket: list[Any] = Field(alias=ATTR_SWITCH_PLUG)
    """


class ApiResource:
    """Base object for resources returned from the gateway."""

    _model_class: type[ApiResourceResponse] = ApiResourceResponse
    raw: ApiResourceResponse

    def __init__(self, raw: TypeRawList) -> None:
        """Initialize base object."""
        self.raw = self._model_class(**raw)

    @property
    def id(self) -> int | None:
        """Id."""
        return self.raw.id

    @property
    def name(self) -> str | None:
        """Name."""
        return self.raw.name

    @property
    def created_at(self) -> datetime | None:
        """Return timestamp of creation."""
        if self.raw.created_at:
            return datetime.utcfromtimestamp(self.raw.created_at)

        return None

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

        def observe_callback(value: ApiResourceResponse) -> None:
            """Call when end point is updated.

            Returns a Command.
            """
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

        def process_result(result: ApiResourceResponse) -> None:
            self.raw = result

        return Command("get", self.path, process_result=process_result)
