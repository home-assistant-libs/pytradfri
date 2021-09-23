"""Test API utilities."""
import asyncio
import functools

from pytradfri.api.aiocoap_api import APIFactory
from pytradfri.command import Command


def async_test(f):
    """Start test."""

    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        """Wrap to start event loop."""
        future = f(*args, **kwargs)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(future)

    return wrapper


class MockCode:
    """Mock Code."""

    def is_successful(self):
        """Is succesful."""
        return True


class MockResponse:
    """Mock response."""

    @property
    def code(self):
        """Return code."""
        return MockCode()

    @property
    def payload(self):
        """Return payload."""
        return "{}".encode("utf-8")


class MockProtocol:
    """Mock Protocol."""

    async def mock_response(self):
        """Return protocol response."""
        return MockResponse()

    @property
    def response(self):
        """Return protocol response."""
        return self.mock_response()


class MockContext:
    """Mock a context."""

    def request(self, arg):
        """Request a protocol."""
        return MockProtocol()


async def mock_create_context():
    """Return a context."""
    return MockContext()


@async_test
async def test_request_returns_single(monkeypatch):
    """Test return single object."""
    monkeypatch.setattr("aiocoap.Context.create_client_context", mock_create_context)

    api = (await APIFactory.init("127.0.0.1")).request

    command = Command("", "")

    response = await api(command)

    assert type(response) != list


@async_test
async def test_request_returns_list(monkeypatch):
    """Test return of lists."""
    monkeypatch.setattr("aiocoap.Context.create_client_context", mock_create_context)

    api = (await APIFactory.init("127.0.0.1")).request

    command = Command("", "")

    response = await api([command, command, command])

    assert type(response) == list
