"""Base class for a controller."""
from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING

from .air_purifier import AirPurifierResponse
from .blind import BlindResponse
from .light import LightResponse
from .signal_repeater import SignalRepeaterResponse
from .socket import SocketResponse

if TYPE_CHECKING:
    # avoid cyclic import at runtime.
    from . import Device


class BaseController:
    """Represent a controller."""

    def __init__(self, device: Device) -> None:
        """Create object of class."""
        self._device = device

    @property
    @abstractmethod
    def raw(
        self,
    ) -> list[BlindResponse] | list[SocketResponse] | list[
        SignalRepeaterResponse
    ] | list[LightResponse] | list[AirPurifierResponse]:
        """Return raw data that it represents."""

    @classmethod
    def _value_validate(
        cls, value: int, rnge: list[int] | tuple[int, int], identifier: str = "Given"
    ) -> None:
        """Make sure a value is within a given range."""
        if value is not None and (value < rnge[0] or value > rnge[1]):
            raise ValueError(
                f"{identifier} value must be between {rnge[0]} and {rnge[1]}."
            )

    def __repr__(self) -> str:
        """Return representation of class object."""
        return (
            f"<{type(self).__name__} for {self._device.name} ({len(self.raw)} devices)>"
        )
