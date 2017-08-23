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


# Scaling to 65535 range and rounding
def xy2tradfri(x, y):
    return (int(x*65535+0.5), int(y*65535+0.5))


def kelvin_to_xyY(T):
    # Sources: "Design of Advanced Color - Temperature Control System
    #           for HDTV Applications" [Lee, Cho, Kim]
    # and https://en.wikipedia.org/wiki/Planckian_locus#Approximation
    # and http://fcam.garage.maemo.org/apiDocs/_color_8cpp_source.html
    if not (1667 <= T <= 25000):
        return None, None

    if T <= 4000:
        # One number differs on Wikipedia and the paper:
        #     0.2343589 is 0.2343580 on Wikipedia... don't know why
        x = -0.2661239*(10**9)/T**3 - 0.2343589*(10**6)/T**2 \
            + 0.8776956*(10**3)/T + 0.17991
    elif T <= 25000:
        x = -3.0258469*(10**9)/T**3 + 2.1070379*(10**6)/T**2 \
            + 0.2226347*(10**3)/T + 0.24039

    if T <= 2222:
        y = -1.1063814*x**3 - 1.3481102*x**2 + 2.18555832*x - 0.20219683
    elif T <= 4000:
        y = -0.9549476*x**3 - 1.37418593*x**2 + 2.09137015*x - 0.16748867
    elif T <= 25000:
        y = 3.081758*x**3 - 5.8733867*x**2 + 3.75112997*x - 0.37001483

    x, y = xy2tradfri(x, y)
    return {X: x, Y: y}


def rgb_to_xyY(r, g, b):
    # According to http://www.brucelindbloom.com/index.html?Eqn_RGB_to_XYZ.html
    # and http://www.brucelindbloom.com/index.html?Eqn_XYZ_to_xyY.html
    def prepare(val):
        val = max(min(val, 255), 0) / 255.0
        if val <= 0.04045:
            return val / 12.92
        else:
            return ((val + 0.055) / 1.055) ** 2.4
    r, g, b = map(prepare, (r, g, b))

    # source: http://www.brucelindbloom.com/index.html?Eqn_RGB_XYZ_Matrix.html
    CIE_X = 0.4124564*r + 0.3575761*g + 0.1804375*b
    CIE_Y = 0.2126729*r + 0.7151522*g + 0.0721750*b
    CIE_Z = 0.0193339*r + 0.1191920*g + 0.9503041*b
    CIE_sum = CIE_X + CIE_Y + CIE_Z

    (x, y) = (0, 0) if CIE_sum == 0 else \
        xy2tradfri(CIE_X / CIE_sum, CIE_Y / CIE_sum)
    return {X: x, Y: y}
