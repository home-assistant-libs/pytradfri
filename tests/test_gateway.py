from pytradfri.const import ROOT_DEVICES
from pytradfri.gateway import Gateway


def test_get_device():
    gateway = Gateway()
    command = gateway.get_device(123)

    assert command.method == 'get'
    assert command.path == [ROOT_DEVICES, 123]
