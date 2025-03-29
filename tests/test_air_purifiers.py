"""Test Air Purifiers."""

import json
from typing import Any

import pytest

from pytradfri.device import Device

from tests.common import load_fixture

pytestmark = pytest.mark.parametrize("device", ["air_purifier"], indirect=True)


@pytest.fixture(name="device")
def device_fixture(request: pytest.FixtureRequest) -> Device:
    """Return a device."""
    device_response: dict[str, Any] = json.loads(request.getfixturevalue(request.param))
    return Device(device_response)


@pytest.fixture(name="air_purifier")
def air_purifier_fixture() -> str:
    """Return a air_purifier response."""
    return load_fixture("air_purifier.json")


def test_device_info_properties(device: Device) -> None:
    """Test device info properties."""
    info = device.device_info

    assert info.manufacturer == "IKEA of Sweden"
    assert info.model_number == "STARKVIND Air purifier"
    assert info.firmware_version == "1.0.033"
    assert info.serial == ""


def test_state(device: Device) -> None:
    """Test air purifier mode."""
    air_purifier = device.air_purifier_control.air_purifiers[0]
    assert air_purifier.state is True


def test_is_auto_mode(device: Device) -> None:
    """Test air purifier mode."""
    air_purifier = device.air_purifier_control.air_purifiers[0]
    assert air_purifier.is_auto_mode is True


def test_air_quality(device: Device) -> None:
    """Test air quality measured by the air purifier."""
    air_purifier = device.air_purifier_control.air_purifiers[0]
    assert air_purifier.air_quality == 5


def test_fan_speed(device: Device) -> None:
    """Test air purifier fan speed."""
    air_purifier = device.air_purifier_control.air_purifiers[0]
    assert air_purifier.fan_speed == 10


def test_controls_locked(device: Device) -> None:
    """Test air purifier controls locked."""
    air_purifier = device.air_purifier_control.air_purifiers[0]
    assert not air_purifier.controls_locked


def test_leds_off(device: Device) -> None:
    """Test air purifier led's off."""
    air_purifier = device.air_purifier_control.air_purifiers[0]
    assert not air_purifier.leds_off


def test_motor_runtime_total(device: Device) -> None:
    """Test motor's total runtime."""
    air_purifier = device.air_purifier_control.air_purifiers[0]
    assert air_purifier.motor_runtime_total == 2


def test_filter_lifetime_total(device: Device) -> None:
    """Test filter's total life time."""
    air_purifier = device.air_purifier_control.air_purifiers[0]
    assert air_purifier.filter_lifetime_total == 259200


def test_filter_status(device: Device) -> None:
    """Test filter status."""
    air_purifier = device.air_purifier_control.air_purifiers[0]
    assert air_purifier.filter_status is False


def test_filter_lifetime_remaining(device: Device) -> None:
    """Test remaining life of filter."""
    air_purifier = device.air_purifier_control.air_purifiers[0]
    assert air_purifier.filter_lifetime_remaining == 259198


def test_filter_runtime(device: Device) -> None:
    """Test filter's run time."""
    air_purifier = device.air_purifier_control.air_purifiers[0]
    assert air_purifier.filter_runtime == 2


def test_turn_off(device: Device) -> None:
    """Test turn off."""
    air_purifier_control = device.air_purifier_control
    assert air_purifier_control is not None
    command = air_purifier_control.turn_off()
    assert command.data == {"15025": [{"5900": 0}]}


def test_turn_on_auto_mode(device: Device) -> None:
    """Test turn on auto mode."""
    air_purifier_control = device.air_purifier_control
    assert air_purifier_control is not None
    command = air_purifier_control.turn_on_auto_mode()
    assert command.data == {"15025": [{"5900": 1}]}


def test_set_fan_speed(device: Device) -> None:
    """Test set fan speed."""
    air_purifier_control = device.air_purifier_control
    assert air_purifier_control is not None
    command = air_purifier_control.set_fan_speed(10)
    assert command.data == {"15025": [{"5900": 10}]}


@pytest.mark.parametrize(("locked", "expected_value"), [(True, 1), (False, 0)])
def test_set_controls_locked(device: Device, locked: bool, expected_value: int) -> None:
    """Test set controls locked."""
    air_purifier_control = device.air_purifier_control
    assert air_purifier_control is not None
    command = air_purifier_control.set_controls_locked(locked)
    assert command.data == {"15025": [{"5905": expected_value}]}


@pytest.mark.parametrize(("leds_off", "expected_value"), [(True, 1), (False, 0)])
def test_set_leds_off(device: Device, leds_off: bool, expected_value: int) -> None:
    """Test set leds off."""
    air_purifier_control = device.air_purifier_control
    assert air_purifier_control is not None
    command = air_purifier_control.set_leds_off(leds_off)
    assert command.data == {"15025": [{"5906": expected_value}]}
