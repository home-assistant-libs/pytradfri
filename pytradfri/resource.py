"""Resources for devices."""
from __future__ import annotations

from abc import abstractmethod
from collections.abc import Callable
from datetime import datetime
from typing import Any, Optional, Union

from pydantic import BaseModel, Field

from .command import Command
from .const import ATTR_CREATED_AT, ATTR_ID, ATTR_NAME, ATTR_OTA_UPDATE_STATE

# type alias
TypeRaw = dict[str, Union[str, int, list[dict[str, Union[str, int]]]]]


class BaseResponse(BaseModel):
    """Represent API base response."""

    id: int = Field(alias=ATTR_ID)


class ApiResourceResponse(BaseResponse):
    """Represent a resource response."""

    name: Optional[str] = Field(alias=ATTR_NAME)
    created_at: Optional[int] = Field(alias=ATTR_CREATED_AT)
    ota_update_state: Optional[int] = Field(alias=ATTR_OTA_UPDATE_STATE)


class ApiResource:
    """Base object for resources returned from the gateway."""

    _model_class: type[ApiResourceResponse] = ApiResourceResponse
    raw: ApiResourceResponse

    def __init__(self, raw: TypeRaw) -> None:
        """Initialize base object."""
        self.raw = self._model_class(**raw)

    @property
    def id(self) -> int:
        """Id."""
        return self.raw.id

    @property
    def name(self) -> str | None:
        """Name."""
        return self.raw.name

    @property
    def created_at(self) -> datetime | None:
        """Return timestamp of creation."""
        created_at = self.raw.created_at

        if created_at is None:
            return None
        return datetime.utcfromtimestamp(created_at)

    @property
    @abstractmethod
    def path(self) -> list[str]:
        """Path to resource."""

    def observe(
        self,
        callback: Callable[[ApiResource], None] | None,
        err_callback: Callable[[Exception], None] | None,
        duration: int = 60,
    ) -> Command[None]:
        """Observe resource and call callback when updated."""

        def observe_callback(value: TypeRaw) -> None:
            """Call when end point is updated.

            Returns a Command.
            """
            self.raw = self._model_class(**value)

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

    def set_name(self, name: str) -> Command[None]:
        """Set group name."""
        return self.set_values({ATTR_NAME: name})

    def set_values(self, values: Any) -> Command[None]:
        """Help to set values for group.

        Helper to set values for group.
        Returns a Command.
        """
        return Command("put", self.path, values)

    def update(self) -> Command[None]:
        """
        Update the group.

        Returns a Command.
        """

        def process_result(result: TypeRaw) -> None:
            self.raw = self._model_class(**result)

        return Command("get", self.path, process_result=process_result)
