"""Base class for a controller."""
from __future__ import annotations

from abc import abstractproperty
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # avoid cyclic import at runtime.
    from . import Device


class BaseController:
    """Represent a controller."""

    def __init__(self, device: Device) -> None:
        """Create object of class."""
        self._device = device

    @abstractproperty
    def raw(self):
        """Return raw data that it represents."""

    def _value_validate(
        self, value: int, rnge: list[int] | tuple[int, int], identifier: str = "Given"
    ) -> None:
        """Make sure a value is within a given range."""
        if value is not None and (value < rnge[0] or value > rnge[1]):
            raise ValueError(
                "%s value must be between %d and %d." % (identifier, rnge[0], rnge[1])
            )

    def __repr__(self):
        """Return representation of class object."""
        return "<{} for {} ({} devices)>".format(
            type(self).__name__, self._device.name, len(self.raw)
        )
