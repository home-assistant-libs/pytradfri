"""Resources for devices."""
from __future__ import annotations

from datetime import datetime
from typing import Union, cast, Callable, Any, Dict, List
from abc import abstractmethod

from .command import Command, TYPE_PROCESS_RESULT_CB, TYPE_ERR_CB
from .const import (
    ATTR_NAME,
    ATTR_CREATED_AT,
    ATTR_ID,
)

# type alias
TYPE_RAW = Dict[str, Union[str, int, List[Dict[str, Union[str, int]]]]]
TYPE_RAW_SIMPLE = Dict[str, Union[str, int]]
TYPE_RAW_LIST = Dict[str, List[Dict[str, Union[str, int]]]]


class ApiResource:
    """Base object for resources returned from the gateway."""

    def __init__(self, raw: TYPE_RAW) -> None:
        """Initialize base object."""
        self.raw = raw

    @property
    def id(self) -> str:
        """Id."""
        return str(self.raw.get(ATTR_ID))

    @property
    def name(self) -> str:
        """Name."""
        return str(self.raw.get(ATTR_NAME))

    @property
    def created_at(self) -> datetime | None:
        """Return timestamp of creation."""
        if ATTR_CREATED_AT not in self.raw:
            return None
        return datetime.utcfromtimestamp(
            int(cast(TYPE_RAW_SIMPLE, self.raw)[ATTR_CREATED_AT])
        )

    @abstractmethod
    @property
    def path(self) -> list[str]:
        """Path to resource."""
        raise NotImplementedError("Path property needs to be implemented")

    def observe(
        self,
        callback: TYPE_PROCESS_RESULT_CB,
        err_callback: TYPE_ERR_CB | None,
        duration: int = 60,
    ) -> Command:
        """Observe resource and call callback when updated."""

        def observe_callback(value: TYPE_RAW) -> None:
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

        def process_result(result: TYPE_RAW) -> None:
            self.raw = result

        return Command("get", self.path, process_result=process_result)
