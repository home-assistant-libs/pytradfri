from pytradfri.color import kelvin_to_xy, x_to_kelvin, \
    can_kelvin_to_xy, can_x_to_kelvin


def test_known_warm():
    assert kelvin_to_xy(2200) == {'5709': 33135, '5710': 27211}
    assert x_to_kelvin(33135) == 2200


def test_known_norm():
    assert kelvin_to_xy(2700) == {'5709': 30140, '5710': 26909}
    assert x_to_kelvin(30140) == 2700


def test_known_cold():
    assert kelvin_to_xy(4000) == {'5709': 24930, '5710': 24694}
    assert x_to_kelvin(24930) == 4000


def test_unknown_warmish():
    assert kelvin_to_xy((2200 + 2700) // 2) == {
        '5709': (33135 + 30140) // 2,
        '5710': (27211 + 26909) // 2
    }
    assert x_to_kelvin((33135 + 30140) // 2) == (2200 + 2700) // 2


def test_unknown_coldish():
    assert kelvin_to_xy((2700 + 4000) // 2) == {
        '5709': (30140 + 24930) // 2,
        '5710': (26909 + 24694) // 2
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
