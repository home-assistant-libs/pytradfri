"""Resources for devices."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Union, cast

from .command import Command, TypeErrCb, TypeProcessResultCb
from .const import ATTR_CREATED_AT, ATTR_ID, ATTR_NAME

# type alias
TypeRaw = Dict[str, Union[str, int, List[Dict[str, Union[str, int]]]]]
TypeRawSimple = Dict[str, Union[str, int]]
TypeRawList = Dict[str, List[Dict[str, Union[str, int]]]]


class ApiResource:
    """Base object for resources returned from the gateway."""

    def __init__(self, raw: TypeRaw) -> None:
        """Initialize base object."""
        self.raw = raw

    @property
    def id(self) -> str | None:
        """Id."""
        return cast(Union[str, None], self.raw.get(ATTR_ID))

    @property
    def name(self) -> str | None:
        """Name."""
        return cast(Union[str, None], self.raw.get(ATTR_NAME))

    @property
    def created_at(self) -> datetime | None:
        """Return timestamp of creation."""
        if ATTR_CREATED_AT not in self.raw:
            return None
        return datetime.utcfromtimestamp(
            int(cast(TypeRawSimple, self.raw)[ATTR_CREATED_AT])
        )

    @property
    def path(self) -> list[str]:
        """Path to resource."""
        raise NotImplementedError("Path property needs to be implemented")

    def observe(
        self,
        callback: TypeProcessResultCb,
        err_callback: TypeErrCb | None,
        duration: int = 60,
    ) -> Command:
        """Observe resource and call callback when updated."""

        def observe_callback(value: TypeRaw) -> None:
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

        def process_result(result: TypeRaw) -> None:
            self.raw = result

        return Command("get", self.path, process_result=process_result)
