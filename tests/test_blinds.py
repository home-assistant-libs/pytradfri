import pytest

from pytradfri.device import Device
from tests.devices import BLIND


@pytest.fixture
def device():
    return Device(BLIND)


def test_device_info_properties(device):
    info = device.device_info

    assert info.manufacturer == 'IKEA of Sweden'
    assert info.model_number == 'FYRTUR block-out roller blind'
    assert info.firmware_version == '2.2.007'
    assert info.serial == ''
    assert info.battery_level == 77

