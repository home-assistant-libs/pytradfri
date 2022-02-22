"""Test Socket."""
import pytest

from pytradfri.device import Device

from .devices import OUTLET


@pytest.fixture
def device():
    """Return socket."""
    return Device(OUTLET)


def test_socket(device):
    """Test socket."""
    plug = device.socket_control.sockets[0]

    assert plug.state is False
