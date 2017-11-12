from .const import (
    ATTR_LIGHT_COLOR_HEX,
    ATTR_LIGHT_COLOR_X as X,
    ATTR_LIGHT_COLOR_Y as Y,
    ATTR_LIGHT_COLOR_SATURATION,
    ATTR_LIGHT_COLOR_HUE,
    ATTR_LIGHT_DIMMER,
    ATTR_LIGHT_MIREDS,
    MIN_MIREDS,
    MAX_MIREDS,
    MIN_MIREDS_WS,
    MAX_MIREDS_WS,
    SUPPORT_BRIGHTNESS,
    SUPPORT_COLOR_TEMP,
    SUPPORT_HEX_COLOR,
    SUPPORT_RGB_COLOR,
    SUPPORT_XY_COLOR)

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


def kelvin_to_xyY(T, white_spectrum_bulb=False):
    # Only used locally to perform normalization of x, y values
    # Scaling to 65535 range and rounding
    def normalize_xy(x, y):
        return (int(x*65535+0.5), int(y*65535+0.5))

    min_kelvin = 1000000/MAX_MIREDS
    max_kelvin = 1000000/MIN_MIREDS
    min_kelvin_ws = 1000000/MAX_MIREDS_WS
    max_kelvin_ws = 1000000/MIN_MIREDS_WS

    # Sources: "Design of Advanced Color - Temperature Control System
    #           for HDTV Applications" [Lee, Cho, Kim]
    # and https://en.wikipedia.org/wiki/Planckian_locus#Approximation
    # and http://fcam.garage.maemo.org/apiDocs/_color_8cpp_source.html

    # Check for Kelvin range for which this function works
    if not (min_kelvin <= T <= max_kelvin):
        raise ValueError('Kelvin needs to be between {} and {}'.format(
            min_kelvin, max_kelvin))

    # Check for White-Spectrum kelvin range
    if white_spectrum_bulb and not (min_kelvin_ws <= T <= max_kelvin_ws):
        raise ValueError('Kelvin needs to be between {} and {} for '
                         'white spectrum bulbs'.format(
                          min_kelvin_ws, max_kelvin_ws))

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
