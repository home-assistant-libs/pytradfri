"""Errors for PyTradfri."""


class PyTradFriError(Exception):
    """Base Error"""
    pass


class CommandError(PyTradFriError):
    """An error happened sending or receiving a command."""
    pass


class ClientError(CommandError):
    """Error when the client caused the error.

    See section 5.9.2 of draft-ietf-core-coap-04.
    """
    pass


class ServerError(CommandError):
    """Error when the server caused the error.

    See section 5.9.3 of draft-ietf-core-coap-04.
    """
    pass
