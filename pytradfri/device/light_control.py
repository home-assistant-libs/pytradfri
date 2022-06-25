"""Class to control the lights."""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from copy import deepcopy
from typing import TYPE_CHECKING, Union, cast

from ..color import COLORS
from ..command import Command
from ..const import (
    ATTR_DEVICE_STATE,
    ATTR_LIGHT_COLOR_HEX,
    ATTR_LIGHT_COLOR_HUE,
    ATTR_LIGHT_COLOR_SATURATION,
    ATTR_LIGHT_COLOR_X,
    ATTR_LIGHT_COLOR_Y,
    ATTR_LIGHT_CONTROL,
    ATTR_LIGHT_DIMMER,
    ATTR_LIGHT_MIREDS,
    ATTR_TRANSITION_TIME,
    RANGE_BRIGHTNESS,
    RANGE_HUE,
    RANGE_MIREDS,
    RANGE_SATURATION,
    RANGE_X,
    RANGE_Y,
)
from ..error import ColorError
from .base_controller import BaseController
from .light import Light, LightResponse

if TYPE_CHECKING:
    # avoid cyclic import at runtime.
    from . import Device


class LightControl(BaseController):
    """Class to control the lights."""

    def __init__(self, device: Device) -> None:
        """Create object of class."""
        super().__init__(device)

        self.can_combine_commands: bool = False

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
    def raw(self) -> list[LightResponse]:
        """Return raw data that it represents."""
        light_control_response = self._device.raw.light_control
        assert light_control_response is not None
        return light_control_response

    @property
    def lights(self) -> list[Light]:
        """Return light objects of the light control."""
        return [Light(self._device, i) for i in range(len(self.raw))]

    def set_state(self, state: bool, *, index: int = 0) -> Command[None]:
        """Set state of a light."""
        return self.set_values({ATTR_DEVICE_STATE: int(state)}, index=index)

    def set_dimmer(
        self, dimmer: int, *, index: int = 0, transition_time: int | None = None
    ) -> Command[None]:
        """Set dimmer value of a light.

        transition_time: Integer representing tenth of a second (default None)
        """
        self._value_validate(dimmer, RANGE_BRIGHTNESS, "Dimmer")

        values = {ATTR_LIGHT_DIMMER: dimmer}

        if transition_time is not None:
            values[ATTR_TRANSITION_TIME] = transition_time

        return self.set_values(values, index=index)

    def set_color_temp(
        self, color_temp: int, *, index: int = 0, transition_time: int | None = None
    ) -> Command[None]:
        """Set color temp a light."""
        self._value_validate(color_temp, RANGE_MIREDS, "Color temperature")

        values = {ATTR_LIGHT_MIREDS: color_temp}

        if transition_time is not None:
            values[ATTR_TRANSITION_TIME] = transition_time

        return self.set_values(values, index=index)

    def set_hex_color(
        self, color: str, *, index: int = 0, transition_time: int | None = None
    ) -> Command[None]:
        """Set hex color of the light."""
        values: dict[str, str | int] = {
            ATTR_LIGHT_COLOR_HEX: color,
        }

        if transition_time is not None:
            values[ATTR_TRANSITION_TIME] = transition_time

        return self.set_values(values, index=index)

    def set_xy_color(
        self,
        color_x: int,
        color_y: int,
        *,
        index: int = 0,
        transition_time: int | None = None,
    ) -> Command[None]:
        """Set xy color of the light."""
        self._value_validate(color_x, RANGE_X, "X color")
        self._value_validate(color_y, RANGE_Y, "Y color")

        values = {
            ATTR_LIGHT_COLOR_X: color_x,
            ATTR_LIGHT_COLOR_Y: color_y,
        }

        if transition_time is not None:
            values[ATTR_TRANSITION_TIME] = transition_time

        return self.set_values(values, index=index)

    def set_hsb(
        self,
        hue: int,
        saturation: int,
        brightness: int | None = None,
        *,
        index: int = 0,
        transition_time: int | None = None,
    ) -> Command[None]:
        """Set HSB color settings of the light."""
        self._value_validate(hue, RANGE_HUE, "Hue")
        self._value_validate(saturation, RANGE_SATURATION, "Saturation")

        values = {
            ATTR_LIGHT_COLOR_SATURATION: saturation,
            ATTR_LIGHT_COLOR_HUE: hue,
        }

        if brightness is not None:
            values[ATTR_LIGHT_DIMMER] = brightness
            self._value_validate(brightness, RANGE_BRIGHTNESS, "Brightness")

        if transition_time is not None:
            values[ATTR_TRANSITION_TIME] = transition_time

        return self.set_values(values, index=index)

    def set_predefined_color(
        self, colorname: str, *, index: int = 0, transition_time: int | None = None
    ) -> Command[None]:
        """Set predefined color."""
        try:
            color = COLORS[colorname.lower().replace(" ", "_")]
            return self.set_hex_color(
                color, index=index, transition_time=transition_time
            )
        except KeyError:
            raise ColorError(f"Invalid color specified: {colorname}") from KeyError

    def set_values(
        self, values: Mapping[str, str | int], *, index: int = 0
    ) -> Command[None]:
        """Set values on light control.

        Returns a Command.
        """
        assert len(self.raw) == 1, "Only devices with 1 light supported"

        return Command("put", self._device.path, {ATTR_LIGHT_CONTROL: [values]})

    def combine_commands(self, commands: Sequence[Command[None]]) -> Command[None]:
        """Combine a sequence of light control commands."""
        combined_data: dict[str, str | int] = {}

        for command in commands:
            data = command.data
            if data is None or ATTR_LIGHT_CONTROL not in data:
                raise TypeError(f"Invalid command data: {data}")

            light_control_data = cast(
                list[Mapping[str, Union[str, int]]], data[ATTR_LIGHT_CONTROL]
            )
            for control_data in light_control_data:
                combined_data.update(control_data)

        new_command = deepcopy(commands[0])
        assert new_command.data is not None  # Ensured by raising an error above.
        new_command.data[ATTR_LIGHT_CONTROL] = [combined_data]

        return new_command
