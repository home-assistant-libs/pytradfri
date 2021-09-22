from pytradfri.device import Device

from .devices import OUTLET


def socket(raw):
    return Device(raw).socket_control.sockets[0]


def test_socket():
    plug = socket(OUTLET)

    assert plug.state == 0
