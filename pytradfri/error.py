"""Errors for PyTradfri."""


class PyTradFriError(Exception):
    """Base Error"""
    pass


class RequestError(PyTradFriError):
    """An error happened sending or receiving a command."""
    pass


class ColorError(PyTradFriError):
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
