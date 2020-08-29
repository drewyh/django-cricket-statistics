"""Views for bowling statistics."""

from typing import Dict

from django.db.models import Case, Count, F, IntegerField, OuterRef, Subquery, Sum, When

from django_cricket_statistics.models import FiveWicketInning, BALLS_PER_OVER
from django_cricket_statistics.views.common import (
    CareerStatistic,
    SeasonStatistic,
    AggregatorMixinABC,
)


class WicketsCareerView(CareerStatistic):
    """Most career bowling wickets."""

    aggregates = Sum("wickets")
    ordering = "-wickets__sum"


class WicketsSeasonView(SeasonStatistic):
    """Most bowling wickets in a season."""

    ordering = "-wickets"


class BowlingAverageMixin(AggregatorMixinABC):
    """Mixin for calculating bowling average."""

    ordering = "bowling_average"

    @classmethod
    def get_aggregates(cls) -> Dict:
        """Return the required aggregate values for annotation."""
        return {
            "bowling_runs__sum": cls.aggregator("bowling_runs"),
            "bowling_wickets__sum": cls.aggregator("bowling_wickets"),
            "bowling_average": (
                Case(
                    When(
                        bowling_wickets__sum__gt=0,
                        then=F("bowling_runs__sum") / F("bowling_wickets__sum"),
                    ),
                    default=None,
                ),
            ),
        }


class BowlingAverageCareerView(BowlingAverageMixin, CareerStatistic):
    """Best career bowling average."""


class BowlingAverageSeasonView(BowlingAverageMixin, SeasonStatistic):
    """Best season bowling average."""


class BowlingEconomyRateMixin(AggregatorMixinABC):
    """Mixin for calculating bowling economy rate."""

    ordering = "bowling_economy_rate"

    @classmethod
    def get_aggregates(cls) -> Dict:
        """Return the required aggregate values for annotation."""
        return {
            "bowling_balls__sum": cls.aggregator("bowling_balls"),
            "bowling_runs__sum": cls.aggregator("bowling_runs"),
            "bowling_economy_rate": (
                Case(
                    When(
                        bowling_balls__sum__gt=0,
                        then=F("bowling_runs__sum")
                        / F("bowling_balls__sum")
                        * BALLS_PER_OVER,
                    ),
                    default=None,
                ),
            ),
        }


class BowlingEconomyRateCareerView(BowlingEconomyRateMixin, CareerStatistic):
    """Best career bowling economy rate."""


class BowlingEconomyRateSeasonView(BowlingEconomyRateMixin, SeasonStatistic):
    """Best season bowling economy rate."""


class BowlingStrikeRateMixin(AggregatorMixinABC):
    """Mixin for calculating bowling strike rate."""

    ordering = "bowling_strike_rate"

    @classmethod
    def get_aggregates(cls) -> Dict:
        """Return the required aggregate values for annotation."""
        return {
            "bowling_wickets__sum": cls.aggregator("bowling_wickets"),
            "bowling_balls__sum": cls.aggregator("bowling_balls"),
            "bowling_strike_rate": (
                Case(
                    When(
                        bowling_wickets__sum__gt=0,
                        then=F("bowling_wickets__sum")
                        / F("bowling_balls__sum")
                        * BALLS_PER_OVER,
                    ),
                    default=None,
                ),
            ),
        }


class BowlingStrikeRateCareerView(BowlingStrikeRateMixin, CareerStatistic):
    """Best career bowling strike rate."""


class BowlingStrikeRateSeasonView(BowlingStrikeRateMixin, SeasonStatistic):
    """Best season bowling strike rate."""


class BestBowlingInningsView(CareerStatistic):
    """Best bowling innings."""

    ordering = ("-best_bowling_wickets", "best_bowling_runs", "grade", "-season")


class BowlingFiveWicketInningsMixin(AggregatorMixinABC):
    """Mixin for counting five wicket innings."""

    ordering = "-five_wicket_innings__count"

    @classmethod
    def get_aggregates(cls) -> Dict:
        """Return the required aggregate values for annotation."""
        five_wicket_innings = (
            FiveWicketInning.objects.filter(statistic=OuterRef("pk"))
            .values("statistic")
            .annotate(five=Count("*"))
            .values("five")
        )

        return {
            "five_wicket_innings___count": cls.aggregator(
                Subquery(five_wicket_innings, output_field=IntegerField())
            )
        }


class FiveWicketInningsCareerView(BowlingFiveWicketInningsMixin, CareerStatistic):
    """Number of career hundreds."""


class FiveWicketInningsSeasonView(BowlingFiveWicketInningsMixin, SeasonStatistic):
    """Number of season hundreds."""
