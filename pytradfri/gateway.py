"""Represent the gateway."""
from datetime import datetime

from .command import Command
from .const import (
    ATTR_AUTH,
    ATTR_COMMISSIONING_MODE,
    ATTR_CURRENT_TIME_ISO8601,
    ATTR_CURRENT_TIME_UNIX,
    ATTR_FIRMWARE_VERSION,
    ATTR_FIRST_SETUP,
    ATTR_GATEWAY_FACTORY_DEFAULTS,
    ATTR_GATEWAY_ID,
    ATTR_GATEWAY_INFO,
    ATTR_GATEWAY_REBOOT,
    ATTR_HOMEKIT_ID,
    ATTR_IDENTITY,
    ATTR_NTP,
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
from .smart_task import SmartTask


class Gateway:
    """This class connects to the IKEA Tradfri Gateway."""

    @classmethod
    def generate_psk(cls, identity):
        """Generate the PRE_SHARED_KEY from the gateway.

        Returns a Command.
        """

        def process_result(result):
            return result[ATTR_PSK]

        return Command(
            "post",
            [ROOT_GATEWAY, ATTR_AUTH],
            {ATTR_IDENTITY: identity},
            process_result=process_result,
        )

    @classmethod
    def get_endpoints(cls):
        """
        Return all available endpoints on the gateway.

        Returns a Command.
        """

        def process_result(result):
            return [line.split(";")[0][2:-1] for line in result.split(",")]

        return Command(
            "get",
            [".well-known", "core"],
            parse_json=False,
            process_result=process_result,
        )

    def get_devices(self):
        """
        Return the devices linked to the gateway.

        Returns a Command.
        """

        def process_result(result):
            return [self.get_device(dev) for dev in result]

        return Command("get", [ROOT_DEVICES], process_result=process_result)

    @classmethod
    def get_device(cls, device_id):
        """
        Return specified device.

        Returns a Command.
        """

        def process_result(result):
            return Device(result)

        return Command("get", [ROOT_DEVICES, device_id], process_result=process_result)

    def get_groups(self):
        """
        Return the groups linked to the gateway.

        Returns a Command.
        """

        def process_result(result):
            return [self.get_group(group) for group in result]

        return Command("get", [ROOT_GROUPS], process_result=process_result)

    def get_group(self, group_id):
        """
        Return specified group.

        Returns a Command.
        """

        def process_result(result):
            return Group(self, result)

        return Command("get", [ROOT_GROUPS, group_id], process_result=process_result)

    @classmethod
    def add_group_member(cls, values):
        """Add a device to a group."""

        return Command("put", [ROOT_GROUPS, "add"], values)

    @classmethod
    def remove_group_member(cls, values):
        """Remove a device from a group."""

        return Command("put", [ROOT_GROUPS, "remove"], values)

    @classmethod
    def get_gateway_info(cls):
        """
        Return the gateway info.

        Returns a Command.
        """

        def process_result(result):
            return GatewayInfo(result)

        return Command(
            "get", [ROOT_GATEWAY, ATTR_GATEWAY_INFO], process_result=process_result
        )

    def get_moods(self, group_id):
        """
        Return moods available in given group.

        Returns a Command.
        """

        def process_result(result):
            return [self.get_mood(mood, mood_parent=group_id) for mood in result]

        return Command("get", [ROOT_MOODS, group_id], process_result=process_result)

    @classmethod
    def get_mood(cls, mood_id, *, mood_parent=None):
        """
        Return a mood.

        Returns a Command.
        """

        def process_result(result):
            return Mood(result, mood_parent)

        return Command(
            "get",
            [ROOT_MOODS, mood_parent, mood_id],
            mood_parent,
            process_result=process_result,
        )

    def get_smart_tasks(self):
        """
        Return the transitions linked to the gateway.

        Returns a Command.
        """

        def process_result(result):
            return [self.get_smart_task(task) for task in result]

        return Command("get", [ROOT_SMART_TASKS], process_result=process_result)

    def get_smart_task(self, task_id):
        """
        Return specified transition.

        Returns a Command.
        """

        def process_result(result):
            return SmartTask(self, result)

        return Command(
            "get", [ROOT_SMART_TASKS, task_id], process_result=process_result
        )

    @classmethod
    def reboot(cls):
        """Reboot the Gateway.

        Returns a Command.
        """

        return Command("post", [ROOT_GATEWAY, ATTR_GATEWAY_REBOOT])

    @classmethod
    def set_commissioning_timeout(cls, timeout):
        """Put the gateway in pairing state.

        The pairing state is when the gateway accepts pairings from
        switches, dimmers and motion sensors for up to timeout seconds.
        Returns a Command.
        """

        return Command(
            "put", [ROOT_GATEWAY, ATTR_GATEWAY_INFO], {ATTR_COMMISSIONING_MODE: timeout}
        )

    @classmethod
    def factory_reset(cls):
        """Reset Gateway to factory defaults.

        WARNING: All data in Gateway is lost (pairing, groups, etc)
        Returns a Command.
        """

        return Command("post", [ROOT_GATEWAY, ATTR_GATEWAY_FACTORY_DEFAULTS])


class GatewayInfo:
    """This class contains Gateway information."""

    def __init__(self, raw):
        """Create object of class."""
        self.raw = raw

    @property
    def id(self):
        """Return the gateway id."""
        return self.raw.get(ATTR_GATEWAY_ID)

    @property
    def ntp_server(self):
        """NTP server in use."""
        return self.raw.get(ATTR_NTP)

    @property
    def firmware_version(self):
        """NTP server in use."""
        return self.raw.get(ATTR_FIRMWARE_VERSION)

    @property
    def current_time(self):
        """Return current time (normal timestamp)."""
        if ATTR_CURRENT_TIME_UNIX not in self.raw:
            return None
        return datetime.utcfromtimestamp(self.raw[ATTR_CURRENT_TIME_UNIX])

    @property
    def current_time_iso8601(self):
        """Return current time in iso8601 format."""
        return self.raw.get(ATTR_CURRENT_TIME_ISO8601)

    @property
    def first_setup(self):
        """Return the time when gateway was first set up."""
        if ATTR_FIRST_SETUP not in self.raw:
            return None
        return datetime.utcfromtimestamp(self.raw[ATTR_FIRST_SETUP])

    @property
    def homekit_id(self):
        """Return homekit id."""
        return self.raw.get(ATTR_HOMEKIT_ID)

    @property
    def path(self):
        """Return path."""
        return [ROOT_GATEWAY, ATTR_GATEWAY_INFO]

    def set_values(self, values):
        """Help set values for mood.

        Returns a Command.
        """
        return Command("put", self.path, values)

    def update(self):
        """
        Update the info.

        Returns a Command.
        """

        def process_result(result):
            """Define callback to process result."""
            self.raw = result

        return Command("get", self.path, process_result=process_result)

    def __repr__(self):
        """Return representation of class object."""
        return "<GatewayInfo>"
