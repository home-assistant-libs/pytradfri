from datetime import datetime

from .const import (
    ROOT_GROUPS,
    ATTR_LIGHT_STATE,
    ATTR_LIGHT_DIMMER,
    ATTR_NAME,
    ATTR_CREATED_AT,
    ATTR_ID,
)

ROOT_DEVICES2 = "15002"  # ??
ATTR_MEMBERS = "9018"
ATTR_MOOD = "9039"


class Group:
    """Represent a group."""
    def __init__(self, gateway, raw):
        self._gateway = gateway
        self.api = gateway.api
        self.raw = raw

    @property
    def id(self):
        return self.raw.get(ATTR_ID)

    @property
    def name(self):
        return self.raw.get(ATTR_NAME)

    @property
    def created_at(self):
        if ATTR_CREATED_AT not in self.raw:
            return None
        return datetime.utcfromtimestamp(self.raw[ATTR_CREATED_AT])

    @property
    def path(self):
        return [ROOT_GROUPS, self.id]

    @property
    def state(self):
        """Boolean representing the light state of the group."""
        return self.raw.get(ATTR_LIGHT_STATE) == 1

    @property
    def dimmer(self):
        """Dimmer value of the group."""
        return self.raw.get(ATTR_LIGHT_DIMMER)

    @property
    def member_ids(self):
        """Members of this group."""
        info = self.raw.get(ATTR_MEMBERS, {})

        if not info or ROOT_DEVICES2 not in info:
            return []

        return info[ROOT_DEVICES2].get(ATTR_ID, [])

    @property
    def mood_id(self):
        """Active mood."""
        return self.raw.get(ATTR_MOOD)

    def members(self):
        """Return device objects of members of this group."""
        return [self._gateway.get_device(dev) for dev in self.member_ids]

    def mood(self):
        """"Active mood."""
        return self._gateway.get_mood(self.mood_id)

    def activate_mood(self, mood_id):
        """Activate a mood."""
        self.set_values({
            ATTR_MOOD: mood_id
        })

    def set_name(self, name):
        """Set group name."""
        self.set_values({
            ATTR_NAME: name
        })

    def set_values(self, values):
        """Helper to set values for group."""
        self.api('put', self.path, values)

    def update(self):
        """Update the group."""
        self.raw = self.api('get', self.path)

    def __repr__(self):
        state = 'on' if self.state else 'off'
        return '<Group {} - {}>'.format(self.name, state)
