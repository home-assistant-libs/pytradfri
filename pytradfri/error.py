"""Errors for PyTradfri."""


class PytradfriError(Exception):
    """Base Error."""


class RequestError(PytradfriError):
    """An error happened sending or receiving a command."""


class ColorError(PytradfriError):
    """An error happened matching color name."""


class RequestTimeout(RequestError):
    """Error when sending or receiving the command timed out."""


class ClientError(RequestError):
    """Error when the client caused the error.

    See section 5.9.2 of draft-ietf-core-coap-04.
    """


class ServerError(RequestError):
    """Error when the server caused the error.

    See section 5.9.3 of draft-ietf-core-coap-04.
    """
