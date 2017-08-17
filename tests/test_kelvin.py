from pytradfri.kelvin import dekelvinize, can_dekelvinize


def test_known_warm():
    assert dekelvinize(2200) == {'5709': 33135, '5710': 27211}


def test_known_norm():
    assert dekelvinize(2700) == {'5709': 30140, '5710': 26909}


def test_known_cold():
    assert dekelvinize(4000) == {'5709': 24930, '5710': 24694}


def test_unknown_warmish():
    assert dekelvinize((2200 + 2700) // 2) == {
        '5709': (33135 + 30140) // 2,
        '5710': (27211 + 26909) // 2
    }


def test_unknown_coldish():
    assert dekelvinize((2700 + 4000) // 2) == {
        '5709': (30140 + 24930) // 2,
        '5710': (26909 + 24694) // 2
    }


def test_can_dekelvinize():
    assert can_dekelvinize(2000) is False
    assert can_dekelvinize(2200) is True
    assert can_dekelvinize(2400) is True
    assert can_dekelvinize(2700) is True
    assert can_dekelvinize(3000) is True
    assert can_dekelvinize(4000) is True
    assert can_dekelvinize(5000) is False
