import pytest

from pytradfri import error
from pytradfri.group import Group
from devices import (GROUP)


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
