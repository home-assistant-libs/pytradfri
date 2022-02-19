"""Test Color."""
from pytradfri.color import supported_features
from pytradfri.const import (
    ATTR_LIGHT_CONTROL,
    SUPPORT_BRIGHTNESS,
    SUPPORT_COLOR_TEMP,
    SUPPORT_HEX_COLOR,
    SUPPORT_RGB_COLOR,
    SUPPORT_XY_COLOR,
)
from pytradfri.device.light import LightResponse

from .devices import (
    LIGHT_CWS,
    LIGHT_CWS_CUSTOM_COLOR,
    LIGHT_W,
    LIGHT_WS,
    LIGHT_WS_CUSTOM_COLOR,
)

# Kelvin range for which the conversion functions work
# and that RGB bulbs can show
MIN_KELVIN = 1667
MAX_KELVIN = 25000

# Kelvin range that white-spectrum bulbs can actually show
MIN_KELVIN_WS = 2200
MAX_KELVIN_WS = 4000


def test_supported_colors_w():
    """Test supported colors."""
    data = LightResponse(**LIGHT_W[ATTR_LIGHT_CONTROL][0])
    assert supported_features(data) == SUPPORT_BRIGHTNESS


def test_supported_colors_ws():
    """Test supported colors."""
    data = LightResponse(**LIGHT_WS["3311"][0])
    assert (
        supported_features(data)
        == SUPPORT_BRIGHTNESS
        + SUPPORT_COLOR_TEMP
        + SUPPORT_HEX_COLOR
        + SUPPORT_XY_COLOR
    )


def test_supported_colors_ws_custom_color():
    """Test supported colors."""
    data = LightResponse(**LIGHT_WS_CUSTOM_COLOR["3311"][0])
    assert (
        supported_features(data)
        == SUPPORT_BRIGHTNESS
        + SUPPORT_COLOR_TEMP
        + SUPPORT_HEX_COLOR
        + SUPPORT_XY_COLOR
    )


def test_supported_colors_cws_custom():
    """Test supported colors."""
    data = LightResponse(**LIGHT_CWS["3311"][0])
    assert (
        supported_features(data)
        == SUPPORT_BRIGHTNESS + SUPPORT_RGB_COLOR + SUPPORT_HEX_COLOR + SUPPORT_XY_COLOR
    )


def test_supported_colors_cws_custom_color():
    """Test supported colors."""
    data = LightResponse(**LIGHT_CWS_CUSTOM_COLOR["3311"][0])
    assert (
        supported_features(data)
        == SUPPORT_BRIGHTNESS + SUPPORT_RGB_COLOR + SUPPORT_HEX_COLOR + SUPPORT_XY_COLOR
    )
