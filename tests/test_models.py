"""Test the views for cricket statistics."""

import pytest

from django_cricket_statistics.views import BattingAverageSeasonView
from django_cricket_statistics.models import Player


@pytest.fixture
def player(db):
    return Player.objects.create(
        first_name="John",
        nickname="Jack",
        middle_names="George Henry",
        last_name="Smith",
    )


def test_player_string(db, player):
    assert str(player) == "JGH Smith"


def test_player_long_name(db, player):
    assert player.long_name == "John George Henry (Jack) Smith"


def test_player_short_name(db, player):
    assert player.short_name == "JGH Smith"
