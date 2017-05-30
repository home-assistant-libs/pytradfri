from datetime import datetime

from pytradfri.command import Command
from .const import (
    ATTR_NAME,
    ATTR_CREATED_AT,
    ATTR_ID,
)


class ApiResource:
    """Base object for resources returned from the gateway."""

    def __init__(self, raw):
        """Initialize base object."""
        self.raw = raw

    @property
    def id(self):
        return self.raw.get(ATTR_ID)

    @property
    def name(self):
        return self.raw.get(ATTR_NAME)

    @property
    def created_at(self):
        if ATTR_CREATED_AT not in self.raw:
            return None
        return datetime.utcfromtimestamp(self.raw[ATTR_CREATED_AT])

    @property
    def path(self):
        """Path to resource."""
        raise NotImplemented('Path property needs to be implemented')

    def observe(self, callback, duration=60):
        """Observe resource and call callback when updated."""
        def observe_callback(value):
            """Called when end point is updated."""
            self.raw = value
            callback(self)

        return Command('get', self.path, callback=observe_callback,
                       observe_duration=duration)

    def set_name(self, name):
        """Set group name."""
        return self.set_values({
            ATTR_NAME: name
        })

    def set_values(self, values):
        """Helper to set values for group."""
        return Command('put', self.path, values)

    def update(self):
        """Update the group."""
        def callback(result):
            self.raw = result
        Command('get', self.path, callback=callback)
