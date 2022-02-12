"""Represent a blind."""
from __future__ import annotations

from typing import TYPE_CHECKING

from ..const import ATTR_BLIND_CURRENT_POSITION, ATTR_START_BLINDS
from ..typing import TypeBlind

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
    def raw(self) -> TypeBlind:
        """Return raw data that it represents."""
        return self.device.raw[ATTR_START_BLINDS][self.index]

    @property
    def current_cover_position(self) -> int:
        """Get the current position of the blind."""
        return self.raw[ATTR_BLIND_CURRENT_POSITION]
