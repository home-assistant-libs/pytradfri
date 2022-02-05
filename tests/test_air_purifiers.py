"""Test Air Purifiers."""
import pytest

from pytradfri.device import Device

from .devices import AIR_PURIFIER


@pytest.fixture
def device():
    """Return Device."""
    return Device(AIR_PURIFIER)


def test_device_info_properties(device):
    """Test device info properties."""
    info = device.device_info

    assert info.manufacturer == "IKEA of Sweden"
    assert info.model_number == "STARKVIND Air purifier"
    assert info.firmware_version == "1.0.033"
    assert info.serial == ""


def test_state(device):
    """Test air purifier mode."""

    air_purifier = device.air_purifier_control.air_purifiers[0]
    assert air_purifier.state is True


def test_is_auto_mode(device):
    """Test air purifier mode."""

    air_purifier = device.air_purifier_control.air_purifiers[0]
    assert air_purifier.is_auto_mode is True


def test_air_quality(device):
    """Test air quality measured by the air purifier."""

    air_purifier = device.air_purifier_control.air_purifiers[0]
    assert air_purifier.air_quality == 5


def test_fan_speed(device):
    """Test air purifier fan speed."""

    air_purifier = device.air_purifier_control.air_purifiers[0]
    assert air_purifier.fan_speed == 10


def test_controls_locked(device):
    """Test air purifier controls locked."""

    air_purifier = device.air_purifier_control.air_purifiers[0]
    assert not air_purifier.controls_locked


def test_leds_off(device):
    """Test air purifier led's off."""

    air_purifier = device.air_purifier_control.air_purifiers[0]
    assert not air_purifier.leds_off


def test_motor_runtime_total(device):
    """Test motor's total runtime."""

    air_purifier = device.air_purifier_control.air_purifiers[0]
    assert air_purifier.motor_runtime_total == 2


def test_filter_lifetime_total(device):
    """Test filter's total life time."""

    air_purifier = device.air_purifier_control.air_purifiers[0]
    assert air_purifier.filter_lifetime_total == 259200


def test_filter_status(device):
    """Test filter status."""

    air_purifier = device.air_purifier_control.air_purifiers[0]
    assert air_purifier.filter_status == 0


def test_filter_lifetime_remaining(device):
    """Test remaining life of filter."""

    air_purifier = device.air_purifier_control.air_purifiers[0]
    assert air_purifier.filter_lifetime_remaining == 259198


def test_filter_runtime(device):
    """Test filter's run time."""

    air_purifier = device.air_purifier_control.air_purifiers[0]
    assert air_purifier.filter_runtime == 2
