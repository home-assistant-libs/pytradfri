"""Test API utilities."""

import json
from typing import Any

import pytest

from pytradfri.api.libcoap_api import APIFactory
from pytradfri.gateway import Gateway


def test_constructor_timeout_passed_to_subprocess(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that original timeout is passed to subprocess."""
    capture = {}

    def capture_args(*args: Any, **kwargs: Any) -> str:
        capture.update(kwargs)
        return json.dumps([])

    monkeypatch.setattr("subprocess.check_output", capture_args)

    api = APIFactory("anything", timeout=20, psk="abc")
    api.request(Gateway().get_devices())
    assert capture["timeout"] == 20


def test_custom_timeout_passed_to_subprocess(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that custom timeout is passed to subprocess."""
    capture = {}

    def capture_args(*args: Any, **kwargs: Any) -> str:
        capture.update(kwargs)
        return json.dumps([])

    monkeypatch.setattr("subprocess.check_output", capture_args)

    api = APIFactory("anything", psk="abc")
    api.request(Gateway().get_devices(), timeout=1)
    assert capture["timeout"] == 1
