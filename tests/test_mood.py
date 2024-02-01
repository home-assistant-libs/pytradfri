"""Test mood."""

import pytest

from pytradfri.const import ROOT_MOODS
from pytradfri.mood import Mood

from .moods import MOOD


@pytest.fixture(name="mood")
def mood_fixture():
    """Return Mood object."""
    return Mood(MOOD, 131080)


def test_mood_properties(mood):
    """Test properties of mood."""
    assert mood.path == [ROOT_MOODS, "131080", "196625"]
