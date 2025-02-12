"""Test aiocoap API."""

import asyncio
from collections.abc import Awaitable, Callable, Generator
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

from aiocoap import Context
from aiocoap.credentials import CredentialsMap
from aiocoap.error import Error
import pytest

from pytradfri.api.aiocoap_api import APIFactory
from pytradfri.command import Command
from pytradfri.error import ServerError


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


class MockRequest:
    """Mock Protocol."""

    def __init__(self, response: Callable[[], Awaitable[Any]]) -> None:
        """Create the request."""
        self._response = response

    @property
    def response(self) -> Any:
        """Return protocol response."""
        return self._response()


def process_result(result: Any) -> Any:
    """Process result."""
    return result


@pytest.fixture(name="response")
def response_fixture() -> AsyncMock:
    """Mock response."""
    return AsyncMock()


@pytest.fixture(name="context")
def context_fixture(response: AsyncMock) -> Generator[MagicMock]:
    """Mock context."""
    with patch(
        "pytradfri.api.aiocoap_api.Context.create_client_context"
    ) as create_client_context:
        context = MagicMock(spec=Context)

        async def create_context() -> MagicMock:
            """Reset the context."""
            response.return_value = MockResponse()
            response.side_effect = None
            context.serversite = None
            context.request_interfaces = []
            context.client_credentials = CredentialsMap()
            context.server_credentials = CredentialsMap()
            context.request.return_value = MockRequest(response=response)
            context.shutdown.side_effect = None
            return context

        create_client_context.side_effect = create_context
        context.create_client_context = create_client_context
        yield context


async def test_request_returns_single(context: MagicMock) -> None:
    """Test return single object."""
    api = (await APIFactory.init("127.0.0.1")).request

    command: Command[dict[str, int]] = Command("", [""], process_result=process_result)

    response = await api(command)

    assert response == {"one": 1}


async def test_request_returns_list(context: MagicMock) -> None:
    """Test return of lists."""
    api = (await APIFactory.init("127.0.0.1")).request

    command: Command[dict[str, int]] = Command("", [""], process_result=process_result)

    response = await api([command, command, command])

    assert isinstance(response, list)
    assert response == [{"one": 1}, {"one": 1}, {"one": 1}]


async def test_context_shutdown_request(
    context: MagicMock, response: AsyncMock
) -> None:
    """Test a request while context is shutting down."""
    factory = await APIFactory.init("127.0.0.1", psk="test-psk")
    shutdown_event = asyncio.Event()

    async def mock_shutdown() -> None:
        """Mock shutdown."""
        response.side_effect = Exception("Context was shutdown")
        await shutdown_event.wait()

    context.shutdown.side_effect = mock_shutdown
    response.side_effect = Error("Boom!")

    request_task_1 = asyncio.create_task(
        factory.request(Command("", [""], process_result=process_result))
    )
    await asyncio.sleep(0)
    request_task_2 = asyncio.create_task(
        factory.request(Command("", [""], process_result=process_result))
    )
    await asyncio.sleep(0)

    shutdown_event.set()
    with pytest.raises(ServerError):
        await request_task_1
    result = await request_task_2

    assert context.shutdown.call_count == 1
    assert context.request.call_count == 2
    assert result == {"one": 1}


async def test_shutdown_after_reset_protocol_error(
    context: MagicMock, response: AsyncMock
) -> None:
    """Test shutdown after unexpected error during protocol reset."""
    # Pass a psk to create a protocol.
    factory = await APIFactory.init("127.0.0.1", psk="test-psk")
    assert context.create_client_context.call_count == 1
    assert context.shutdown.call_count == 0

    class UnknownError(Exception):
        """Unknown error."""

    context.shutdown.side_effect = UnknownError("Unexpected error!")
    response.side_effect = Error("Boom!")

    request_task = asyncio.create_task(
        factory.request(Command("", [""], process_result=process_result))
    )
    await asyncio.sleep(0)

    assert context.create_client_context.call_count == 1
    assert context.shutdown.call_count == 1

    with pytest.raises(UnknownError):
        await request_task

    # Shutdown will create a new protocol context and then shut it down.
    await factory.shutdown()

    assert context.create_client_context.call_count == 2
    assert context.shutdown.call_count == 2
