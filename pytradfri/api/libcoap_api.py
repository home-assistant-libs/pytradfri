"""COAP implementation."""
from __future__ import annotations

import json
import logging
import subprocess
from time import time
from typing import TYPE_CHECKING, Any, Protocol, Union, cast, overload

from ..command import Command, T
from ..error import ClientError, RequestError, RequestTimeout, ServerError
from ..gateway import Gateway

_LOGGER = logging.getLogger(__name__)

CLIENT_ERROR_PREFIX = "4."
SERVER_ERROR_PREFIX = "5."


class APIRequestProtocol(Protocol):
    """Represent the protocol for the APIFactory request method."""

    @overload
    def __call__(self, api_commands: Command[T], timeout: int | None = None) -> T:
        """Define the signature of the request method."""

    @overload
    def __call__(
        self, api_commands: list[Command[T]], timeout: int | None = None
    ) -> list[T]:
        """Define the signature of the request method."""

    def __call__(
        self, api_commands: Command[T] | list[Command[T]], timeout: int | None = None
    ) -> T | list[T]:
        """Define the signature of the request method."""


class APIFactory:
    """APIFactory."""

    def __init__(
        self,
        host: str,
        psk_id: str = "pytradfri",
        psk: str | None = None,
        timeout: int = 10,
    ) -> None:
        """Create object of class."""
        self._host = host
        self._psk_id = psk_id
        self._psk = psk
        self._timeout = timeout  # seconds

    @property
    def psk(self) -> str | None:
        """Return psk."""
        return self._psk

    @psk.setter
    def psk(self, value: str) -> None:
        """Set psk."""
        self._psk = value

    def _base_command(self, method: str) -> list[str]:
        """Return base command."""
        if self._psk is None:
            raise RuntimeError("You must enter a PSK.")

        return [
            "coap-client",
            "-u",
            self._psk_id,
            "-k",
            self._psk,
            "-v",
            "0",
            "-m",
            method,
        ]

    def _execute(self, api_command: Command[T], *, timeout: int | None = None) -> T:
        """Execute the command."""
        if api_command.observe:
            self._observe(api_command)
            return api_command.result

        method = api_command.method
        path = api_command.path
        data = api_command.data
        parse_json = api_command.parse_json
        url = api_command.url(self._host)

        proc_timeout = self._timeout
        if timeout is not None:
            proc_timeout = timeout

        command = self._base_command(method)

        kwargs: dict[str, Any] = {
            "stderr": subprocess.DEVNULL,
            "timeout": proc_timeout,
            "universal_newlines": True,
        }

        if data is not None:
            kwargs["input"] = json.dumps(data)
            command.append("-f")
            command.append("-")
            _LOGGER.debug("Executing %s %s %s: %s", self._host, method, path, data)
        else:
            _LOGGER.debug("Executing %s %s %s", self._host, method, path)

        command.append(url)

        try:
            return_value = subprocess.check_output(command, **kwargs)
        except subprocess.TimeoutExpired:
            raise RequestTimeout() from None
        except subprocess.CalledProcessError as exc:
            msg = f"Error executing request: {exc}"
            raise RequestError(msg) from None

        api_command.process_result(_process_output(return_value, parse_json))
        return api_command.result

    @overload
    def request(self, api_commands: Command[T], timeout: int | None = None) -> T:
        """Make a request. Timeout is in seconds."""

    @overload
    def request(
        self, api_commands: list[Command[T]], timeout: int | None = None
    ) -> list[T]:
        """Make a request. Timeout is in seconds."""

    def request(
        self, api_commands: Command[T] | list[Command[T]], timeout: int | None = None
    ) -> T | list[T]:
        """Make a request. Timeout is in seconds."""
        if not isinstance(api_commands, list):
            return self._execute(api_commands, timeout=timeout)

        command_results = []

        for api_command in api_commands:
            result = self._execute(api_command, timeout=timeout)
            command_results.append(result)

        return command_results

    def _observe(self, api_command: Command[T]) -> None:
        """Observe an endpoint."""
        path = api_command.path
        duration = api_command.observe_duration
        if duration <= 0:
            raise ValueError("Observation duration has to be greater than 0.")
        url = api_command.url(self._host)
        err_callback = api_command.err_callback

        command = self._base_command("get") + [
            "-s",
            str(duration),
            "-B",
            str(duration),
            url,
        ]

        try:
            proc = subprocess.Popen(  # pylint: disable=consider-using-with
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                universal_newlines=True,
            )
        except subprocess.CalledProcessError as exc:
            msg = f"Error executing request: {exc}"
            raise RequestError(msg) from None

        output = ""
        open_obj = 0
        start = time()

        def read_stdout() -> str:
            """Read from stdout."""
            if TYPE_CHECKING:
                assert proc.stdout
            return proc.stdout.read(1)

        for data in iter(read_stdout, ""):
            if data == "\n":
                _LOGGER.debug(
                    "Observing stopped for %s after %.1fs", path, time() - start
                )
                if err_callback:
                    err_callback(RequestError("Observing stopped."))
                break

            if data == "{":
                open_obj += 1
            elif data == "}":
                open_obj -= 1

            output += data

            if open_obj == 0:
                api_command.process_result(_process_output(output))
                output = ""

    def generate_psk(self, security_key: str) -> str:
        """Generate and set a psk from the security key."""
        if not self._psk:
            # Backup the real identity.
            existing_psk_id = self._psk_id

            # Set the default identity and security key for generation.
            self._psk_id = "Client_identity"
            self._psk = security_key

            # Ask the Gateway to generate the psk for the identity.
            self._psk = self.request(Gateway().generate_psk(existing_psk_id))

            # Restore the real identity.
            self._psk_id = existing_psk_id

        return self._psk


def _process_output(
    output: str, parse_json: bool = True
) -> list[Any] | dict[Any, Any] | str | None:
    """Process output."""
    output = output.strip()
    _LOGGER.debug("Received: %s", output)

    if not output:
        return None
    if "decrypt_verify" in output:
        raise RequestError(
            "Please compile coap-client without debug output. See "
            "instructions at "
            "https://github.com/ggravlingen/pytradfri#installation"
        )
    if output.startswith(CLIENT_ERROR_PREFIX):
        raise ClientError(output)
    if output.startswith(SERVER_ERROR_PREFIX):
        raise ServerError(output)
    if not parse_json:
        return output
    return cast(Union[dict[Any, Any], list[Any]], json.loads(output))
