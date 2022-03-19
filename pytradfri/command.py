"""Command implementation."""
from __future__ import annotations

from collections.abc import Callable
from typing import Any, Generic, TypeVar

T = TypeVar("T")


class Command(Generic[T]):
    """The object for coap commands."""

    def __init__(
        self,
        method: str,
        path: list[str],
        data: Any | None = None,
        *,
        parse_json: bool = True,
        observe: bool = False,
        observe_duration: int = 0,
        process_result: Callable[..., T] | None = None,
        err_callback: Callable[[Exception], None] | None = None,
    ) -> None:
        """Create object of class."""
        self._method = method
        self._path = path
        self._data = data
        self._parse_json = parse_json
        self._process_result = process_result
        self._err_callback = err_callback
        self._observe = observe
        self._observe_duration = observe_duration
        self._raw_result: list[Any] | dict[Any, Any] | str | None = None
        # If there's no process_result callback, the result will always be None.
        # And in that case T will also be None.
        self._result: T = None  # type: ignore[assignment]

    @property
    def method(self) -> str:
        """Return method."""
        return self._method

    @property
    def path(self) -> list[str]:
        """Return path."""
        return self._path

    @property
    def data(self) -> dict[str, Any] | None:
        """Return data."""
        return self._data

    @property
    def parse_json(self) -> bool:
        """Json parsing result."""
        return self._parse_json

    def process_result(self, result: list[Any] | dict[Any, Any] | str | None) -> T:
        """Process and set result."""
        if self._process_result:
            self._result = self._process_result(result)

        self._raw_result = result
        return self._result

    @property
    def err_callback(self) -> Callable[[Exception], None] | None:
        """Will be fired when an observe request fails."""
        return self._err_callback

    @property
    def observe(self) -> bool:
        """Observe function."""
        return self._observe

    @property
    def observe_duration(self) -> int:
        """Return duration period of observations."""
        return self._observe_duration

    @property
    def raw_result(self) -> list[Any] | dict[Any, Any] | str | None:
        """Return raw result."""
        return self._raw_result

    @property
    def result(self) -> T:
        """Return result."""
        return self._result

    @property
    def path_str(self) -> str:
        """Return coap path."""
        return "/".join(str(v) for v in self._path)

    def url(self, host: str) -> str:
        """Generate url for coap client."""
        return f"coaps://{host}:5684/{self.path_str}"

    def __repr__(self) -> str:
        """Return the representation."""
        if self.data is None:
            template = "<Command {} {}{}>"
        else:
            template = "<Command {} {}: {}>"
        return template.format(self.method, self.path, self.data or "")
