"""Base class for a controller."""


class Controller:
    """Represent a controller."""

    def _value_validate(self, value, rnge, identifier="Given"):
        """
        Make sure a value is within a given range
        """
        if value is not None and (value < rnge[0] or value > rnge[1]):
            raise ValueError(
                "%s value must be between %d and %d." % (identifier, rnge[0], rnge[1])
            )
