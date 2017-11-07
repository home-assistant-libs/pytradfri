from pytradfri.const import (
    ATTR_LIGHT_COLOR_X as X,
    ATTR_LIGHT_COLOR_Y as Y,
    ATTR_LIGHT_CONTROL,
    SUPPORT_BRIGHTNESS,
    SUPPORT_COLOR_TEMP,
    SUPPORT_HEX_COLOR,
    SUPPORT_RGB_COLOR,
    #  SUPPORT_XY_COLOR
    )
from pytradfri.color import can_kelvin_to_xy, kelvin_to_xyY, xyY_to_kelvin, \
    rgb_to_xyY, rgb2xyzD65, xy_brightness_to_rgb, supported_color_features
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


def test_can_dekelvinize():
    assert can_kelvin_to_xy(1600) is False
    assert can_kelvin_to_xy(1800) is True
    assert can_kelvin_to_xy(2000) is True
    assert can_kelvin_to_xy(2200) is True
    assert can_kelvin_to_xy(2400) is True
    assert can_kelvin_to_xy(2700) is True
    assert can_kelvin_to_xy(3000) is True
    assert can_kelvin_to_xy(4000) is True
    assert can_kelvin_to_xy(5000) is True
    assert can_kelvin_to_xy(25000) is True
    assert can_kelvin_to_xy(26000) is False


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


def test_xyY_to_kelvin():
    # xyY_to_kelvin approximates, so +-20 is sufficiently precise.
    # Values taken from Tradfri App.
    warm = xyY_to_kelvin(33135, 27211)
    assert warm in range(2200-20, 2200+21)

    normal = xyY_to_kelvin(30140, 26909)
    assert normal in range(2700-20, 2700+21)

    cold = xyY_to_kelvin(24930, 24694)
    assert cold in range(4000-20, 4000+21)


def test_rgb_to_xyY():
    # rgb_to_xyY approximates, so +-50 is sufficiently precise.
    # Verification values calculated by http://colormine.org/convert/rgb-to-xyz

    red = rgb_to_xyY(255, 0, 0)
    assert red[X] in range(41947-50, 41947+51)
    assert red[Y] in range(21625-50, 21625+51)

    green = rgb_to_xyY(0, 255, 0)
    assert green[X] in range(19661-50, 19661+51)
    assert green[Y] in range(39321-50, 39321+51)

    blue = rgb_to_xyY(0, 0, 255)
    assert blue[X] in range(9831-50, 9831+51)
    assert blue[Y] in range(3933-50, 3933+51)


def test_rgb_to_xyzD65():
    # Uses CIE standard illuminant A = 2856K
    # src: http://www.brucelindbloom.com/index.html?Eqn_RGB_XYZ_Matrix.html
    # calculation https://gist.github.com/r41d/43e14df2ccaeca56d32796efd6584b48

    red = rgb2xyzD65(255, 0, 0)
    assert round(red[0], 4) == 105.1764
    assert round(red[1], 4) == 54.2316
    assert round(red[2], 4) == 4.9301

    green = rgb2xyzD65(0, 255, 0)
    assert round(green[0], 4) == 91.1819
    assert round(green[1], 4) == 182.3638
    assert round(green[2], 4) == 30.394

    blue = rgb2xyzD65(0, 0, 255)
    assert round(blue[0], 4) == 46.0116
    assert round(blue[1], 4) == 18.4046
    assert round(blue[2], 4) == 242.3275


def test_xy_brightness_to_rgb():
    # Converted to Python from Obj-C, original source from:
    # http://www.developers.meethue.com/documentation/color-conversions-rgb-xy
    rgb = xy_brightness_to_rgb(33135, 27211, 0)
    assert rgb == (0, 0, 0)

    rgb = xy_brightness_to_rgb(33135, 27211, 15)
    assert rgb == (101, 57, 0)


def test_supported_colors():
    print(LIGHT_W[ATTR_LIGHT_CONTROL][0])
    assert supported_color_features(LIGHT_W[ATTR_LIGHT_CONTROL][0]) ==\
        SUPPORT_BRIGHTNESS
    assert supported_color_features(LIGHT_WS['3311'][0]) == SUPPORT_BRIGHTNESS\
        + SUPPORT_COLOR_TEMP + SUPPORT_HEX_COLOR
    assert supported_color_features(LIGHT_WS_CUSTOM_COLOR['3311'][0]) ==\
        SUPPORT_BRIGHTNESS + SUPPORT_COLOR_TEMP + SUPPORT_HEX_COLOR
    assert supported_color_features(LIGHT_CWS['3311'][0]) ==\
        SUPPORT_BRIGHTNESS + SUPPORT_RGB_COLOR + SUPPORT_HEX_COLOR
    assert supported_color_features(LIGHT_CWS_CUSTOM_COLOR['3311'][0]) ==\
        SUPPORT_BRIGHTNESS + SUPPORT_RGB_COLOR + SUPPORT_HEX_COLOR
