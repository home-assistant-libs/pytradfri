import pytest
from devices import (GROUP)

from pytradfri import error
from pytradfri.const import (
    ATTR_LIGHT_MIREDS,
    ATTR_LIGHT_COLOR_HUE,
    ATTR_LIGHT_COLOR_SATURATION,
    ATTR_LIGHT_DIMMER
)
from pytradfri.group import Group


@pytest.fixture
def group():
    return Group(GROUP)


def test_setters():
    cmd = Group('anygateway', GROUP) \
        .set_predefined_color('Candlelight')
    assert cmd.data == {'5706': 'ebb63e'}

    with pytest.raises(error.ColorError):
        Group('anygateway', GROUP) \
            .set_predefined_color('kjlisby')

    cmd = Group('anygateway', GROUP) \
        .set_hex_color('c984bb')
    assert cmd.data == {'5706': 'c984bb'}

    cmd = Group('anygateway', GROUP) \
        .set_predefined_color('Candlelight', 100)
    assert cmd.data == {'5712': 100, '5706': 'ebb63e'}

    cmd = Group('anygateway', GROUP) \
        .set_xy_color(200, 45000)
    assert cmd.data == {'5709': 200, '5710': 45000}

    cmd = Group('anygateway', GROUP) \
        .set_color_temp(300)
    assert cmd.data == {ATTR_LIGHT_MIREDS: 300}

    cmd = Group('anygateway', GROUP) \
        .set_hsb(300, 200, 100)
    assert cmd.data == {
        ATTR_LIGHT_COLOR_HUE: 300,
        ATTR_LIGHT_COLOR_SATURATION: 200,
        ATTR_LIGHT_DIMMER: 100,
    }
