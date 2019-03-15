"""Test API utilities."""
import asyncio
import functools

from pytradfri.api.aiocoap_api import APIFactory
from pytradfri.command import Command


def async_test(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        future = f(*args, **kwargs)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(future)
    return wrapper


class MockCode:
    def is_successful(self):
        return True


class MockResponse:
    @property
    def code(self):
        return MockCode()

    @property
    def payload(self):
        return '{}'.encode('utf-8')


class MockProtocol:
    async def mock_response(self):
        return MockResponse()

    @property
    def response(self):
        return self.mock_response()


class MockContext:
    def request(self, arg):
        return MockProtocol()


async def mock_create_context(loop):
    return MockContext()


@async_test
async def test_request_returns_single(monkeypatch):
    monkeypatch.setattr('aiocoap.Context.create_client_context',
                        mock_create_context)

    api = APIFactory('127.0.0.1').request

    command = Command('', '')

    response = await api(command)

    assert type(response) != list


@async_test
async def test_request_returns_list(monkeypatch):
    monkeypatch.setattr('aiocoap.Context.create_client_context',
                        mock_create_context)

    api = APIFactory('127.0.0.1').request

    command = Command('', '')

    response = await api([command, command, command])

    assert type(response) == list
