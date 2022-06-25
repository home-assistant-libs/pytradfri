"""COAP implementation using aiocoap."""
from __future__ import annotations

import asyncio
from collections.abc import Callable
from enum import Enum
import json
import logging
from typing import Any, Protocol, Union, cast, overload

from aiocoap import Context, Message
from aiocoap.credentials import CredentialsMissingError
from aiocoap.error import (
    ConstructionRenderableError,
    Error,
    LibraryShutdown,
    TimeoutError as COAPTimeoutError,
)
from aiocoap.numbers.codes import Code
from aiocoap.protocol import BlockwiseRequest

from ..command import Command, T
from ..error import ClientError, RequestTimeout, ServerError
from ..gateway import Gateway

_LOGGER = logging.getLogger(__name__)


class UndefinedType(Enum):
    """Singleton type for use with not set sentinel values."""

    _singleton = 0


_SENTINEL = UndefinedType._singleton  # pylint: disable=protected-access


class APIRequestProtocol(Protocol):
    """Represent the protocol for the APIFactory request method."""

    @overload
    async def __call__(
        self, api_commands: Command[T], timeout: float | None = None
    ) -> T:
        """Define the signature of the request method."""

    @overload
    async def __call__(
        self, api_commands: list[Command[T]], timeout: float | None = None
    ) -> list[T]:
        """Define the signature of the request method."""

    async def __call__(
        self, api_commands: Command[T] | list[Command[T]], timeout: float | None = None
    ) -> T | list[T]:
        """Define the signature of the request method."""


