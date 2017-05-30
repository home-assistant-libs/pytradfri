"""Represent a mood on the gateway."""
from .const import ROOT_MOODS
from .resource import ApiResource


class Mood(ApiResource):
    def __init__(self, raw, parent):
        super().__init__(raw)
        self._parent = parent

    @property
    def path(self):
        return [ROOT_MOODS, self._parent, self.id]

    def __repr__(self):
        return '<Mood {}>'.format(self.name)
