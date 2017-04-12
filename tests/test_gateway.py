from opentradfri.const import ROOT_DEVICES, ATTR_NAME
from opentradfri.gateway import Gateway


def test_get_device(mock_api):
    mock_api.mock_request('get', [ROOT_DEVICES, 123], {
        ATTR_NAME: 'Test name'
    })
    gateway = Gateway(mock_api)
    dev = gateway.get_device(123)

    assert dev.name == 'Test name'
