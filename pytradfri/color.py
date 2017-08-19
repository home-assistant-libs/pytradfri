from .const import (ATTR_LIGHT_COLOR_X as X, ATTR_LIGHT_COLOR_Y as Y)


KNOWN_XY = {
  2200: {X: 33135, Y: 27211},
  2700: {X: 30140, Y: 26909},
  4000: {X: 24930, Y: 24694},
}

KNOWN_KELVIN = KNOWN_XY.keys()

KNOWN_X = [v[X] for v in KNOWN_XY.values()]


def can_kelvin_to_xy(kelvins):
    return kelvins is not None and min(KNOWN_KELVIN) <= kelvins <= max(KNOWN_KELVIN)


def can_x_to_kelvin(x):
    return x is not None and min(KNOWN_X) <= x <= max(KNOWN_X)


def kelvin_to_xy(kelvins):
    if kelvins in KNOWN_XY:
        return KNOWN_XY[kelvins]
    else:
        lower_k = max([k for k in KNOWN_KELVIN if k < kelvins])
        higher_k = min([k for k in KNOWN_KELVIN if k > kelvins])
        offset = (kelvins - lower_k) / (higher_k - lower_k)
        lower = KNOWN_XY[lower_k]
        higher = KNOWN_XY[higher_k]
        return {
            coord: int(offset * higher[coord] + (1 - offset) * lower[coord])
            for coord in [X, Y]
        }


def x_to_kelvin(x):
    known = next((k for k, v in KNOWN_XY.items() if v[X] == x), None)
    if known is not None:
        return known
    else:
        lower_x = max([k for k in KNOWN_X if k < x])
        higher_x = min([k for k in KNOWN_X if k > x])
        lower = x_to_kelvin(lower_x)
        higher = x_to_kelvin(higher_x)
        offset = (x - lower_x) / (higher_x - lower_x)
        return int(offset * higher + (1 - offset) * lower)
