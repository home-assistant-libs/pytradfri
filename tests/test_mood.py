import pytest

from pytradfri.const import ROOT_MOODS
from pytradfri.mood import Mood

from .moods import MOOD


@pytest.fixture
def mood():
    return Mood(MOOD, 131080)


def test_mood_properties(mood):
    assert mood.path == [ROOT_MOODS, 131080, 196625]
