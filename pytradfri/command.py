"""Command implementation."""
from __future__ import annotations

from copy import deepcopy
from typing import Any, Optional, Callable

TYPE_PROCESS_RESULT_CB = Optional[Callable[[Any], Optional[str]]]
TYPE_ERR_CB = Optional[Callable[[str], str]]


class Command(object):
    """The object for coap commands."""

    def __init__(
        self,
        method: str,
        path: list[str],
        data: Optional[dict[str, Any]] = None,
        *,
        parse_json: bool = True,
        observe: bool = False,
        observe_duration: int = 0,
        process_result: TYPE_PROCESS_RESULT_CB = None,
        err_callback: TYPE_ERR_CB = None
    ) -> None:
        self._method = method
        self._path = path
        self._data = data
        self._parse_json = parse_json
        self._process_result = process_result
        self._err_callback = err_callback
        self._observe = observe
        self._observe_duration = observe_duration
        self._raw_result: Optional[str] = None
        self._result: Optional[str] = None

    @property
    def method(self) -> str:
        return self._method

    @property
    def path(self) -> list[str]:
        return self._path

    @property
    def data(self) -> Optional[dict[str, Any]]:
        return self._data

    @property
    def parse_json(self) -> bool:
        return self._parse_json

    @property
    def process_result(self) -> TYPE_PROCESS_RESULT_CB:
        return self._process_result

    @property
    def err_callback(self) -> TYPE_ERR_CB:
        """This will be fired when an observe request fails."""
        return self._err_callback

    @property
    def observe(self) -> bool:
        return self._observe

    @property
    def observe_duration(self) -> int:
        return self._observe_duration

    @property
    def raw_result(self) -> Optional[str]:
        return self._raw_result

    @property
    def result(self) -> Optional[str]:
        return self._result

    @result.setter
    def result(self, value: str) -> None:
        """The result of the command."""
        if self._process_result:
            self._result = self._process_result(value)

        self._raw_result = value

    @property
    def path_str(self) -> str:
        """Return coap path."""
        return "/".join(str(v) for v in self._path)

    def url(self, host: str) -> str:
        """Generate url for coap client."""
        return "coaps://{}:5684/{}".format(host, self.path_str)

    def _merge(
        self, a: Optional[dict[str, Any]], b: Optional[dict[str, Any]]
    ) -> Optional[dict[str, Any]]:
        """Merges a into b."""
        if a is None or b is None:
            return None
        for k, v in a.items():
            if isinstance(v, dict):
                item = b.setdefault(k, {})
                self._merge(v, item)
            elif isinstance(v, list):
                item = b.setdefault(k, [{}])
                if len(v) == 1 and isinstance(v[0], dict):
                    self._merge(v[0], item[0])
                else:
                    b[k] = v
            else:
                b[k] = v
        return b

    def combine_data(self, command2: Optional[Command]) -> None:
        """Combines the data for this command with another."""
        if command2 is None:
            return
        self._data = self._merge(command2._data, self._data)

    def __add__(self, other: Optional[Command]) -> Command:
        if other is None:
            return deepcopy(self)
        if isinstance(other, self.__class__):
            newObj = deepcopy(self)
            newObj.combine_data(other)
            return newObj
        else:
            raise (
                TypeError(
                    "unsupported operand type(s) for +: "
                    "'{}' and '{}'".format(self.__class__, type(other))
                )
            )

    def __repr__(self) -> str:
        """Return the representation."""
        if self.data is None:
            template = "<Command {} {}{}>"
        else:
            template = "<Command {} {}: {}>"
        return template.format(self.method, self.path, self.data or "")
