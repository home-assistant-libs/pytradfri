"""Test Blinds."""

import json
from typing import Any

import pytest

from pytradfri.device import Device

from tests.common import load_fixture


@pytest.fixture(name="device")
def device_fixture(request: pytest.FixtureRequest) -> Device:
    """Return a device."""
    device_response: dict[str, Any] = json.loads(request.getfixturevalue(request.param))
    return Device(device_response)


@pytest.fixture(name="blind")
def blind_fixture() -> str:
    """Return a blind response."""
    return load_fixture("blind.json")


@pytest.mark.parametrize("device", ["blind"], indirect=True)
def test_device_info_properties(device: Device) -> None:
    """Test device info properties."""
    info = device.device_info

    assert info.manufacturer == "IKEA of Sweden"
    assert info.model_number == "FYRTUR block-out roller blind"
    assert info.firmware_version == "2.2.007"
    assert info.serial == ""
    assert info.battery_level == 77


@pytest.mark.parametrize("device", ["blind"], indirect=True)
def test_current_position(device: Device) -> None:
    """Test blind position."""
    blind = device.blind_control.blinds[0]
    assert blind.current_cover_position == 50


@pytest.mark.parametrize("device", ["blind"], indirect=True)
def test_set_state(device: Device) -> None:
    """Test set state."""
    blind_control = device.blind_control
    assert blind_control is not None
    command = blind_control.set_state(50)
    assert command.data == {"15015": [{"5536": 50}]}


@pytest.mark.parametrize("device", ["blind"], indirect=True)
def test_trigger_blind(device: Device) -> None:
    """Test trigger blind."""
    blind_control = device.blind_control
    assert blind_control is not None
    command = blind_control.trigger_blind()
    assert command.data == {"15015": [{"5523": True}]}
