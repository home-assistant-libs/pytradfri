"""Resources for devices."""
from __future__ import annotations

from abc import abstractmethod
from datetime import datetime
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .command import Command, TypeProcessResultCb
from .const import ATTR_CREATED_AT, ATTR_ID, ATTR_NAME, ATTR_OTA_UPDATE_STATE

if TYPE_CHECKING:
    from .group import GroupResponse

# type alias
TypeRaw = Dict[str, Union[str, int, List[Dict[str, Union[str, int]]]]]


class ApiResourceResponse(BaseModel):
    """Represent a resource response."""

    id: int = Field(alias=ATTR_ID)
    name: str = Field(alias=ATTR_NAME)
    created_at: Optional[int] = Field(alias=ATTR_CREATED_AT)
    ota_update_state: Optional[int] = Field(alias=ATTR_OTA_UPDATE_STATE)


class ApiResource:
    """Base object for resources returned from the gateway."""

    _model_class: type[ApiResourceResponse] | None = None
    raw: TypeRaw | ApiResourceResponse | GroupResponse

    def __init__(self, raw: TypeRaw) -> None:
        """Initialize base object."""
        if self._model_class:
            self.raw = self._model_class(**raw)
        else:
            self.raw = raw

    @property
    def id(self) -> int | None:
        """Id."""
        if self._model_class:
            resource_id = self.raw.id  # type: ignore[union-attr]
        else:
            resource_id = self.raw[ATTR_ID]  # type: ignore[index]
        return resource_id

    @property
    def name(self) -> str | None:
        """Name."""
        if self._model_class:
            name = self.raw.name  # type: ignore[union-attr]
        else:
            name = self.raw[ATTR_NAME]  # type: ignore[index]
        return name

    @property
    def created_at(self) -> datetime | None:
        """Return timestamp of creation."""
        if self._model_class:
            created_at = self.raw.created_at  # type: ignore[union-attr]
        else:
            created_at = self.raw[ATTR_CREATED_AT]  # type: ignore[index]

        if created_at is None:
            return None
        return datetime.utcfromtimestamp(created_at)

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

        def observe_callback(value: TypeRaw) -> None:
            """Call when end point is updated.

            Returns a Command.
            """
            if self._model_class:
                self.raw = self._model_class(**value)
            else:
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
            if self._model_class:
                self.raw = self._model_class(**result)
            else:
                self.raw = result

        return Command("get", self.path, process_result=process_result)
