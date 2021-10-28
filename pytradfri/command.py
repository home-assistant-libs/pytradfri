"""Command implementation."""
from __future__ import annotations

from copy import deepcopy
from typing import Any, Callable, Optional

TypeProcessResultCb = Optional[Callable[[Any], Optional[str]]]
TypeErrCb = Optional[Callable[[str], str]]


class Command:
    """The object for coap commands."""

    def __init__(
        self,
        method: str,
        path: list[str],
        data: dict[str, Any] | None = None,
        *,
        parse_json: bool = True,
        observe: bool = False,
        observe_duration: int = 0,
        process_result: TypeProcessResultCb = None,
        err_callback: TypeErrCb = None,
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
        self._raw_result: str | None = None
        self._result: str | None = None

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

    @property
    def process_result(self) -> TypeProcessResultCb:
        """Definition of callback to process result."""
        return self._process_result

    @property
    def err_callback(self) -> TypeErrCb:
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
    def raw_result(self) -> str | None:
        """Return raw result."""
        return self._raw_result

    @property
    def result(self) -> str | None:
        """Return result."""
        return self._result

    @result.setter
    def result(self, value: str) -> None:
        """Return command result."""
        if self._process_result:
            self._result = self._process_result(value)

        self._raw_result = value

    @property
    def path_str(self) -> str:
        """Return coap path."""
        return "/".join(str(v) for v in self._path)

    def url(self, host: str) -> str:
        """Generate url for coap client."""
        return f"coaps://{host}:5684/{self.path_str}"

    def _merge(
        self, a_dict: dict[str, Any] | None, b_dict: dict[str, Any] | None
    ) -> dict[str, Any] | None:
        """Merge a into b."""
        if a_dict is None or b_dict is None:
            return None
        for key, value in a_dict.items():
            if isinstance(value, dict):
                item = b_dict.setdefault(key, {})
                self._merge(value, item)
            elif isinstance(value, list):
                item = b_dict.setdefault(key, [{}])
                if len(value) == 1 and isinstance(value[0], dict):
                    self._merge(value[0], item[0])
                else:
                    b_dict[key] = value
            else:
                b_dict[key] = value
        return b_dict

    def combine_data(self, command2: Command | None) -> None:
        """Combine data for this command with another."""
        if command2 is None:
            return
        self._data = self._merge(
            command2._data, self._data  # pylint: disable=protected-access
        )

    def __add__(self, other: Command | None) -> Command:
        """Add Command to this Command."""
        if other is None:
            return deepcopy(self)
        if isinstance(other, self.__class__):
            new_obj = deepcopy(self)
            new_obj.combine_data(other)
            return new_obj
        msg = f"unsupported operand type(s) for '{self.__class__}' and '{type(other)}'"
        raise (TypeError(msg))

    def __repr__(self) -> str:
        """Return the representation."""
        if self.data is None:
            template = "<Command {} {}{}>"
        else:
            template = "<Command {} {}: {}>"
        return template.format(self.method, self.path, self.data or "")
