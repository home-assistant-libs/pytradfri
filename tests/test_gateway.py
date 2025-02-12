"""Test Gateway."""

from copy import deepcopy
from datetime import datetime

import pytest

from pytradfri.const import ATTR_CLIENT_IDENTITY_PROPOSED, ATTR_PSK, ROOT_DEVICES
from pytradfri.gateway import Gateway, GatewayInfo

GATEWAY_INFO = {
    "9023": "xyz.pool.ntp.pool",
    "9059": 1509788799,
    "9073": 0,  # Unknown
    "9060": "2017-11-04T09:46:39.046784Z",
    "9080": 0,  # Unknown
    "9071": 1,
    "9062": 0,  # Unknown
    "9061": 0,
    "9093": 0,
    "9029": "1.2.42",
    "9081": "7e0000000000000a",
    "9092": 0,
    "9069": 1509474847,
    "9082": True,  # Unknown
    "9055": 0,
    "9083": "123-45-67",
    "9066": 5,
    "9054": 0,
    "9077": 0,  # Unknown
    "9072": 0,  # Unknown
    "9074": 0,  # Unknown
    "9075": 0,  # Unknown
    "9076": 0,  # Unknown
    "9078": 0,  # Unknown
    "9079": 0,  # Unknown
    "9106": 0,  # Unknown
    "9105": 0,  # Unknown
}


@pytest.fixture(name="gateway")
def gateway_fixture():
    """Fixture that returns a gateway."""
    return Gateway()


def test_get_device(gateway):
    """Test get device."""
    command = gateway.get_device(123)

    assert command.method == "get"
    assert command.path == [ROOT_DEVICES, "123"]


def test_gateway_info():
    """Test retrieval of gateway info."""
    gateway_info = GatewayInfo(GATEWAY_INFO)

    assert gateway_info.id == "7e0000000000000a"
    assert gateway_info.ntp_server == "xyz.pool.ntp.pool"
    assert gateway_info.firmware_version == "1.2.42"
    assert gateway_info.current_time == datetime.utcfromtimestamp(1509788799)
    assert gateway_info.current_time_iso8601 == "2017-11-04T09:46:39.046784Z"
    assert gateway_info.first_setup == datetime.utcfromtimestamp(1509474847)
    assert gateway_info.homekit_id == "123-45-67"
    assert gateway_info.path == ["15011", "15012"]

    new_gateway = deepcopy(GATEWAY_INFO)
    new_gateway["9059"] = None
    new_gateway["9069"] = None
    gateway_info_empty = GatewayInfo(new_gateway)

    assert gateway_info_empty.current_time is None
    assert gateway_info_empty.first_setup is None


def test_generate_psk(gateway):
    """Test psk generation."""
    command = gateway.generate_psk("identityString")

    assert command.method == "post"
    assert command.data == {ATTR_CLIENT_IDENTITY_PROPOSED: "identityString"}
    assert "PSKstring" in command.process_result({ATTR_PSK: "PSKstring"})
