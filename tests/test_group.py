"""Test Group."""
import pytest

from pytradfri import error
from pytradfri.const import (
    ATTR_GROUP_ID,
    ATTR_ID,
    ATTR_LIGHT_COLOR_HUE,
    ATTR_LIGHT_COLOR_SATURATION,
    ATTR_LIGHT_DIMMER,
    ATTR_LIGHT_MIREDS,
    ROOT_MOODS,
)
from pytradfri.gateway import Gateway
from pytradfri.group import Group

from .devices import GROUP


@pytest.fixture
def gateway():
    """Return gateway."""
    return Gateway()


@pytest.fixture
def group(gateway):
    """Return Group."""
    return Group(gateway, GROUP)


def test_setters(group):
    """Test setters in group."""
    cmd = Group("anygateway", GROUP).set_predefined_color("Candlelight")
    assert cmd.data == {"5706": "ebb63e"}

    with pytest.raises(error.ColorError):
        Group("anygateway", GROUP).set_predefined_color("kjlisby")

    cmd = Group("anygateway", GROUP).set_hex_color("c984bb")
    assert cmd.data == {"5706": "c984bb"}

    cmd = Group("anygateway", GROUP).set_predefined_color("Candlelight", 100)
    assert cmd.data == {"5712": 100, "5706": "ebb63e"}

    cmd = Group("anygateway", GROUP).set_xy_color(200, 45000)
    assert cmd.data == {"5709": 200, "5710": 45000}

    cmd = Group("anygateway", GROUP).set_color_temp(300)
    assert cmd.data == {ATTR_LIGHT_MIREDS: 300}

    cmd = Group("anygateway", GROUP).set_hsb(300, 200, 100)
    assert cmd.data == {
        ATTR_LIGHT_COLOR_HUE: 300,
        ATTR_LIGHT_COLOR_SATURATION: 200,
        ATTR_LIGHT_DIMMER: 100,
    }

    cmd = group.add_member(65547)
    assert cmd.data == {ATTR_GROUP_ID: GROUP[ATTR_ID], ATTR_ID: [65547]}

    cmd = group.remove_member(65547)
    assert cmd.data == {ATTR_GROUP_ID: GROUP[ATTR_ID], ATTR_ID: [65547]}


def test_moods(group: Group) -> None:
    """Test moods."""
    cmd = group.moods()
    assert cmd.path == [ROOT_MOODS, group.id]
