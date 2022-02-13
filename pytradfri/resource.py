"""Resources for devices."""
from __future__ import annotations

from abc import abstractmethod
from datetime import datetime
from typing import Any, Callable, Dict, List, Union

from .command import Command, TypeProcessResultCb
from .const import ATTR_NAME
from .type_hint import ApiResourceResponse

# type alias
TypeRaw = Dict[str, Union[str, int, List[Dict[str, Union[str, int]]]]]
TypeRawSimple = Dict[str, Union[str, int]]
TypeRawList = Dict[str, List[Dict[str, Union[str, int]]]]


class ApiResource:
    """Base object for resources returned from the gateway."""

    def __init__(self, raw: TypeRawList) -> None:
        """Initialize base object."""
        self.raw: ApiResourceResponse = ApiResourceResponse(**raw)

    @property
    def id(self) -> int | None:
        """Id."""
        return self.raw.id

    @property
    def name(self) -> str | None:
        """Name."""
        return self.raw.name

    @property
    def created_at(self) -> datetime | None:
        """Return timestamp of creation."""
        if self.raw.created_at:
            return datetime.utcfromtimestamp(self.raw.created_at)

        return None

    @property
    @abstractmethod
    def path(self) -> list[str]:
        """Path to resource."""

    def observe(
        self,
        callback: TypeProcessResultCb,
        err_callback: Callable[[Exception], None] | None,
        duration: int = 60,
    ) -> Command:
        """Observe resource and call callback when updated."""

        def observe_callback(value: ApiResourceResponse) -> None:
            """Call when end point is updated.

            Returns a Command.
            """
            self.raw = value
            if callback:
                callback(self)

        return Command(
            "get",
            self.path,
            process_result=observe_callback,
            err_callback=err_callback,
            observe=True,
            observe_duration=duration,
        )

    def set_name(self, name: str) -> Command:
        """Set group name."""
        return self.set_values({ATTR_NAME: name})

    def set_values(self, values: Any) -> Command:
        """Help to set values for group.

        Helper to set values for group.
        Returns a Command.
        """
        return Command("put", self.path, values)

    def update(self) -> Command:
        """
        Update the group.

        Returns a Command.
        """

        def process_result(result: ApiResourceResponse) -> None:
            self.raw = result

        return Command("get", self.path, process_result=process_result)
