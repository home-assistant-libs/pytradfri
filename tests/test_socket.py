"""Test Socket."""
from pytradfri.device import Device

from .devices import OUTLET


def socket(raw):
    """Return socket."""
    return Device(raw).socket_control.sockets[0]


def test_socket():
    """Test socket."""
    plug = socket(OUTLET)

    assert plug.state == 0
