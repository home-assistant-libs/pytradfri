"""Resources for devices."""
from datetime import datetime

from .command import Command
from .const import ATTR_CREATED_AT, ATTR_ID, ATTR_NAME


class ApiResource:
    """Base object for resources returned from the gateway."""

    def __init__(self, raw):
        """Initialize base object."""
        self.raw = raw

    @property
    def id(self):
        """Id."""
        return self.raw.get(ATTR_ID)

    @property
    def name(self):
        """Name."""
        return self.raw.get(ATTR_NAME)

    @property
    def created_at(self):
        """Return timestamp of creation."""
        if ATTR_CREATED_AT not in self.raw:
            return None
        return datetime.utcfromtimestamp(self.raw[ATTR_CREATED_AT])

    @property
    def path(self):
        """Path to resource."""
        raise NotImplementedError("Path property needs to be implemented")

    def observe(self, callback, err_callback, duration=60):
        """Observe resource and call callback when updated."""

        def observe_callback(value):
            """Call when end point is updated.

            Returns a Command.
            """
            self.raw = value
            callback(self)

        return Command(
            "get",
            self.path,
            process_result=observe_callback,
            err_callback=err_callback,
            observe=True,
            observe_duration=duration,
        )

    def set_name(self, name):
        """Set group name."""
        return self.set_values({ATTR_NAME: name})

    def set_values(self, values):
        """Help to set values for group.

        Returns a Command.
        """
        return Command("put", self.path, values)

    def update(self):
        """
        Update the group.

        Returns a Command.
        """

        def process_result(result):
            self.raw = result

        return Command("get", self.path, process_result=process_result)
