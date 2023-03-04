"""Test aiocoap API."""
from typing import Any

import pytest
from aiocoap import Message

from pytradfri.api.aiocoap_api import APIFactory
from pytradfri.command import Command


class MockCode:
    """Mock Code."""

    def is_successful(self) -> bool:
        """Is successful."""
        return True


class MockResponse:
    """Mock response."""

    @property
    def code(self) -> MockCode:
        """Return code."""
        return MockCode()

    @property
    def payload(self) -> bytes:
        """Return payload."""
        return b'{"one": 1}'


class MockProtocol:
    """Mock Protocol."""

    async def mock_response(self) -> Any:
        """Return protocol response."""
        return MockResponse()

    @property
    def response(self) -> Any:
        """Return protocol response."""
        return self.mock_response()


class MockContext:
    """Mock a context."""

    def request(self, message: Message) -> MockProtocol:
        """Request a protocol."""
        return MockProtocol()


async def mock_create_context() -> MockContext:
    """Return a context."""
    return MockContext()


def process_result(result: Any) -> Any:
    """Process result."""
    return result


async def test_request_returns_single(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test return single object."""
    monkeypatch.setattr("aiocoap.Context.create_client_context", mock_create_context)

    api = (await APIFactory.init("127.0.0.1")).request

    command: Command[dict[str, int]] = Command("", [""], process_result=process_result)

    response = await api(command)

    assert response == {"one": 1}


async def test_request_returns_list(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test return of lists."""
    monkeypatch.setattr("aiocoap.Context.create_client_context", mock_create_context)

    api = (await APIFactory.init("127.0.0.1")).request

    command: Command[dict[str, int]] = Command("", [""], process_result=process_result)

    response = await api([command, command, command])

    assert isinstance(response, list)
    assert response == [{"one": 1}, {"one": 1}, {"one": 1}]
