"""Represent the gateway."""
from datetime import datetime

from .const import (
    ROOT_DEVICES, ROOT_GROUPS, ROOT_MOODS, ROOT_SMART_TASKS,
    PATH_GATEWAY_INFO, ATTR_NTP, ATTR_FIRMWARE_VERSION,
    ATTR_CURRENT_TIME_UNIX, ATTR_CURRENT_TIME_ISO8601,
    ATTR_FIRST_SETUP, ATTR_GATEWAY_ID)
from .device import Device
from .group import Group
from .mood import Mood
from .smart_task import SmartTask


class Gateway(object):
    """This class connects to the IKEA Tradfri Gateway."""

    def __init__(self, api):
        self.api = api

    def get_endpoints(self):
        """Return all available endpoints on the gateway."""
        data = self.api('get', ['.well-known', 'core'], parse_json=False)
        return [line.split(';')[0][2:-1] for line in data.split(',')]

    def get_devices(self):
        """Return the devices linked to the gateway."""
        devices = self.api('get', [ROOT_DEVICES])

        return [self.get_device(dev) for dev in devices]

    def get_device(self, device_id):
        """Return specified device."""
        return Device(self.api, self.api('get', [ROOT_DEVICES, device_id]))

    def get_groups(self):
        """Return the groups linked to the gateway."""
        groups = self.api('get', [ROOT_GROUPS])

        return [self.get_group(group) for group in groups]

    def get_group(self, group_id):
        """Return specified group."""
        return Group(self, self.api('get', [ROOT_GROUPS, group_id]))

    def get_gateway_info(self):
        """Return the gateway info."""
        return GatewayInfo(self.api, self.api('get', PATH_GATEWAY_INFO))

    def get_moods(self):
        """Return moods defined on the gateway."""
        mood_parent = self._get_mood_parent()

        return [self.get_mood(mood, mood_parent=mood_parent) for mood in
                self.api('get', [ROOT_MOODS, mood_parent])]

    def get_mood(self, mood_id, *, mood_parent=None):
        """Return a mood."""
        if mood_parent is None:
            mood_parent = self._get_mood_parent()

        return Mood(
            self.api, self.api('get', [ROOT_MOODS, mood_parent, mood_id]),
            mood_parent)

    def _get_mood_parent(self):
        """Get the parent of all moods."""
        return self.api('get', [ROOT_MOODS])[0]

    def get_smart_tasks(self):
        """Return the transitions linked to the gateway."""
        tasks = self.api('get', [ROOT_SMART_TASKS])

        return [self.get_smart_task(task) for task in tasks]

    def get_smart_task(self, task_id):
        """Return specified transition."""
        return SmartTask(self.api, self.api(
            'get', [ROOT_SMART_TASKS, task_id]))


class GatewayInfo:
    def __init__(self, api, raw):
        self.api = api
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
        """Helper to set values for mood."""
        self.api('put', self.path, values)

    def update(self):
        self.raw = self.api('get', self.path)

    def __repr__(self):
        return '<GatewayInfo>'
