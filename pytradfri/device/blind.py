"""Represent a blind."""
from __future__ import annotations

from typing import TYPE_CHECKING, cast

from ..const import ATTR_BLIND_CURRENT_POSITION, ATTR_START_BLINDS
from ..resource import TypeRaw, TypeRawList

if TYPE_CHECKING:
    # avoid cyclic import at runtime.
    from . import Device


class Blind:
    """Represent a blind."""

    def __init__(self, device: Device, index: int) -> None:
        """Create object of class."""
        self.device = device
        self.index = index

    @property
    def raw(self) -> TypeRaw:
        """Return raw data that it represents."""
        return cast(
            TypeRaw,
            cast(TypeRawList, self.device.raw)[ATTR_START_BLINDS][self.index],
        )

    @property
    def current_cover_position(self) -> int:
        """Get the current position of the blind."""
        return cast(int, self.raw.get(ATTR_BLIND_CURRENT_POSITION))
