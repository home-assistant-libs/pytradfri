import math
from .const import (ATTR_LIGHT_COLOR_X as X, ATTR_LIGHT_COLOR_Y as Y)


KNOWN_XY = {
  2200: {X: 33135, Y: 27211},
  2700: {X: 30140, Y: 26909},
  4000: {X: 24930, Y: 24694},
}
KNOWN_KELVIN = KNOWN_XY.keys()
KNOWN_X = [v[X] for v in KNOWN_XY.values()]
MIN_KELVIN = min(KNOWN_KELVIN)
MAX_KELVIN = max(KNOWN_KELVIN)
MIN_X = min(KNOWN_X)
MAX_X = max(KNOWN_X)


def can_kelvin_to_xy(k):
    return MIN_KELVIN <= k <= MAX_KELVIN


def can_x_to_kelvin(x):
    return MIN_X <= x <= MAX_X


def kelvin_to_xy(k):
    if k in KNOWN_XY:
        return KNOWN_XY[k]
    lower_k = max(kk for kk in KNOWN_KELVIN if kk < k)
    higher_k = min(kk for kk in KNOWN_KELVIN if kk > k)
    offset = (k - lower_k) / (higher_k - lower_k)
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
    lower_x = max(k for k in KNOWN_X if k < x)
    higher_x = min(k for k in KNOWN_X if k > x)
    lower = x_to_kelvin(lower_x)
    higher = x_to_kelvin(higher_x)
    offset = (x - lower_x) / (higher_x - lower_x)
    return int(offset * higher + (1 - offset) * lower)


def rgb_to_xyY(r, g, b):
    # According to http://www.brucelindbloom.com/index.html?Eqn_RGB_to_XYZ.html
    # and http://www.brucelindbloom.com/index.html?Eqn_XYZ_to_xyY.html
    companding = lambda x: x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4
    prepare = lambda x: companding(max(min(x,255),0) / 255.0)
    r, g, b = map(prepare, (r, g, b))

    # sRGB D65 matrix from http://www.brucelindbloom.com/index.html?Eqn_RGB_XYZ_Matrix.html
    CIE_X = 0.4124564*r + 0.3575761*g + 0.1804375*b
    CIE_Y = 0.2126729*r + 0.7151522*g + 0.0721750*b
    CIE_Z = 0.0193339*r + 0.1191920*g + 0.9503041*b
    CIE_sum = CIE_X + CIE_Y + CIE_Z

    (x, y) = (0, 0) if CIE_sum == 0 else (CIE_X / CIE_sum * 65535, CIE_Y / CIE_sum * 65535)

    return { X: x, Y: y }
