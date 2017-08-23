from .const import (ATTR_LIGHT_COLOR_X as X, ATTR_LIGHT_COLOR_Y as Y)


MIN_KELVIN = 1667
MAX_KELVIN = 25000


def can_kelvin_to_xy(k):
    return MIN_KELVIN <= k <= MAX_KELVIN


# Scaling to 65535 range and rounding
def xy2tradfri(x, y):
    return (int(x*65535+0.5), int(y*65535+0.5))


def kelvin_to_xyY(T):
    # Sources: "Design of Advanced Color - Temperature Control System
    #           for HDTV Applications" [Lee, Cho, Kim]
    # and https://en.wikipedia.org/wiki/Planckian_locus#Approximation
    # and http://fcam.garage.maemo.org/apiDocs/_color_8cpp_source.html
    if not (1667 <= T <= 25000):
        return None

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


def xyY_to_kelvin(x, y):
    # This is an approximation, for information, see the source.
    # Source: https://en.wikipedia.org/wiki/Color_temperature#Approximation
    # Input range for x and y is 0-65535
    n = (x/65535-0.3320) / (y/65535-0.1858)
    kelvin = int((-449*n**3 + 3525*n**2 - 6823.3*n + 5520.33) + 0.5)
    return kelvin if MIN_KELVIN <= kelvin <= MAX_KELVIN else None


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
