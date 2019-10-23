import pytest

from pytradfri.device import Device
from devices import SIGNAL_REPEATER


@pytest.fixture
def device():
    return Device(SIGNAL_REPEATER)


def test_device_info_properties(device):
    info = device.device_info

    assert info.manufacturer == 'IKEA of Sweden'
    assert info.model_number == 'TRADFRI Signal Repeater'
    assert info.firmware_version == '2.2.005'
    assert info.serial == ''
