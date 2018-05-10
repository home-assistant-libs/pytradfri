import pytest
from datetime import datetime

from pytradfri.gateway import Gateway, GatewayInfo
from pytradfri.const import (
    ROOT_DEVICES,
    ATTR_CLIENT_IDENTITY_PROPOSED,
    ATTR_PSK
)


GATEWAY_INFO = {
  "9023": "xyz.pool.ntp.pool",
  "9029": "1.2.42",
  "9054": 0,
  "9055": 0,
  "9059": 1509788799,
  "9060": "2017-11-04T09:46:39.046784Z",
  "9061": 0,
  "9062": 0,
  "9066": 5,
  "9069": 1509474847,
  "9071": 1,
  "9072": 0,
  "9073": 0,
  "9074": 0,
  "9075": 0,
  "9076": 0,
  "9077": 0,
  "9078": 0,
  "9079": 0,
  "9080": 0,
  "9081": "7e0000000000000a",
  "9083": "123-45-67",
  "9092": 0,
  "9093": 0,
  "9106": 0
}

GATEWAY_INFO_EMPTY = {}


@pytest.fixture
def gateway():
    return Gateway()


def test_get_device(gateway):
    command = gateway.get_device(123)

    assert command.method == 'get'
    assert command.path == [ROOT_DEVICES, 123]


def test_gateway_info():
    gateway_info = GatewayInfo(GATEWAY_INFO)
    gateway_info_empty = GatewayInfo(GATEWAY_INFO_EMPTY)

    assert gateway_info.id == '7e0000000000000a'
    assert gateway_info.ntp_server == 'xyz.pool.ntp.pool'
    assert gateway_info.firmware_version == '1.2.42'
    assert gateway_info.current_time == datetime.utcfromtimestamp(1509788799)
    assert gateway_info.current_time_iso8601 == '2017-11-04T09:46:39.046784Z'
    assert gateway_info.first_setup == datetime.utcfromtimestamp(1509474847)
    assert gateway_info.homekit_id == '123-45-67'
    assert gateway_info.path == ['15011', '15012']

    assert gateway_info_empty.current_time is None
    assert gateway_info_empty.first_setup is None


def test_generate_psk(gateway):
    command = gateway.generate_psk("identityString")

    assert command.method == 'post'
    assert command.data == {ATTR_CLIENT_IDENTITY_PROPOSED: "identityString"}
    assert "PSKstring" in command.process_result({ATTR_PSK: "PSKstring"})
