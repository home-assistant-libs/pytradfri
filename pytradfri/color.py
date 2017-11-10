from .const import (
    ATTR_LIGHT_COLOR_HEX,
    ATTR_LIGHT_COLOR_X as X,
    ATTR_LIGHT_COLOR_Y as Y,
    ATTR_LIGHT_COLOR_SATURATION,
    ATTR_LIGHT_COLOR_HUE,
    ATTR_LIGHT_DIMMER,
    ATTR_LIGHT_MIREDS,
    SUPPORT_BRIGHTNESS,
    SUPPORT_COLOR_TEMP,
    SUPPORT_HEX_COLOR,
    SUPPORT_RGB_COLOR,
    SUPPORT_XY_COLOR)

import math

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

#  http://www.brucelindbloom.com/index.html?Eqn_RGB_XYZ_Matrix.html
M_CIE_RGB = [
            [0.4887180, 0.3106803, 0.2006017],
            [0.1762044, 0.8129847, 0.0108109],
            [0.0000000, 0.0102048, 0.9897952]]

M_CIE_RGB_I = [
              [2.3706743, -0.9000405, -0.4706338],
              [-0.5138850, 1.4253036, 0.0885814],
              [0.0052982, -0.0146949, 1.0093968]]

M_S_RGB = [
          [0.4123866,  0.3575915,  0.1804505],
          [0.2126368,  0.7151830,  0.0721802],
          [0.0193306,  0.1191972,  0.9503726]]

M_S_RGB_I = [
            [3.2404542 , -1.5371385,-0.4985314],
            [-0.9692660,  1.8760108, 0.0415560],
            [0.0556434 , -0.2040259, 1.0572252]]

WIDE_GAMUT_RGB = [
                 [0.6016556, 0.2241551, 0.1246452],
                 [0.2423106, 0.8242476, -0.0665581],
                 [-0.0197805, -0.0432227, 1.1520609]]

WIDE_GAMUT_RGB_I = [
                   [1.8634534, -0.5189129, -0.2315923],
                   [-0.5468874, 1.3692053, 0.1382728],
                   [0.0114768, -0.0424600, 0.8692210]]

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


def colorGammaAdjust(component):
    if component > 0.04045:
        return(math.pow((component + 0.055) / (1.0 + 0.055),
               2.4))
    else:
        return(component / 12.92)


def rgb_to_xy(r, g, b):
    # Based on this transformation
    # https://github.com/puzzle-star/SmartThings-IKEA-Tradfri-RGB/blob/master/ikea-tradfri-rgb.groovy

    #  Use one of the constants from above
    M = WIDE_GAMUT_RGB

    vX = r * M[0][0] + g * M[0][1] + b * M[0][2]
    vY = r * M[1][0] + g * M[1][1] + b * M[1][2]
    vZ = r * M[2][0] + g * M[2][1] + b * M[2][2]

    x = vX / (vX + vY + vZ)
    y = vY / (vX + vY + vZ)

    return {X: int(x*65536), Y: int(y*65536)}


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

    M = WIDE_GAMUT_RGB_I

    r = X * M[0][0] + Y * M[0][1] + Z * M[0][2]
    g = X * M[1][0] + Y * M[1][1] + Z * M[1][2]
    b = X * M[2][0] + Y * M[2][1] + Z * M[2][2]

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


# https://stackoverflow.com/questions/29643352/converting-hex-to-rgb-value-in-python
def hex_to_rgb(hex):
    return tuple(int(hex[i:i+2], 16) for i in (0, 2, 4))


def supported_features(data):
    SUPPORTED_COLOR_FEATURES = 0

    if ATTR_LIGHT_DIMMER in data:
        SUPPORTED_COLOR_FEATURES = SUPPORTED_COLOR_FEATURES\
            + SUPPORT_BRIGHTNESS

    if ATTR_LIGHT_COLOR_HEX in data:
        SUPPORTED_COLOR_FEATURES = SUPPORTED_COLOR_FEATURES\
            + SUPPORT_HEX_COLOR

    if ATTR_LIGHT_MIREDS in data:
        SUPPORTED_COLOR_FEATURES = SUPPORTED_COLOR_FEATURES\
            + SUPPORT_COLOR_TEMP

    if X in data and Y in data:
            SUPPORTED_COLOR_FEATURES = SUPPORTED_COLOR_FEATURES\
                + SUPPORT_XY_COLOR

    if ATTR_LIGHT_MIREDS not in data and X in data and Y in data and \
            ATTR_LIGHT_COLOR_SATURATION in data and ATTR_LIGHT_COLOR_HUE\
            in data:
            SUPPORTED_COLOR_FEATURES = SUPPORTED_COLOR_FEATURES\
                + SUPPORT_RGB_COLOR

    return SUPPORTED_COLOR_FEATURES
