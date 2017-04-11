"""Represent the gateway."""
from .const import (
    ROOT_DEVICES, ROOT_GROUPS, ROOT_MOODS, PATH_NTP)
from .device import Device
from .group import Group
from .mood import Mood


class Gateway(object):
    """This class connects to the IKEA Tradfri Gateway"""

    def __init__(self, api):
        self.api = api

    def get_endpoints(self):
        """Return all available endpoints on the gateway."""
        data = self.api('get', ['.well-known', 'core'], parse_json=False)
        return [line.split(';')[0][2:-1] for line in data.split(',')]

    def get_devices(self):
        """Returns the devices linked to the gateway"""
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

    def get_ntp(self):
        """Return the ntp server in use by the gateway."""
        return self.api('get', PATH_NTP)

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
