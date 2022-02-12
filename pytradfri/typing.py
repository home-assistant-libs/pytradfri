"""
Type hints.

The TypedDict:s below uses an alternative syntax due to the need of using strings
as keys: https://www.python.org/dev/peps/pep-0589/#alternative-syntax
"""
from typing import List, TypedDict

TypeAirPurifier = TypedDict(
    "TypeAirPurifier",
    {
        "5900": int,  # Mode
        "5902": int,  # Filter runtume
        "5903": int,  # Filter status
        "5904": int,  # Filter lifetime total
        "5905": int,  # Manual controls locked
        "5906": int,  # Led light on/off
        "5907": int,  # Air quality level
        "5908": int,  # Fan speed
        "5909": int,  # Motor runtime total
        "5910": int,  # Filter lifetime remaining
        "9003": int,  # ID
    },
)

TypeBlind = TypedDict(
    "TypeBlind",
    {
        "5536": int,  # Current blind position
        "9003": int,  # ID
    },
)

TypeDeviceInfo = TypedDict(
    "TypeDeviceInfo",
    {
        "0": str,  # Manufacturer
        "1": str,  # Model number
        "2": str,  # Serial number
        "3": str,  # Firmware version
        "6": int,  # Power source
        "7": str,  # OTA image type
        "9": int,  # Battery level
    },
)


TypeApiResource = TypedDict(
    "TypeApiResource",
    {
        "9001": str,  # Name
        "9002": int,  # Created at
        "9003": str,  # ID
        "3": TypeDeviceInfo,
        "15025": List[TypeAirPurifier],
        "15015": List[TypeBlind],
    },
)
