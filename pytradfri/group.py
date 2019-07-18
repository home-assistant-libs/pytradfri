from .const import (
    ROOT_GROUPS,
    ATTR_DEVICE_STATE,
    ATTR_LIGHT_DIMMER,
    ATTR_LIGHT_COLOR_X,
    ATTR_LIGHT_COLOR_Y,
    ATTR_LIGHT_COLOR_HEX,
    ATTR_ID,
    ATTR_TRANSITION_TIME,
    RANGE_X,
    RANGE_Y
)
from .color import COLORS
from .resource import ApiResource
from .error import ColorError

ROOT_DEVICES2 = "15002"  # ??
ATTR_MEMBERS = "9018"
ATTR_MOOD = "9039"


class Group(ApiResource):
    """Represent a group."""
    def __init__(self, gateway, raw):
        super().__init__(raw)
        self._gateway = gateway

    @property
    def path(self):
        return [ROOT_GROUPS, self.id]

    @property
    def state(self):
        """Boolean representing the light state of the group."""
        return self.raw.get(ATTR_DEVICE_STATE) == 1

    @property
    def dimmer(self):
        """Dimmer value of the group."""
        return self.raw.get(ATTR_LIGHT_DIMMER)

    @property
    def hex_color(self):
        return self.raw.get(ATTR_LIGHT_COLOR_HEX)

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
        return self.set_values({
            ATTR_MOOD: mood_id
        })

    def set_state(self, state):
        """Set state of a group."""
        return self.set_values({
            ATTR_DEVICE_STATE: int(state)
        })

    def set_dimmer(self, dimmer, transition_time=None):
        """Set dimmer value of a group.

        dimmer: Integer between 0..255
        transition_time: Integer representing tenth of a second (default None)
        """
        values = {
            ATTR_LIGHT_DIMMER: dimmer,
        }
        if transition_time is not None:
            values[ATTR_TRANSITION_TIME] = transition_time
        return self.set_values(values)

    def set_hex_color(self, color, transition_time=None):
        """Set hex color of a group."""
        values = {
            ATTR_LIGHT_COLOR_HEX: color,
        }
        if transition_time is not None:
            values[ATTR_TRANSITION_TIME] = transition_time
        return self.set_values(values)

    def set_xy_color(self, color_x, color_y, transition_time=None):
        """Set xy color of a group."""
        self._value_validate(color_x, RANGE_X, "X color")
        self._value_validate(color_y, RANGE_Y, "Y color")

        values = {
            ATTR_LIGHT_COLOR_X: color_x,
            ATTR_LIGHT_COLOR_Y: color_y
        }

        if transition_time is not None:
            values[ATTR_TRANSITION_TIME] = transition_time

        return self.set_values(values)

    def set_predefined_color(self, colorname, transition_time=None):
        try:
            color = COLORS[colorname.lower().replace(" ", "_")]
            return self.set_hex_color(color, transition_time=transition_time)
        except KeyError:
            raise ColorError('Invalid color specified: %s',
                             colorname)

    def _value_validate(self, value, rnge, identifier="Given"):
        """
        Make sure a value is within a given range
        """
        if value is not None and (value < rnge[0] or value > rnge[1]):
            raise ValueError('%s value must be between %d and %d.'
                             % (identifier, rnge[0], rnge[1]))

    def __repr__(self):
        state = 'on' if self.state else 'off'
        return '<Group {} - {}>'.format(self.name, state)
