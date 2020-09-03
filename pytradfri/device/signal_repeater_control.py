"""Class to control the signal repeater."""
from pytradfri.const import ROOT_SIGNAL_REPEATER
from pytradfri.device.signal_repeater import SignalRepeater


class SignalRepeaterControl:
    """Class to control the signal repeaters."""

    def __init__(self, device):
        self._device = device

    @property
    def raw(self):
        """Return raw data that it represents."""
        return self._device.raw[ROOT_SIGNAL_REPEATER]

    @property
    def signal_repeaters(self):
        """Return signal repeater objects of the signal repeater control."""
        return [SignalRepeater(self._device, i) for i in range(len(self.raw))]

    def __repr__(self):
        return "<SignalRepeaterControl for {} ({} signal repeaters)>".format(
            self._device.name, len(self.raw)
        )
