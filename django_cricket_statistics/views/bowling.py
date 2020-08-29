"""Views for bowling statistics."""

from typing import Dict

from django.db.models import Sum

from django_cricket_statistics.views.common import CareerStatistic, SeasonStatistic
from django_cricket_statistics.statistics import (
    BOWLING_AVERAGE,
    BOWLING_STRIKE_RATE,
    BOWLING_ECONOMY_RATE,
    FIVE_WICKET_INNINGS,
)


class WicketsCareerView(CareerStatistic):
    """Most career bowling wickets."""

    aggregates = Sum("wickets")
    ordering = "-wickets__sum"


class WicketsSeasonView(SeasonStatistic):
    """Most bowling wickets in a season."""

    ordering = "-wickets"


class BowlingAverageMixin:
    """Mixin for calculating bowling average."""

    ordering = "bowling_average"

    @classmethod
    def get_aggregates(cls) -> Dict:
        """Return the required aggregate values for annotation."""
        return BOWLING_AVERAGE


class BowlingAverageCareerView(BowlingAverageMixin, CareerStatistic):
    """Best career bowling average."""


class BowlingAverageSeasonView(BowlingAverageMixin, SeasonStatistic):
    """Best season bowling average."""


class BowlingEconomyRateMixin:
    """Mixin for calculating bowling economy rate."""

    ordering = "bowling_economy_rate"

    @classmethod
    def get_aggregates(cls) -> Dict:
        """Return the required aggregate values for annotation."""
        return BOWLING_ECONOMY_RATE


class BowlingEconomyRateCareerView(BowlingEconomyRateMixin, CareerStatistic):
    """Best career bowling economy rate."""


class BowlingEconomyRateSeasonView(BowlingEconomyRateMixin, SeasonStatistic):
    """Best season bowling economy rate."""


class BowlingStrikeRateMixin:
    """Mixin for calculating bowling strike rate."""

    ordering = "bowling_strike_rate"

    @classmethod
    def get_aggregates(cls) -> Dict:
        """Return the required aggregate values for annotation."""
        return BOWLING_STRIKE_RATE


class BowlingStrikeRateCareerView(BowlingStrikeRateMixin, CareerStatistic):
    """Best career bowling strike rate."""


class BowlingStrikeRateSeasonView(BowlingStrikeRateMixin, SeasonStatistic):
    """Best season bowling strike rate."""


class BestBowlingInningsView(CareerStatistic):
    """Best bowling innings."""

    ordering = ("-best_bowling_wickets", "best_bowling_runs", "grade", "-season")


class BowlingFiveWicketInningsMixin:
    """Mixin for counting five wicket innings."""

    ordering = "-five_wicket_innings__count"

    @classmethod
    def get_aggregates(cls) -> Dict:
        """Return the required aggregate values for annotation."""
        return FIVE_WICKET_INNINGS


class FiveWicketInningsCareerView(BowlingFiveWicketInningsMixin, CareerStatistic):
    """Number of career hundreds."""


class FiveWicketInningsSeasonView(BowlingFiveWicketInningsMixin, SeasonStatistic):
    """Number of season hundreds."""
