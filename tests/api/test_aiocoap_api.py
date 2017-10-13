"""Test API utilities."""
import asyncio
import pytest

from pytradfri.api.aiocoap_api import api_factory
from pytradfri.command import Command


class MockCode:
    @property
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
    @asyncio.coroutine
    def mock_response(self):
        return MockResponse()

    @property
    def response(self):
        return self.mock_response()


class MockContext:
    def request(self, arg):
        return MockProtocol()


@asyncio.coroutine
def mock_create_context(loop):
    return MockContext()


@pytest.mark.asyncio
def test_request_returns_single(monkeypatch):
    monkeypatch.setattr('aiocoap.Context.create_client_context',
                        mock_create_context)

    api = yield from api_factory('127.0.0.1', 'key')

    command = Command('', '')

    response = yield from api(command)

    assert type(response) != list


@pytest.mark.asyncio
def test_request_returns_list(monkeypatch):
    monkeypatch.setattr('aiocoap.Context.create_client_context',
                        mock_create_context)

    api = yield from api_factory('127.0.0.1', 'key')

    command = Command('', '')

    response = yield from api([command, command, command])

    assert type(response) == list