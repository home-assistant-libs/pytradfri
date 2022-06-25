"""Group handling."""
from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from pydantic import Field

from .color import COLORS
from .command import Command
from .const import (
    ATTR_DEVICE_STATE,
    ATTR_GROUP_ID,
    ATTR_GROUP_MEMBERS,
    ATTR_HS_LINK,
    ATTR_ID,
    ATTR_LIGHT_COLOR_HEX,
    ATTR_LIGHT_COLOR_HUE,
    ATTR_LIGHT_COLOR_SATURATION,
    ATTR_LIGHT_COLOR_X,
    ATTR_LIGHT_COLOR_Y,
    ATTR_LIGHT_DIMMER,
    ATTR_LIGHT_MIREDS,
    ATTR_MOOD,
    ATTR_TRANSITION_TIME,
    RANGE_BRIGHTNESS,
    RANGE_HUE,
    RANGE_MIREDS,
    RANGE_SATURATION,
    RANGE_X,
    RANGE_Y,
    ROOT_GROUPS,
)
from .device import Device
from .error import ColorError
from .mood import Mood
from .resource import ApiResource, ApiResourceResponse, TypeRaw

if TYPE_CHECKING:
    from .gateway import Gateway


class GroupResponse(ApiResourceResponse):
    """Represent API response for a blind."""

    color_hex: Optional[str] = Field(alias=ATTR_LIGHT_COLOR_HEX)
    dimmer: int = Field(alias=ATTR_LIGHT_DIMMER)
    group_members: dict[str, dict[str, list[int]]] = Field(alias=ATTR_GROUP_MEMBERS)
    mood_id: str = Field(alias=ATTR_MOOD)
    state: int = Field(alias=ATTR_DEVICE_STATE)


class Group(ApiResource):
    """Represent a group."""

    _model_class: type[GroupResponse] = GroupResponse
    raw: GroupResponse

    def __init__(self, gateway: Gateway, raw: TypeRaw) -> None:
        """Create object of class."""
        super().__init__(raw)
        self._gateway = gateway

    @property
    def path(self) -> list[str]:
        """Path."""
        return [ROOT_GROUPS, str(self.id)]

    @property
    def state(self) -> bool:
        """Boolean representing the light state of the group."""
        return self.raw.state == 1

    @property
    def dimmer(self) -> int:
        """Dimmer value of the group."""
        return self.raw.dimmer

    @property
    def hex_color(self) -> str | None:
        """Return hex color."""
        if self.raw.color_hex:
            return self.raw.color_hex

        return None

    @property
    def member_ids(self) -> list[int]:
        """
        Members of this group.

        A group with devices will look like this:
        {"15002": {"9003": [65536, 65537]}}

        An empty group will look like this:
        {"15002": {"9003": []}}

        If a group is created in the app and no devices are added
        to it, it will immediately be deleted.
        """
        return self.raw.group_members[ATTR_HS_LINK][ATTR_ID]

    @property
    def mood_id(self) -> str:
        """Active mood."""
        return self.raw.mood_id

    def members(self) -> list[Command[Device]]:
        """Return device objects of members of this group."""
        return [self._gateway.get_device(str(dev)) for dev in self.member_ids]

    def add_member(self, memberid: str) -> Command[None]:
        """Add a member to this group."""
        return self._gateway.add_group_member(
            {ATTR_GROUP_ID: self.id, ATTR_ID: [memberid]}
        )

    def remove_member(self, memberid: str) -> Command[None]:
        """Remove a member from this group."""
        return self._gateway.remove_group_member(
            {ATTR_GROUP_ID: self.id, ATTR_ID: [memberid]}
        )

    def moods(self) -> Command[list[Command[Mood]]]:
        """Return mood objects of moods in this group."""
        return self._gateway.get_moods(self.id)

    def mood(self) -> Command[Mood]:
        """Active mood."""
        return self._gateway.get_mood(self.mood_id, mood_parent=self.id)

    def activate_mood(self, mood_id: str) -> Command[None]:
        """Activate a mood."""
        return self.set_values({ATTR_MOOD: mood_id, ATTR_DEVICE_STATE: int(self.state)})

    def set_state(self, state: bool) -> Command[None]:
        """Set state of a group."""
        return self.set_values({ATTR_DEVICE_STATE: int(state)})

    def set_dimmer(
        self, dimmer: int, transition_time: int | None = None
    ) -> Command[None]:
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

    def set_color_temp(
        self, color_temp: int, *, index: int = 0, transition_time: int | None = None
    ) -> Command[None]:
        """Set color temp a light."""
        self._value_validate(color_temp, RANGE_MIREDS, "Color temperature")

        values = {ATTR_LIGHT_MIREDS: color_temp}

        if transition_time is not None:
            values[ATTR_TRANSITION_TIME] = transition_time

        return self.set_values(values)

    def set_hex_color(
        self, color: str, transition_time: int | None = None
    ) -> Command[None]:
        """Set hex color of a group."""
        values: dict[str, int | str] = {
            ATTR_LIGHT_COLOR_HEX: color,
        }
        if transition_time is not None:
            values[ATTR_TRANSITION_TIME] = transition_time
        return self.set_values(values)

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

        values = {ATTR_LIGHT_COLOR_SATURATION: saturation, ATTR_LIGHT_COLOR_HUE: hue}

        if brightness is not None:
            values[ATTR_LIGHT_DIMMER] = brightness
            self._value_validate(brightness, RANGE_BRIGHTNESS, "Brightness")

        if transition_time is not None:
            values[ATTR_TRANSITION_TIME] = transition_time

        return self.set_values(values)

    def set_xy_color(
        self, color_x: int, color_y: int, transition_time: int | None = None
    ) -> Command[None]:
        """Set xy color of a group."""
        self._value_validate(color_x, RANGE_X, "X color")
        self._value_validate(color_y, RANGE_Y, "Y color")

        values = {ATTR_LIGHT_COLOR_X: color_x, ATTR_LIGHT_COLOR_Y: color_y}

        if transition_time is not None:
            values[ATTR_TRANSITION_TIME] = transition_time

        return self.set_values(values)

    def set_predefined_color(
        self, colorname: str, transition_time: int | None = None
    ) -> Command[None]:
        """Set predefined color for group."""
        try:
            color = COLORS[colorname.lower().replace(" ", "_")]
            return self.set_hex_color(color, transition_time=transition_time)
        except KeyError as exc:
            raise ColorError(f"Invalid color specified: {colorname}") from exc

    def _value_validate(
        self, value: int, rnge: tuple[int, int], identifier: str = "Given"
    ) -> None:
        """Make sure a value is within a given range."""
        if value is not None and (value < rnge[0] or value > rnge[1]):
            raise ValueError(
                f"{identifier} value must be between {rnge[0]} and {rnge[1]}."
            )

    def __repr__(self) -> str:
        """Return representation of class object."""
        state = "on" if self.state else "off"
        return f"<Group {self.name} - {state}>"
