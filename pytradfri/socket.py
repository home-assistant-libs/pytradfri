"""Control a socket device."""
from .command import Command
from .const import (
    ATTR_LIGHT_STATE,
    ATTR_SWITCH_PLUG,
)

class SocketControl:
    """Class to control the sockets."""

    def __init__(self, device):
        self._device = device

        self.can_combine_commands = None

    @property
    def raw(self):
        """Return raw data that it represents."""
        return self._device.raw[ATTR_SWITCH_PLUG]

    @property
    def sockets(self):
        """Return light objects of the light control."""
        return [Socket(self._device, i) for i in range(len(self.raw))]

    def set_state(self, state, *, index=0):
        """Set state of a light."""
        return self.set_values({
            ATTR_LIGHT_STATE: int(state)
        }, index=index)

    def set_values(self, values, *, index=0):
        """
        Set values on light control.
        Returns a Command.
        """
        assert len(self.raw) == 1, \
            'Only devices with 1 light supported'

        return Command('put', self._device.path, {
            ATTR_SWITCH_PLUG: [
                values
            ]
        })

    def __repr__(self):
        return '<SocketControl for {} ({} sockets)>'.format(self._device.name,
                                                            len(self.raw))


class Socket:
    """Represent a light.

    https://github.com/IPSO-Alliance/pub/blob/master/docs/IPSO-Smart-Objects.pdf
    """

    def __init__(self, device, index):
        self.device = device
        self.index = index

    @property
    def supported_features(self):
        return supported_features(self.raw)

    @property
    def state(self):
        return self.raw.get(ATTR_LIGHT_STATE) == 1

    @property
    def raw(self):
        """Return raw data that it represents."""
        return self.device.raw[ATTR_LIGHT_CONTROL][self.index]

    def __repr__(self):
        state = "on" if self.state else "off"
        return "<Light #{} - " \
               "name: {}, " \
               "state: {}, " \
               "dimmer: {}, "\
               "hex_color: {}, " \
               "xy_color: {}, " \
               "hsb_xy_color: {}, "\
               "supported features: {} " \
               ">".format(self.index, self.device.name, state, self.dimmer,
                          self.hex_color, self.xy_color,
                          self.hsb_xy_color, self.supported_features)
