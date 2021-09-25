"""Test API utilities."""
import json

import pytest

from pytradfri import RequestTimeout
from pytradfri.api.libcoap_api import APIFactory, retry_timeout
from pytradfri.gateway import Gateway


def test_retry_timeout_passes_args():
    """Test passing args."""
    calls = []

    def api(*args, **kwargs):
        """Mock api."""
        calls.append((args, kwargs))

    retry_api = retry_timeout(api)

    retry_api(1, 2, hello="world")
    assert len(calls) == 1
    args, kwargs = calls[0]
    assert args == (1, 2)
    assert kwargs == {"hello": "world"}


def test_retry_timeout_retries_timeouts():
    """Test retrying timeout."""
    calls = []

    def api(*args, **kwargs):
        """Mock api."""
        calls.append((args, kwargs))

        if len(calls) == 1:
            raise RequestTimeout()

    retry_api = retry_timeout(api, retries=2)

    retry_api(1, 2, hello="world")
    assert len(calls) == 2


def test_retry_timeout_raises_after_max_retries():
    """Test retrying timeout."""
    calls = []

    def api(*args, **kwargs):
        """Mock api."""
        calls.append((args, kwargs))

        raise RequestTimeout()

    retry_api = retry_timeout(api, retries=5)

    with pytest.raises(RequestTimeout):
        retry_api(1, 2, hello="world")

    assert len(calls) == 5


def test_constructor_timeout_passed_to_subprocess(monkeypatch):
    """Test that original timeout is passed to subprocess."""
    capture = {}

    def capture_args(*args, **kwargs):
        capture.update(kwargs)
        return json.dumps([])

    monkeypatch.setattr("subprocess.check_output", capture_args)

    api = APIFactory("anything", timeout=20)
    api.request(Gateway().get_devices())
    assert capture["timeout"] == 20


def test_custom_timeout_passed_to_subprocess(monkeypatch):
    """Test that custom timeout is passed to subprocess."""
    capture = {}

    def capture_args(*args, **kwargs):
        capture.update(kwargs)
        return json.dumps([])

    monkeypatch.setattr("subprocess.check_output", capture_args)

    api = APIFactory("anything")
    api.request(Gateway().get_devices(), timeout=1)
    assert capture["timeout"] == 1
