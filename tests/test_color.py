from pytradfri.const import (ATTR_LIGHT_COLOR_X as X, ATTR_LIGHT_COLOR_Y as Y)
from pytradfri.color import kelvin_to_xy, x_to_kelvin, \
    kelvin_to_xyY, rgb_to_xyY, \
    can_kelvin_to_xy, can_x_to_kelvin


def test_known_warm():
    assert kelvin_to_xy(2200) == {X: 33135, Y: 27211}
    assert x_to_kelvin(33135) == 2200


def test_known_norm():
    assert kelvin_to_xy(2700) == {X: 30140, Y: 26909}
    assert x_to_kelvin(30140) == 2700


def test_known_cold():
    assert kelvin_to_xy(4000) == {X: 24930, Y: 24694}
    assert x_to_kelvin(24930) == 4000


def test_unknown_warmish():
    assert kelvin_to_xy((2200 + 2700) // 2) == {
        X: (33135 + 30140) // 2,
        Y: (27211 + 26909) // 2
    }
    assert x_to_kelvin((33135 + 30140) // 2) == (2200 + 2700) // 2


def test_unknown_coldish():
    assert kelvin_to_xy((2700 + 4000) // 2) == {
        X: (30140 + 24930) // 2,
        Y: (26909 + 24694) // 2
    }
    assert x_to_kelvin((30140 + 24930) // 2) == (2700 + 4000) // 2


def test_can_dekelvinize():
    assert can_kelvin_to_xy(2000) is False
    assert can_kelvin_to_xy(2200) is True
    assert can_kelvin_to_xy(2400) is True
    assert can_kelvin_to_xy(2700) is True
    assert can_kelvin_to_xy(3000) is True
    assert can_kelvin_to_xy(4000) is True
    assert can_kelvin_to_xy(5000) is False
    assert can_x_to_kelvin(24000) is False
    assert can_x_to_kelvin(24930) is True
    assert can_x_to_kelvin(26000) is True
    assert can_x_to_kelvin(30140) is True
    assert can_x_to_kelvin(32000) is True
    assert can_x_to_kelvin(33135) is True
    assert can_x_to_kelvin(34000) is False


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
