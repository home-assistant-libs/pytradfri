"""Represent a socket."""
from __future__ import annotations

from typing import TYPE_CHECKING, cast

from ..const import ATTR_DEVICE_STATE, ATTR_SWITCH_PLUG
from ..resource import TYPE_RAW, TYPE_RAW_LIST

if TYPE_CHECKING:
    # avoid cyclic import at runtime.
    from . import Device
else:
    Device = dict


class Socket:
    """Represent a socket."""

    def __init__(self, device: Device, index: int) -> None:
        """Create object of class."""
        self.device = device
        self.index = index

    @property
    def state(self) -> bool:
        """State."""
        if self.raw is None:
            return False
        return bool(self.raw.get(ATTR_DEVICE_STATE) == 1)

    @property
    def raw(self) -> TYPE_RAW | None:
        """Return raw data that it represents."""
        if not self.device.raw:
            return None
        return cast(
            TYPE_RAW, cast(TYPE_RAW_LIST, self.device.raw)[ATTR_SWITCH_PLUG][self.index]
        )

    def __repr__(self) -> str:
        """Return representation of class object."""
        state = "on" if self.state else "off"
        if self.device.name is None:
            name = "unknown"
        else:
            name = self.device.name
        return f"<Socket #{self.index} - name: {self.device.name}, state: {state}>"
