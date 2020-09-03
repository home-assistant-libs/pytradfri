"""Class to control the lights."""
from pytradfri.color import COLORS
from pytradfri.command import Command
from pytradfri.const import (
    ATTR_LIGHT_DIMMER,
    ATTR_LIGHT_MIREDS,
    ATTR_LIGHT_COLOR_X,
    ATTR_LIGHT_COLOR_HUE,
    RANGE_MIREDS,
    RANGE_HUE,
    RANGE_SATURATION,
    ATTR_LIGHT_CONTROL,
    ATTR_DEVICE_STATE,
    RANGE_BRIGHTNESS,
    ATTR_TRANSITION_TIME,
    ATTR_LIGHT_COLOR_HEX,
    RANGE_X,
    RANGE_Y,
    ATTR_LIGHT_COLOR_Y,
    ATTR_LIGHT_COLOR_SATURATION,
)
from pytradfri.device.light import Light
from pytradfri.error import ColorError


class LightControl:
    """Class to control the lights."""

    def __init__(self, device):
        self._device = device

        self.can_set_dimmer = None
        self.can_set_temp = None
        self.can_set_xy = None
        self.can_set_color = None
        self.can_combine_commands = None

        if ATTR_LIGHT_DIMMER in self.raw[0]:
            self.can_set_dimmer = True

        if ATTR_LIGHT_MIREDS in self.raw[0]:
            self.can_set_temp = True

        if ATTR_LIGHT_COLOR_X in self.raw[0]:
            self.can_set_xy = True

        if ATTR_LIGHT_COLOR_HUE in self.raw[0]:
            self.can_set_color = True

        # Currently uncertain which bulbs are capable of setting
        # multiple values simultaneously. As of gateway firmware
        # 1.3.14 1st party bulbs do not seem to support this properly,
        # but (at least some) hue bulbs do.
        if "Philips" in self._device.device_info.manufacturer:
            self.can_combine_commands = True

        self.min_mireds = RANGE_MIREDS[0]
        self.max_mireds = RANGE_MIREDS[1]

        self.min_hue = RANGE_HUE[0]
        self.max_hue = RANGE_HUE[1]

        self.min_saturation = RANGE_SATURATION[0]
        self.max_saturation = RANGE_SATURATION[1]

    @property
    def raw(self):
        """Return raw data that it represents."""
        return self._device.raw[ATTR_LIGHT_CONTROL]

    @property
    def lights(self):
        """Return light objects of the light control."""
        return [Light(self._device, i) for i in range(len(self.raw))]

    def set_state(self, state, *, index=0):
        """Set state of a light."""
        return self.set_values({ATTR_DEVICE_STATE: int(state)}, index=index)

    def set_dimmer(self, dimmer, *, index=0, transition_time=None):
        """Set dimmer value of a light.
        transition_time: Integer representing tenth of a second (default None)
        """
        self._value_validate(dimmer, RANGE_BRIGHTNESS, "Dimmer")

        values = {ATTR_LIGHT_DIMMER: dimmer}

        if transition_time is not None:
            values[ATTR_TRANSITION_TIME] = transition_time

        return self.set_values(values, index=index)

    def set_color_temp(self, color_temp, *, index=0, transition_time=None):
        """Set color temp a light."""
        self._value_validate(color_temp, RANGE_MIREDS, "Color temperature")

        values = {ATTR_LIGHT_MIREDS: color_temp}

        if transition_time is not None:
            values[ATTR_TRANSITION_TIME] = transition_time

        return self.set_values(values, index=index)

    def set_hex_color(self, color, *, index=0, transition_time=None):
        """Set hex color of the light."""
        values = {
            ATTR_LIGHT_COLOR_HEX: color,
        }

        if transition_time is not None:
            values[ATTR_TRANSITION_TIME] = transition_time

        return self.set_values(values, index=index)

    def set_xy_color(self, color_x, color_y, *, index=0, transition_time=None):
        """Set xy color of the light."""
        self._value_validate(color_x, RANGE_X, "X color")
        self._value_validate(color_y, RANGE_Y, "Y color")

        values = {ATTR_LIGHT_COLOR_X: color_x, ATTR_LIGHT_COLOR_Y: color_y}

        if transition_time is not None:
            values[ATTR_TRANSITION_TIME] = transition_time

        return self.set_values(values, index=index)

    def set_hsb(
        self, hue, saturation, brightness=None, *, index=0, transition_time=None
    ):
        """Set HSB color settings of the light."""
        self._value_validate(hue, RANGE_HUE, "Hue")
        self._value_validate(saturation, RANGE_SATURATION, "Saturation")

        values = {ATTR_LIGHT_COLOR_SATURATION: saturation, ATTR_LIGHT_COLOR_HUE: hue}

        if brightness is not None:
            values[ATTR_LIGHT_DIMMER] = brightness
            self._value_validate(brightness, RANGE_BRIGHTNESS, "Brightness")

        if transition_time is not None:
            values[ATTR_TRANSITION_TIME] = transition_time

        return self.set_values(values, index=index)

    def set_predefined_color(self, colorname, *, index=0, transition_time=None):
        try:
            color = COLORS[colorname.lower().replace(" ", "_")]
            return self.set_hex_color(
                color, index=index, transition_time=transition_time
            )
        except KeyError:
            raise ColorError("Invalid color specified: %s", colorname)

    def _value_validate(self, value, rnge, identifier="Given"):
        """
        Make sure a value is within a given range
        """
        if value is not None and (value < rnge[0] or value > rnge[1]):
            raise ValueError(
                "%s value must be between %d and %d." % (identifier, rnge[0], rnge[1])
            )

    def set_values(self, values, *, index=0):
        """
        Set values on light control.
        Returns a Command.
        """
        assert len(self.raw) == 1, "Only devices with 1 light supported"

        return Command("put", self._device.path, {ATTR_LIGHT_CONTROL: [values]})

    def __repr__(self):
        return "<LightControl for {} ({} lights)>".format(
            self._device.name, len(self.raw)
        )
