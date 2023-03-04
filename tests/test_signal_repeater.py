"""Test for the signal repeater device."""


from pytradfri.device import Device
from tests.devices import SIGNAL_REPEATER


def test_properties():
    """Test that we can fetch attributes of the signal repeater."""
    device = Device(SIGNAL_REPEATER)
    signal_repeater = device.signal_repeater_control.signal_repeaters[0]
    assert signal_repeater.id == 0
