from .const import (ATTR_LIGHT_COLOR_X as X, ATTR_LIGHT_COLOR_Y as Y)


# Kelvin range for which the conversion functions work
# and that RGB bulbs can show
MIN_KELVIN = 1667
MAX_KELVIN = 25000

# Kelvin range that white-spectrum bulbs can actually show
MIN_KELVIN_WS = 2200
MAX_KELVIN_WS = 4000

# Extracted from Tradfri Android App string.xml
COLOR_NAMES = {
    '4a418a': 'Blue',
    '6c83ba': 'Light Blue',
    '8f2686': 'Saturated Purple',
    'a9d62b': 'Lime',
    'c984bb': 'Light Purple',
    'd6e44b': 'Yellow',
    'd9337c': 'Saturated Pink',
    'da5d41': 'Dark Peach',
    'dc4b31': 'Saturated Red',
    'dcf0f8': 'Cold sky',
    'e491af': 'Pink',
    'e57345': 'Peach',
    'e78834': 'Warm Amber',
    'e8bedd': 'Light Pink',
    'eaf6fb': 'Cool daylight',
    'ebb63e': 'Candlelight',
    'efd275': 'Warm glow',
    'f1e0b5': 'Warm white',
    'f2eccf': 'Sunrise',
    'f5faf6': 'Cool white'
}
# When setting colors by name via the API,
# lowercase strings with no spaces are preferred
COLORS = {name.lower().replace(" ", "_"): hex
          for hex, name in COLOR_NAMES.items()}


def can_kelvin_to_xy(k):
    return MIN_KELVIN <= k <= MAX_KELVIN


# Only used locally to perform normalization of x, y values
# Scaling to 65535 range and rounding
def normalize_xy(x, y):
    return (int(x*65535+0.5), int(y*65535+0.5))


def kelvin_to_xyY(T, white_spectrum_bulb=False):
    # Sources: "Design of Advanced Color - Temperature Control System
    #           for HDTV Applications" [Lee, Cho, Kim]
    # and https://en.wikipedia.org/wiki/Planckian_locus#Approximation
    # and http://fcam.garage.maemo.org/apiDocs/_color_8cpp_source.html

    # Check for Kelvin range for which this function works
    if not (MIN_KELVIN <= T <= MAX_KELVIN):
        raise ValueError('Kelvin needs to be between {} and {}'.format(
            MIN_KELVIN, MAX_KELVIN))

    # Check for White-Spectrum kelvin range
    if white_spectrum_bulb and not (MIN_KELVIN_WS <= T <= MAX_KELVIN_WS):
        raise ValueError('Kelvin needs to be between {} and {} for '
                         'white spectrum bulbs'.format(
                          MIN_KELVIN_WS, MAX_KELVIN_WS))

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

    x, y = normalize_xy(x, y)
    return {X: x, Y: y}


def xyY_to_kelvin(x, y):
    # This is an approximation, for information, see the source.
    # Source: https://en.wikipedia.org/wiki/Color_temperature#Approximation
    # Input range for x and y is 0-65535
    n = (x/65535-0.3320) / (y/65535-0.1858)
    kelvin = int((-449*n**3 + 3525*n**2 - 6823.3*n + 5520.33) + 0.5)
    return kelvin


def rgb2xyzA(r, g, b):
    # Uses CIE standard illuminant A = 2856K
    # src: http://www.brucelindbloom.com/index.html?Eqn_RGB_XYZ_Matrix.html
    # calculation https://gist.github.com/r41d/43e14df2ccaeca56d32796efd6584b48
    X = 0.76103282*r + 0.29537849*g + 0.04208869*b
    Y = 0.39240755*r + 0.59075697*g + 0.01683548*b
    Z = 0.03567341*r + 0.0984595*g + 0.22166709*b
    return X, Y, Z


def rgb2xyzD65(r, g, b):
    # Uses CIE standard illuminant D65 = 6504K
    # src: http://www.brucelindbloom.com/index.html?Eqn_RGB_XYZ_Matrix.html
    X = 0.4124564 * r + 0.3575761 * g + 0.1804375 * b
    Y = 0.2126729 * r + 0.7151522 * g + 0.0721750 * b
    Z = 0.0193339 * r + 0.1191920 * g + 0.9503041 * b
    return X, Y, Z


def xyz2xyY(X, Y, Z):
    total = X + Y + Z
    return (0, 0) if total == 0 else normalize_xy(X / total, Y / total)


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

    x, y = xyz2xyY(*rgb2xyzA(r, g, b))
    return {X: x, Y: y}


# Converted to Python from Obj-C, original source from:
# http://www.developers.meethue.com/documentation/color-conversions-rgb-xy
# pylint: disable=invalid-sequence-index
def xy_brightness_to_rgb(vX: float, vY: float, ibrightness: int):
    """Convert from XYZ to RGB."""
    brightness = ibrightness / 255.
    if brightness == 0:
        return (0, 0, 0)
    Y = brightness
    if vY == 0:
        vY += 0.00000000001
    X = (Y / vY) * vX
    Z = (Y / vY) * (1 - vX - vY)
    # Convert to RGB using Wide RGB D65 conversion.
    r = X * 1.656492 - Y * 0.354851 - Z * 0.255038
    g = -X * 0.707196 + Y * 1.655397 + Z * 0.036152
    b = X * 0.051713 - Y * 0.121364 + Z * 1.011530
    # Apply reverse gamma correction.
    r, g, b = map(
        lambda x: (12.92 * x) if (x <= 0.0031308) else
        ((1.0 + 0.055) * pow(x, (1.0 / 2.4)) - 0.055),
        [r, g, b]
    )
    # Bring all negative components to zero.
    r, g, b = map(lambda x: max(0, x), [r, g, b])
    # If one component is greater than 1, weight components by that value.
    max_component = max(r, g, b)
    if max_component > 1:
        r, g, b = map(lambda x: x / max_component, [r, g, b])
    ir, ig, ib = map(lambda x: int(x * 255), [r, g, b])
    return (ir, ig, ib)
