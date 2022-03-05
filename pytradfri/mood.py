"""Represent a mood on the gateway."""
from __future__ import annotations

from typing import cast

from .const import ROOT_MOODS
from .resource import ApiResource, TypeRaw


class Mood(ApiResource):
    """Mood."""

    def __init__(self, raw: TypeRaw, parent: str) -> None:
        """Create object of class."""
        super().__init__(raw)
        self._parent = parent

    @property
    def path(self) -> list[str]:
        """Path."""
        return [ROOT_MOODS, self._parent, cast(str, self.id)]

    def __repr__(self) -> str:
        """Return representation of class object."""
        return f"<Mood {self._parent} {self.name}>"
