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
