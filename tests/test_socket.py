"""Test Socket."""

from pytradfri.device import Device
from pytradfri.resource import TypeRaw

from .devices import OUTLET


def socket(raw: TypeRaw) -> Device:
    """Return socket."""
    return Device(raw).socket_control.sockets[0]


def test_socket() -> None:
    """Test socket."""
    plug = socket(OUTLET)

    assert plug.state == 0
