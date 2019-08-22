"""Class to control the blinds."""
from pytradfri.const import ATTR_SWITCH_PLUG
from pytradfri.device.blind import Blind


class BlindControl:
    """Class to control the sockets."""

    def __init__(self, device):
        self._device = device

    @property
    def raw(self):
        """Return raw data that it represents."""
        return self._device.raw[ATTR_SWITCH_PLUG]

    @property
    def blinds(self):
        """Return socket objects of the socket control."""
        return [Blind(self._device, i) for i in range(len(self.raw))]

    def __repr__(self):
        return '<SocketControl for {} ({} blinds)>'.format(self._device.name,
                                                           len(self.raw))
