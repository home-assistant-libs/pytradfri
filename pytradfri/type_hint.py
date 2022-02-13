"""Type hints for API responses."""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from .const import (
    ATTR_AIR_PURIFIER_AIR_QUALITY,
    ATTR_AIR_PURIFIER_CONTROLS_LOCKED,
    ATTR_AIR_PURIFIER_FAN_SPEED,
    ATTR_AIR_PURIFIER_FILTER_LIFETIME_REMAINING,
    ATTR_AIR_PURIFIER_FILTER_LIFETIME_TOTAL,
    ATTR_AIR_PURIFIER_FILTER_RUNTIME,
    ATTR_AIR_PURIFIER_FILTER_STATUS,
    ATTR_AIR_PURIFIER_LEDS_OFF,
    ATTR_AIR_PURIFIER_MODE,
    ATTR_AIR_PURIFIER_MOTOR_RUNTIME_TOTAL,
    ATTR_APPLICATION_TYPE,
    ATTR_BLIND_CURRENT_POSITION,
    ATTR_CREATED_AT,
    ATTR_DEVICE_BATTERY,
    ATTR_DEVICE_FIRMWARE_VERSION,
    ATTR_DEVICE_INFO,
    ATTR_DEVICE_MANUFACTURER,
    ATTR_DEVICE_MODEL_NUMBER,
    ATTR_DEVICE_POWER_SOURCE,
    ATTR_DEVICE_SERIAL,
    ATTR_DEVICE_STATE,
    ATTR_ID,
    ATTR_LAST_SEEN,
    ATTR_LIGHT_CONTROL,
    ATTR_LIGHT_DIMMER,
    ATTR_NAME,
    ATTR_OTA_UPDATE_STATE,
    ATTR_REACHABLE_STATE,
    ATTR_START_BLINDS,
    ATTR_SWITCH_PLUG,
    ROOT_AIR_PURIFIER,
    ROOT_SIGNAL_REPEATER,
)


class AirPurifierResponse(BaseModel):
    """Represent the air purifier part of the device response."""

    air_quality: int = Field(alias=ATTR_AIR_PURIFIER_AIR_QUALITY)
    controls_locked: int = Field(alias=ATTR_AIR_PURIFIER_CONTROLS_LOCKED)
    fan_speed: int = Field(alias=ATTR_AIR_PURIFIER_FAN_SPEED)
    filter_lifetime_remaining: int = Field(
        alias=ATTR_AIR_PURIFIER_FILTER_LIFETIME_REMAINING
    )
    filter_lifetime_total: int = Field(alias=ATTR_AIR_PURIFIER_FILTER_LIFETIME_TOTAL)
    filter_runtime: int = Field(alias=ATTR_AIR_PURIFIER_FILTER_RUNTIME)
    filter_status: int = Field(alias=ATTR_AIR_PURIFIER_FILTER_STATUS)
    id: int = Field(alias=ATTR_ID)
    leds_off: int = Field(alias=ATTR_AIR_PURIFIER_LEDS_OFF)
    mode: int = Field(alias=ATTR_AIR_PURIFIER_MODE)
    motor_runtime_total: int = Field(alias=ATTR_AIR_PURIFIER_MOTOR_RUNTIME_TOTAL)


class BlindResponse(BaseModel):
    """Represent the blind part of the device response."""

    id: int = Field(alias=ATTR_ID)
    current_cover_position: int = Field(alias=ATTR_BLIND_CURRENT_POSITION)


class DeviceInfoResponse(BaseModel):
    """Represent the device info part of the device response."""

    manufacturer: str = Field(alias=ATTR_DEVICE_MANUFACTURER)
    model_number: str = Field(alias=ATTR_DEVICE_MODEL_NUMBER)
    serial: str = Field(alias=ATTR_DEVICE_SERIAL)
    firmware_version: str = Field(alias=ATTR_DEVICE_FIRMWARE_VERSION)
    power_source: int = Field(alias=ATTR_DEVICE_POWER_SOURCE)
    battery_level: int | None = Field(alias=ATTR_DEVICE_BATTERY)


class SocketResponse(BaseModel):
    """Represent the socket part of the device response."""

    id: int = Field(alias=ATTR_ID)
    state: int = Field(alias=ATTR_DEVICE_STATE)
    dimmer: int = Field(alias=ATTR_LIGHT_DIMMER)


class ApiResourceResponse(BaseModel):
    """Represent an API response."""

    air_purifier: list[AirPurifierResponse] | None = Field(alias=ROOT_AIR_PURIFIER)
    application_type: int = Field(alias=ATTR_APPLICATION_TYPE)
    blind: list[BlindResponse] | None = Field(alias=ATTR_START_BLINDS)
    created_at: int = Field(alias=ATTR_CREATED_AT)
    device_info: DeviceInfoResponse = Field(alias=ATTR_DEVICE_INFO)
    id: int = Field(alias=ATTR_ID)
    last_seen: int = Field(alias=ATTR_LAST_SEEN)
    light: list[Any] | None = Field(alias=ATTR_LIGHT_CONTROL)  # To be implemented later
    name: str = Field(alias=ATTR_NAME)
    ota_update_state: int = Field(alias=ATTR_OTA_UPDATE_STATE)
    reachable: int = Field(alias=ATTR_REACHABLE_STATE)
    signal_repeater: list[Any] | None = Field(
        alias=ROOT_SIGNAL_REPEATER
    )  # To be implemented later
    socket: list[SocketResponse] | None = Field(alias=ATTR_SWITCH_PLUG)
