"""Test the views for cricket statistics."""

from django.test import TestCase

from django_cricket_statistics.views import BattingAverageSeasonView
from django_cricket_statistics.models import Player


class PlayerTestCase(TestCase):
    def setUp(self):
        Player.objects.create(
            first_name="John",
            nickname="Jack",
            middle_names="George Henry",
            last_name="Smith",
        )

    def test_player_string(self):
        player = Player.objects.get(first_name="John")
        self.assertEqual(str(player), "JGH Smith")

    def test_player_long_name(self):
        player = Player.objects.get(first_name="John")
        self.assertEqual(player.long_name, "John George Henry (Jack) Smith")

    def test_player_short_name(self):
        player = Player.objects.get(first_name="John")
        self.assertEqual(player.short_name, "JGH Smith")

