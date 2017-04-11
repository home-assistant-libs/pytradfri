"""Errors for PyTradfri."""


class PyTradFriError(Exception):
    """Base Error"""
    pass


class CommandError(PyTradFriError):
    """An error happened sending or receiving a command."""
    pass


class NotFoundError(CommandError):
    """Command returned a not found error."""
    pass
