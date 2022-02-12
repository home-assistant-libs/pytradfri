"""Represent a blind."""
from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict, cast

from ..const import ATTR_BLIND_CURRENT_POSITION, ATTR_START_BLINDS
from ..resource import TypeRawList

if TYPE_CHECKING:
    # avoid cyclic import at runtime.
    from . import Device


TypeBlind = TypedDict(
    # Alternative syntax required due to the need of using strings as keys:
    # https://www.python.org/dev/peps/pep-0589/#alternative-syntax
    "TypeBlind",
    {
        "5536": int,  # Current blind position
        "9003": int,  # ID
    },
)


class Blind:
    """Represent a blind."""

    def __init__(self, device: Device, index: int) -> None:
        """Create object of class."""
        self.device = device
        self.index = index

    @property
    def raw(self) -> TypeBlind:
        """Return raw data that it represents."""
        return cast(
            TypeBlind,
            cast(TypeRawList, self.device.raw)[ATTR_START_BLINDS][self.index],
        )

    @property
    def current_cover_position(self) -> int:
        """Get the current position of the blind."""
        return self.raw[ATTR_BLIND_CURRENT_POSITION]
