"""Represent a blind."""
from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

from ..const import ATTR_BLIND_CURRENT_POSITION, ATTR_ID

if TYPE_CHECKING:
    # avoid cyclic import at runtime.
    from . import Device


class BlindResponse(BaseModel):
    """Represent the blind part of the device response."""

    id: int = Field(alias=ATTR_ID)
    current_cover_position: int = Field(alias=ATTR_BLIND_CURRENT_POSITION)


class Blind:
    """Represent a blind."""

    def __init__(self, device: Device, index: int) -> None:
        """Create object of class."""
        self.device = device
        self.index = index

    @property
    def raw(self) -> BlindResponse:
        """Return raw response."""
        return self.device.raw.blind_control[self.index]  # type: ignore[union-attr, index]

    @property
    def current_cover_position(self) -> int:
        """Get the current position of the blind."""
        return self.raw.current_cover_position
