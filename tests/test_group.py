from datetime import datetime
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
    assert cmd.data == "['15004', 131073]: {'5706': 'ebb63e'}"

    with pytest.raises(error.ColorError):
        Group('anygateway', GROUP) \
            .set_predefined_color('kjlisby')

    cmd = Group('anygateway', GROUP) \
        .set_hex_color('c984bb')
    assert cmd.data == "['15004', 131073]: {'5706': 'c984bb'}"

