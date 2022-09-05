"""Represent the gateway."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field

from .command import Command
from .const import (
    ATTR_ALEXA_PAIR_STATUS,
    ATTR_AUTH,
    ATTR_CERTIFICATE_PROV,
    ATTR_COMMISSIONING_MODE,
    ATTR_CURRENT_TIME_ISO8601,
    ATTR_CURRENT_TIME_UNIX,
    ATTR_FIRMWARE_VERSION,
    ATTR_FIRST_SETUP,
    ATTR_GATEWAY_FACTORY_DEFAULTS,
    ATTR_GATEWAY_ID,
    ATTR_GATEWAY_INFO,
    ATTR_GATEWAY_REBOOT,
    ATTR_GATEWAY_TIME_SOURCE,
    ATTR_GATEWAY_UPDATE_PROGRESS,
    ATTR_GOOGLE_HOME_PAIR_STATUS,
    ATTR_HOMEKIT_ID,
    ATTR_IDENTITY,
    ATTR_NTP,
    ATTR_OTA_TYPE,
    ATTR_OTA_UPDATE_STATE,
    ATTR_PSK,
    ROOT_DEVICES,
    ROOT_GATEWAY,
    ROOT_GROUPS,
    ROOT_MOODS,
    ROOT_SMART_TASKS,
)
from .device import Device
from .group import Group
from .mood import Mood
from .resource import TypeRaw
from .smart_task import SmartTask


class GatewayInfoResponse(BaseModel):
    """Represent API response for the gateway."""

    certificate_provisioned: int = Field(alias=ATTR_CERTIFICATE_PROV)
    current_time: Optional[int] = Field(alias=ATTR_CURRENT_TIME_UNIX)
    current_time_iso8601: str = Field(alias=ATTR_CURRENT_TIME_ISO8601)
    commissioning_mode: int = Field(alias=ATTR_COMMISSIONING_MODE)
    firmware_version: str = Field(alias=ATTR_FIRMWARE_VERSION)
    first_setup: Optional[int] = Field(alias=ATTR_FIRST_SETUP)
    homekit_id: str = Field(alias=ATTR_HOMEKIT_ID)
    id: str = Field(alias=ATTR_GATEWAY_ID)
    ntp_server: str = Field(alias=ATTR_NTP)
    ota_type: int = Field(alias=ATTR_OTA_TYPE)
    ota_update_state: int = Field(alias=ATTR_OTA_UPDATE_STATE)
    pair_status_alexa: int = Field(alias=ATTR_ALEXA_PAIR_STATUS)
    pair_status_google_home: int = Field(alias=ATTR_GOOGLE_HOME_PAIR_STATUS)
    time_source: int = Field(alias=ATTR_GATEWAY_TIME_SOURCE)
    update_progress: int = Field(alias=ATTR_GATEWAY_UPDATE_PROGRESS)


class Gateway:
    """This class connects to the IKEA Tradfri Gateway."""

    @classmethod
    def generate_psk(cls, identity: str) -> Command[str]:
        """Generate the PRE_SHARED_KEY from the gateway.

        Returns a Command.
        """

        def process_result(result: dict[str, str]) -> str:
            return result[ATTR_PSK]

        return Command(
            "post",
            [ROOT_GATEWAY, ATTR_AUTH],
            {ATTR_IDENTITY: identity},
            process_result=process_result,
        )

    @classmethod
    def get_endpoints(cls) -> Command[list[str]]:
        """
        Return all available endpoints on the gateway.

        The response from the gateway looks like this:
        <//15006>;ct=0;obs,
        <//15001>;ct=0;obs,
        <//15004>;ct=0;obs,
        <//15004/add>;ct=0,
        <//15004/remove>;ct=0,
        <//15010>;ct=0;obs,
        <//15005>;ct=0;obs,
        <//15011/15012>;ct=0;obs,
        <//15011/9034>;ct=0,
        <//15011/9030>;ct=0,
        <//15011/9031>;ct=0,
        <//15011/9094>;ct=0;obs,
        <//15011/9095>;ct=0;obs,
        <//15011/9104>;ct=0;obs,
        <//15004/131073>;ct=0;obs,
        <//15001/65536>;ct=0;obs,
        <//15005/131073/196608>;ct=0;obs,
        <//15011/9063>;ct=0

        Returns a Command.
        """

        def process_result(result: str) -> list[str]:
            return [line.split(";")[0][2:-1] for line in result.split(",")]

        return Command(
            "get",
            [".well-known", "core"],
            parse_json=False,
            process_result=process_result,
        )

    def get_devices(self) -> Command[list[Command[Device]]]:
        """
        Return the devices linked to the gateway.

        Returns a Command.
        """

        def process_result(result: list[str]) -> list[Command[Device]]:
            return [self.get_device(dev) for dev in result]

        return Command("get", [ROOT_DEVICES], process_result=process_result)

    @classmethod
    def get_device(cls, device_id: str) -> Command[Device]:
        """
        Return specified device.

        Returns a Command.
        """

        def process_result(result: TypeRaw) -> Device:
            return Device(result)

        return Command("get", [ROOT_DEVICES, device_id], process_result=process_result)

    def get_groups(self) -> Command[list[Command[Group]]]:
        """
        Return the groups linked to the gateway.

        Returns a Command.
        """

        def process_result(result: list[str]) -> list[Command[Group]]:
            return [self.get_group(group) for group in result]

        return Command("get", [ROOT_GROUPS], process_result=process_result)

    def get_group(self, group_id: str) -> Command[Group]:
        """
        Return specified group.

        Returns a Command.
        """

        def process_result(result: TypeRaw) -> Group:
            return Group(self, result)

        return Command("get", [ROOT_GROUPS, group_id], process_result=process_result)

    @classmethod
    def add_group_member(cls, values: dict[str, Any]) -> Command[None]:
        """Add a device to a group."""
        return Command("put", [ROOT_GROUPS, "add"], values)

    @classmethod
    def remove_group_member(cls, values: dict[str, Any]) -> Command[None]:
        """Remove a device from a group."""
        return Command("put", [ROOT_GROUPS, "remove"], values)

    @classmethod
    def get_gateway_info(cls) -> Command[GatewayInfo]:
        """
        Return the gateway info.

        Returns a Command.
        """

        def process_result(result: TypeRaw) -> GatewayInfo:
            return GatewayInfo(result)

        return Command(
            "get", [ROOT_GATEWAY, ATTR_GATEWAY_INFO], process_result=process_result
        )

    def get_moods(self, group_id: int) -> Command[list[Command[Mood]]]:
        """
        Return moods available in given group.

        Returns a Command.
        """

        def process_result(result: list[str]) -> list[Command[Mood]]:
            return [self.get_mood(mood, mood_parent=group_id) for mood in result]

        return Command(
            "get", [ROOT_MOODS, str(group_id)], process_result=process_result
        )

    @classmethod
    def get_mood(cls, mood_id: str, *, mood_parent: int) -> Command[Mood]:
        """
        Return a mood.

        Returns a Command.
        """

        def process_result(result: TypeRaw) -> Mood:
            return Mood(result, mood_parent)

        return Command(
            "get",
            [ROOT_MOODS, str(mood_parent), mood_id],
            mood_parent,
            process_result=process_result,
        )

    def get_smart_tasks(self) -> Command[list[Command[SmartTask]]]:
        """
        Return the transitions linked to the gateway.

        Returns a Command.
        """

        def process_result(result: list[str]) -> list[Command[SmartTask]]:
            return [self.get_smart_task(task) for task in result]

        return Command("get", [ROOT_SMART_TASKS], process_result=process_result)

    def get_smart_task(self, task_id: str) -> Command[SmartTask]:
        """
        Return specified transition.

        Returns a Command.
        """

        def process_result(result: TypeRaw) -> SmartTask:
            return SmartTask(self, result)

        return Command(
            "get", [ROOT_SMART_TASKS, task_id], process_result=process_result
        )

    @classmethod
    def reboot(cls) -> Command[None]:
        """Reboot the Gateway.

        Returns a Command.
        """
        return Command("post", [ROOT_GATEWAY, ATTR_GATEWAY_REBOOT])

    @classmethod
    def set_commissioning_timeout(cls, timeout: int) -> Command[None]:
        """Put the gateway in pairing state.

        The pairing state is when the gateway accepts pairings from
        switches, dimmers and motion sensors for up to timeout seconds.
        Returns a Command.
        """
        return Command(
            "put", [ROOT_GATEWAY, ATTR_GATEWAY_INFO], {ATTR_COMMISSIONING_MODE: timeout}
        )

    @classmethod
    def factory_reset(cls) -> Command[None]:
        """Reset Gateway to factory defaults.

        WARNING: All data in Gateway is lost (pairing, groups, etc)
        Returns a Command.
        """
        return Command("post", [ROOT_GATEWAY, ATTR_GATEWAY_FACTORY_DEFAULTS])


class GatewayInfo:
    """This class contains Gateway information."""

    raw: GatewayInfoResponse

    def __init__(self, raw: TypeRaw) -> None:
        """Create object of class."""
        self.raw = GatewayInfoResponse(**raw)

    @property
    def certificate_provisioned(self) -> int:
        """Return provisioning status of certificate."""
        return self.raw.certificate_provisioned

    @property
    def current_time(self) -> datetime | None:
        """Return current time (normal timestamp)."""
        if self.raw.current_time is not None:
            return datetime.utcfromtimestamp(self.raw.current_time)

        return None

    @property
    def commissioning_mode(self) -> int:
        """Return comissioning mode."""
        return self.raw.commissioning_mode

    @property
    def current_time_iso8601(self) -> str:
        """Return current time in iso8601 format."""
        return self.raw.current_time_iso8601

    @property
    def firmware_version(self) -> str:
        """Return gateway firmware version."""
        return self.raw.firmware_version

    @property
    def first_setup(self) -> datetime | None:
        """Return the time when gateway was first set up."""
        if self.raw.first_setup is not None:
            return datetime.utcfromtimestamp(self.raw.first_setup)

        return None

    @property
    def homekit_id(self) -> str:
        """Return homekit id."""
        return self.raw.homekit_id

    @property
    def id(self) -> str:
        """Return the gateway id."""
        return self.raw.id

    @property
    def ntp_server(self) -> str:
        """NTP server in use."""
        return self.raw.ntp_server

    @property
    def ota_type(self) -> int:
        """Return OTA type."""
        return self.raw.ota_type

    @property
    def ota_update_state(self) -> int:
        """Return OTA update state."""
        return self.raw.ota_update_state

    @property
    def pair_status_google_home(self) -> int:
        """Return pairing status Google Home."""
        return self.raw.pair_status_google_home

    @property
    def pair_status_alexa(self) -> int:
        """Return pairing status Amazon Alexa."""
        return self.raw.pair_status_alexa

    @property
    def path(self) -> list[str]:
        """Return path."""
        return [ROOT_GATEWAY, ATTR_GATEWAY_INFO]

    @property
    def time_source(self) -> int:
        """Return time source."""
        return self.raw.time_source

    @property
    def update_progress(self) -> int:
        """Return update status."""
        return self.raw.update_progress

    def set_values(self, values: dict[str, Any]) -> Command[None]:
        """Help set values for mood.

        Returns a Command.
        """
        return Command("put", self.path, values)

    def update(self) -> Command[None]:
        """
        Update the info.

        Returns a Command.
        """

        def process_result(result: TypeRaw) -> None:
            """Define callback to process result."""
            self.raw = GatewayInfoResponse(**result)

        return Command("get", self.path, process_result=process_result)

    def __repr__(self) -> str:
        """Return representation of class object."""
        return "<GatewayInfo>"
