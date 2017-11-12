from pytradfri.const import (
    ATTR_LIGHT_COLOR_X as X,
    ATTR_LIGHT_COLOR_Y as Y,
    ATTR_LIGHT_CONTROL,
    SUPPORT_BRIGHTNESS,
    SUPPORT_COLOR_TEMP,
    SUPPORT_HEX_COLOR,
    SUPPORT_RGB_COLOR,
    SUPPORT_XY_COLOR
    )
from pytradfri.color import xy_brightness_to_rgb,\
    supported_features, kelvin_to_xyY
import pytest
from devices import (
    LIGHT_W,
    LIGHT_WS,
    LIGHT_WS_CUSTOM_COLOR,
    LIGHT_CWS,
    LIGHT_CWS_CUSTOM_COLOR
    )


# Kelvin range for which the conversion functions work
# and that RGB bulbs can show
MIN_KELVIN = 1667
MAX_KELVIN = 25000

# Kelvin range that white-spectrum bulbs can actually show
MIN_KELVIN_WS = 2200
MAX_KELVIN_WS = 4000


def test_kelvin_to_xyY():
    # kelvin_to_xyY approximates, so +-50 is sufficiently precise.
    # Values taken from Tradfri App, these only differ slightly from online
    # calculators such as https://www.ledtuning.nl/en/cie-convertor

    warm = kelvin_to_xyY(2200)
    assert warm[X] in range(33135-50, 33135+51)
    assert warm[Y] in range(27211-50, 27211+51)

    normal = kelvin_to_xyY(2700)
    assert normal[X] in range(30140-50, 30140+51)
    assert normal[Y] in range(26909-50, 26909+51)

    cold = kelvin_to_xyY(4000)
    assert cold[X] in range(24930-50, 24930+51)
    assert cold[Y] in range(24694-50, 24694+51)

    cold = kelvin_to_xyY(25000)
    assert cold[X] in range(16546-50, 16546+51)
    assert cold[Y] in range(16546-50, 16546+51)

    with pytest.raises(ValueError):
        kelvin_to_xyY(99999)

    with pytest.raises(ValueError):
        kelvin_to_xyY(0, True)


def test_xy_brightness_to_rgb():
    # Converted to Python from Obj-C, original source from:
    # http://www.developers.meethue.com/documentation/color-conversions-rgb-xy
    rgb = xy_brightness_to_rgb(33135, 27211, 0)
    assert rgb == (0, 0, 0)

    rgb = xy_brightness_to_rgb(33135, 27211, 15)
    assert rgb == (119, 133, 0)


def test_supported_colors():
    assert supported_features(LIGHT_W[ATTR_LIGHT_CONTROL][0]) ==\
        SUPPORT_BRIGHTNESS

    assert supported_features(LIGHT_WS['3311'][0]) == SUPPORT_BRIGHTNESS\
        + SUPPORT_COLOR_TEMP + SUPPORT_HEX_COLOR + SUPPORT_XY_COLOR

    assert supported_features(LIGHT_WS_CUSTOM_COLOR['3311'][0]) ==\
        SUPPORT_BRIGHTNESS + SUPPORT_COLOR_TEMP + SUPPORT_HEX_COLOR + \
        SUPPORT_XY_COLOR

    assert supported_features(LIGHT_CWS['3311'][0]) ==\
        SUPPORT_BRIGHTNESS + SUPPORT_RGB_COLOR + SUPPORT_HEX_COLOR + \
        SUPPORT_XY_COLOR

    assert supported_features(LIGHT_CWS_CUSTOM_COLOR['3311'][0]) ==\
        SUPPORT_BRIGHTNESS + SUPPORT_RGB_COLOR + SUPPORT_HEX_COLOR + \
        SUPPORT_XY_COLOR