class APIFactory:
    """ApiFactory."""

    def __init__(
        self,
        host: str,
        psk_id: str = "pytradfri",
        psk: str | None = None,
        internal_create: UndefinedType | None = None,
    ):
        """Create object of class."""
        if internal_create is not _SENTINEL:
            raise ValueError("Use APIFactory.init(…) to initialize APIFactory")

        self._psk = psk
        self._host = host
        self._psk_id = psk_id
        self._observations_err_callbacks: list[Callable[[Exception], None]] = []
        self._protocol: asyncio.Task[Context] | None = None
        self._reset_lock = asyncio.Lock()
        self._shutdown = False

    @classmethod
    async def init(
        cls, host: str, psk_id: str = "pytradfri", psk: str | None = None
    ) -> "APIFactory":
        """Initialize an APIFactory."""
        instance = cls(host, psk_id=psk_id, psk=psk, internal_create=_SENTINEL)
        if psk:
            await instance._update_credentials()
        return instance

    @property
    def psk_id(self) -> str:
        """Return psk id."""
        return self._psk_id

    @property
    def psk(self) -> str | None:
        """Return psk."""
        return self._psk

    async def _get_protocol(self) -> Context:
        """Get the protocol for the request."""
        if self._protocol is None:
            self._protocol = asyncio.create_task(Context.create_client_context())
        return await self._protocol

    async def _reset_protocol(self, exc: BaseException | None = None) -> None:
        """Reset the protocol if an error occurs."""
        skip = self._reset_lock.locked()
        async with self._reset_lock:
            if self._shutdown:
                return
            if skip:
                # The lock was already acquired, so another task was already
                # in the process of resetting the protocol, so we don't need
                # to do it again.
                #
                # This is only here for performance reasons.  It should be
                # safe if the protocol is reset multiple times.
                _LOGGER.debug("Skipping reset: protocol was already being reset")
                return

            _LOGGER.debug("Resetting protocol")

            # Be responsible and clean up.
            protocol = await self._get_protocol()
            await protocol.shutdown()
            self._protocol = None

            # The error callbacks are called when shutting down the protocol.
            # Clear the saved callbacks
            self._observations_err_callbacks.clear()

    async def shutdown(self, exc: Exception | None = None) -> None:
        """Shutdown the API events.

        This should be called before closing the event loop.
        """
        await self._reset_protocol(exc)
        self._shutdown = True

    async def _get_response(
        self, msg: Message, timeout: float | None
    ) -> tuple[BlockwiseRequest, Message]:
        """Perform the request, get the response."""
        try:
            protocol = await self._get_protocol()
            pr_req: BlockwiseRequest = protocol.request(msg)
            pr_resp: Message = await asyncio.wait_for(pr_req.response, timeout)
            return pr_req, pr_resp
        except CredentialsMissingError as exc:
            await self._reset_protocol(exc)
            await self._update_credentials()
            raise ServerError("There was an error with the request.", exc) from exc
        except ConstructionRenderableError as exc:
            raise ClientError("There was an error with the request.", exc) from exc
        except asyncio.TimeoutError as exc:
            await self._reset_protocol(exc)
            await self._update_credentials()
            raise RequestTimeout("Request timed out.", exc) from exc
        except COAPTimeoutError as exc:
            await self._reset_protocol(exc)
            await self._update_credentials()
            raise RequestTimeout("Request timed out.", exc) from exc
        except LibraryShutdown as exc:
            raise ClientError("Protocol is shutdown.", exc) from exc
        except Error as exc:
            await self._reset_protocol(exc)
            await self._update_credentials()
            raise ServerError("There was an error with the request.", exc) from exc
        except asyncio.CancelledError as exc:
            await self._reset_protocol(exc)
            await self._update_credentials()
            raise exc

    async def _execute(self, api_command: Command[T], timeout: float | None) -> T:
        """Execute the command."""
        if api_command.observe:
            await self._observe(api_command, timeout)
            # The observe command result is set by the observe helper method above.
            return api_command.result

        method = api_command.method
        data = api_command.data
        parse_json = api_command.parse_json
        url = api_command.url(self._host)

        kwargs = {}

        if data is not None:
            kwargs["payload"] = json.dumps(data).encode("utf-8")

        api_method = Code.GET
        if method == "put":
            api_method = Code.PUT
        elif method == "post":
            api_method = Code.POST
        elif method == "delete":
            api_method = Code.DELETE
        elif method == "fetch":
            api_method = Code.FETCH
        elif method == "patch":
            api_method = Code.PATCH

        msg = Message(code=api_method, uri=url, **kwargs)

        _LOGGER.debug("Executing %s %s", self._host, api_command)

        _, res = await self._get_response(msg, timeout)
        api_command.process_result(_process_output(res, parse_json))

        return api_command.result

    @overload
    async def request(
        self, api_commands: Command[T], timeout: float | None = None
    ) -> T:
        """Make a request."""

    @overload
    async def request(
        self, api_commands: list[Command[T]], timeout: float | None = None
    ) -> list[T]:
        """Make a request."""

    async def request(
        self, api_commands: Command[T] | list[Command[T]], timeout: float | None = None
    ) -> T | list[T]:
        """Make a request."""
        if not isinstance(api_commands, list):
            _LOGGER.debug("REQUEST call single: %s %s", self._host, api_commands)
            result = await self._execute(api_commands, timeout)
            _LOGGER.debug("REQUEST result single: %s", result)

            return result

        _LOGGER.debug("REQUEST call multiple: %s %s", self._host, api_commands)
        commands = (self._execute(api_command, timeout) for api_command in api_commands)
        command_results: list[T] = await asyncio.gather(*commands)
        _LOGGER.debug("REQUEST result multiple: %s", command_results)

        return command_results

    async def _observe(self, api_command: Command[T], timeout: float | None) -> None:
        """Observe an endpoint."""
        duration = api_command.observe_duration
        url = api_command.url(self._host)
        err_callback = api_command.err_callback

        msg = Message(code=Code.GET, uri=url, observe=duration)

        # Note that this is necessary to start observing
        pr_req, pr_rsp = await self._get_response(msg, timeout)

        api_command.process_result(_process_output(pr_rsp))

        def success_callback(res: Message) -> None:
            api_command.process_result(_process_output(res))

        def error_callback(exc: Exception) -> None:
            if isinstance(exc, LibraryShutdown):
                _LOGGER.debug("Protocol is shutdown, stopping observation")
                return

            if err_callback:
                err_callback(exc)

        observation = pr_req.observation
        # The observation is set on the request
        # since we pass a Message with observe set above.
        assert observation is not None
        observation.register_callback(success_callback)
        observation.register_errback(error_callback)
        self._observations_err_callbacks.append(observation.error)

    async def generate_psk(self, security_key: str) -> str:
        """Generate and set a psk from the security key."""
        if not self._psk:
            # Set context once for generating key
            protocol = await self._get_protocol()
            command = Gateway().generate_psk(self._psk_id)
            protocol.client_credentials.load_from_dict(
                {
                    f"coaps://{self._host}:5684/{command.path_str}": {
                        "dtls": {
                            "psk": security_key.encode("utf-8"),
                            "client-identity": "Client_identity".encode("utf-8"),
                        }
                    }
                }
            )

            self._psk = cast(str, await self.request(command))

            # aiocoap has now cached our psk, so it must be reset.
            # We also no longer need the protocol, so this will clean that up.
            await self._reset_protocol()
            await self._update_credentials()

        return self._psk

    async def _update_credentials(self) -> None:
        """Update credentials."""
        if not self._psk:
            # No credentials to reset
            return
        protocol = await self._get_protocol()
        protocol.client_credentials.load_from_dict(
            {
                f"coaps://{self._host}:5684/*": {
                    "dtls": {
                        "psk": self._psk.encode("utf-8"),
                        "client-identity": self._psk_id.encode("utf-8"),
                    }
                }
            }
        )


def _process_output(
    res: Message, parse_json: bool = True
) -> list[Any] | dict[Any, Any] | str | None:
    """Process output."""
    res_payload: str = res.payload.decode("utf-8")
    output = res_payload.strip()

    _LOGGER.debug("Status: %s, Received: %s", res.code, output)

    if not output:
        return None

    # Codes are defined here:
    # https://github.com/chrysn/aiocoap/blob/7b7d43655454682cad6c53e156176d555f3b65a8
    # /aiocoap/numbers/codes.py
    if not res.code.is_successful():
        if 128 <= res.code < 160:
            raise ClientError(f"Gateway payload: {output}. Error code: {res.code}.")
        if 160 <= res.code < 192:
            raise ServerError(f"Gateway payload: {output}. Error code: {res.code}.")

    if not parse_json:
        return output

    return cast(Union[list[Any], dict[Any, Any]], json.loads(output))
