from pytradfri.device import Device
from devices import (
    BLIND
)


def socket(raw):
    return Device(raw).blind_control.blinds[0]


def test_blind():
    blind = socket(BLIND)

    print(blind.raw)
