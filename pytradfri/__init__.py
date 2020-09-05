"""Implement an API wrapper around Ikea Tradfri."""
from pathlib import Path

from .error import (
    PytradfriError,
    RequestError,
    ClientError,
    ServerError,
    RequestTimeout,
)
from .gateway import Gateway

__all__ = [
    "Gateway",
    "PytradfriError",
    "RequestError",
    "ClientError",
    "ServerError",
    "RequestTimeout",
]

__version__ = (Path(__file__).parent / "VERSION").read_text().strip()
