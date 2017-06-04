"""Represent the gateway."""
from datetime import datetime

from .command import Command
from .const import (
    ROOT_DEVICES, ROOT_GROUPS, ROOT_MOODS, ROOT_SMART_TASKS,
    PATH_GATEWAY_INFO, ATTR_NTP, ATTR_FIRMWARE_VERSION,
    ATTR_CURRENT_TIME_UNIX, ATTR_CURRENT_TIME_ISO8601,
    ATTR_FIRST_SETUP, ATTR_GATEWAY_ID)
from .device import Device
from .group import Group
from .mood import Mood
from .smart_task import SmartTask


class Gateway:
    """This class connects to the IKEA Tradfri Gateway."""

    def get_endpoints(self):
        """
        Return all available endpoints on the gateway.

        Returns a Command.
        """
        def process_result(result):
            return [line.split(';')[0][2:-1] for line in result.split(',')]

        return Command('get', ['.well-known', 'core'], parse_json=False,
                       process_result=process_result)

    def get_devices(self):
        """
        Return the devices linked to the gateway.

        Returns a Command.
        """
        def process_result(result):
            return [self.get_device(dev) for dev in result]

        return Command('get', [ROOT_DEVICES], process_result=process_result)

    def get_device(self, device_id):
        """
        Return specified device.

        Returns a Command.
        """
        def process_result(result):
            return Device(result)

        return Command('get', [ROOT_DEVICES, device_id],
                       process_result=process_result)

    def get_groups(self):
        """
        Return the groups linked to the gateway.

        Returns a Command.
        """
        def process_result(result):
            return [self.get_group(group) for group in result]

        return Command('get', [ROOT_GROUPS], process_result=process_result)

    def get_group(self, group_id):
        """
        Return specified group.

        Returns a Command.
        """
        def process_result(result):
            return Group(self, result)

        return Command('get', [ROOT_GROUPS, group_id],
                       process_result=process_result)

    def get_gateway_info(self):
        """
        Return the gateway info.

        Returns a Command.
        """
        def process_result(result):
            return GatewayInfo(result)

        return Command('get', PATH_GATEWAY_INFO, process_result=process_result)

    def get_moods(self):
        """
        Return moods defined on the gateway.

        Returns a Command.
        """
        mood_parent = self._get_mood_parent()

        def process_result(result):
            return [self.get_mood(mood, mood_parent=mood_parent) for mood in
                    result]

        return Command('get', [ROOT_MOODS, mood_parent],
                       process_result=process_result)

    def get_mood(self, mood_id, *, mood_parent=None):
        """
        Return a mood.

        Returns a Command.
        """
        if mood_parent is None:
            mood_parent = self._get_mood_parent()

        def process_result(result):
            return Mood(result, mood_parent)

        return Command('get', [ROOT_MOODS, mood_parent, mood_id],
                       mood_parent, process_result=process_result)

    def _get_mood_parent(self):
        """
        Get the parent of all moods.

        Returns a Command.
        """
        def process_result(result):
            return result[0]

        return Command('get', [ROOT_MOODS], process_result=process_result)

    def get_smart_tasks(self):
        """
        Return the transitions linked to the gateway.

        Returns a Command.
        """
        def process_result(result):
            return [self.get_smart_task(task) for task in result]

        return Command('get', [ROOT_SMART_TASKS],
                       process_result=process_result)

    def get_smart_task(self, task_id):
        """
        Return specified transition.

        Returns a Command.
        """
        def process_result(result):
            return SmartTask(self, result)

        return Command('get', [ROOT_SMART_TASKS, task_id],
                       process_result=process_result)


class GatewayInfo:
    """This class contains Gateway information."""

    def __init__(self, raw):
        self.raw = raw

    @property
    def id(self):
        """This looks like a value representing an id."""
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
        if ATTR_CURRENT_TIME_UNIX not in self.raw:
            return None
        return datetime.utcfromtimestamp(self.raw[ATTR_CURRENT_TIME_UNIX])

    @property
    def current_time_iso8601(self):
        return self.raw.get(ATTR_CURRENT_TIME_ISO8601)

    @property
    def first_setup(self):
        """This is a guess of the meaning of this value."""
        if ATTR_FIRST_SETUP not in self.raw:
            return None
        return datetime.utcfromtimestamp(self.raw[ATTR_FIRST_SETUP])

    @property
    def path(self):
        return PATH_GATEWAY_INFO

    def set_values(self, values):
        """
        Helper to set values for mood.

        Returns a Command.
        """
        return Command('put', self.path, values)

    def update(self):
        """
        Update the info.

        Returns a Command.
        """
        def process_result(result):
            self.raw = result

        return Command('get', self.path, process_result=process_result)

    def __repr__(self):
        return '<GatewayInfo>'
