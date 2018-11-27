"""Errors for PyTradfri."""


class PytradfriError(Exception):
    """Base Error"""
    pass


class RequestError(PytradfriError):
    """An error happened sending or receiving a command."""
    pass


class ColorError(PytradfriError):
    """An error happened matching color name."""
    pass


class RequestTimeout(RequestError):
    """Error when sending or receiving the command timed out."""
    pass


class ClientError(RequestError):
    """Error when the client caused the error.

    See section 5.9.2 of draft-ietf-core-coap-04.
    """
    pass


class ServerError(RequestError):
    """Error when the server caused the error.

    See section 5.9.3 of draft-ietf-core-coap-04.
    """
    pass


class ObservationError():
    """Error when the observation got stuck.

    This can happen with indefinate observations which can get stuck after
    some time.
    """
    pass
