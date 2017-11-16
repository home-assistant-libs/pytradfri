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
from pytradfri.color import supported_features
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
