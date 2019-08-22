"""Class to control the blinds."""


class BlindControl:
    """Class to control the sockets."""

    def __init__(self, device):
        self._device = device

    @property
    def raw(self):
        """Return raw data that it represents."""
        return self._device.raw

    def __repr__(self):
        return '<BlindControl for {} ({} blinds)>'.format(self._device.name,
                                                          len(self.raw))
