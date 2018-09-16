from pytradfri.device import Device
from devices import (
    SOCKET
)


def socket(raw):
    return Device(raw).socket_control.lights[0]


def test_socket():
    plug = socket(SOCKET)

    assert plug.state == 0
