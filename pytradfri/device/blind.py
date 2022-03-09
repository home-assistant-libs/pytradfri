"""Represent a blind."""
from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import Field

from ..const import ATTR_BLIND_CURRENT_POSITION
from ..resource import BaseResponse


class BlindResponse(BaseResponse):
    """Represent API response for a blind."""

    current_cover_position: int = Field(alias=ATTR_BLIND_CURRENT_POSITION)


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
    def raw(self) -> BlindResponse:
        """Return raw data that it represents."""
        blind_control_response = self.device.raw.blind_control
        assert blind_control_response is not None
        return blind_control_response[self.index]

    @property
    def current_cover_position(self) -> int:
        """Get the current position of the blind."""
        return self.raw.current_cover_position
