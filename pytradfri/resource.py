from datetime import datetime

from .const import (
    ATTR_NAME,
    ATTR_CREATED_AT,
    ATTR_ID,
)


class ApiResource:
    """Base object for resources returned from the gateway."""

    def __init__(self, api, raw):
        """Initialize base object."""
        self.api = api
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

        self.api.observe(self.path, observe_callback, duration)

    def set_name(self, name):
        """Set group name."""
        self.set_values({
            ATTR_NAME: name
        })

    def set_values(self, values):
        """Helper to set values for group."""
        self.api('put', self.path, values)

    def update(self):
        """Update the group."""
        self.raw = self.api('get', self.path)
