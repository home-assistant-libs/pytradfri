"""Typing information."""
from typing import TypedDict

TypeDeviceInfo = TypedDict(
    # Alternative syntax required due to the need of using strings as keys:
    # https://www.python.org/dev/peps/pep-0589/#alternative-syntax
    "TypeDeviceInfo",
    {
        "0": str,  # Manufacturer
        "1": str,  # Model number
        "2": str,  # Serial number
        "3": str,  # Firmware version
        "6": int,  # Power source
        "7": int,  # Unknown, from air purifier
        "9": int,  # Battery level
    },
)
