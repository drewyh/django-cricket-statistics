"""Views for statistics."""

from django.db.models import Case, F, Sum, When
from django.views.generic import ListView

from django_cricket_statistics.models import Statistic, BALLS_PER_OVER


class PlayerStatisticView(ListView):
    """View for statistics grouped by player."""

    model = Statistic
    paginate_by = 20

    aggregates = None
    filters = None
    group_by = None

    @classmethod
    def get_aggregates(cls):
        """Return aggregates from a method."""
        return None

    def get_queryset(self):
        """Return the queryset for the view."""
        # handle filtering from the url
        pre_filters = {
            name: self.kwargs[name]
            for name in ("grade", "season")
            if name in self.kwargs
        }
        queryset = self.model.objects.filter(**pre_filters)

        # group the results
        group_by = self.group_by or {}
        if group_by:
            queryset = queryset.values(*group_by)

        # the associated player is always required
        queryset = queryset.select_related("player")

        # annotate the required value
        aggregates = self.aggregates or self.get_aggregates()
        if self.aggregates is not None:
            if isinstance(aggregates, dict):
                queryset = queryset.annotate(**aggregates)
            else:
                queryset = queryset.annotate(aggregates)

        # apply filters
        filters = self.filters or {}
        if filters:
            queryset = queryset.filter(**filters)

        return queryset


class SeasonStatistic(PlayerStatisticView):
    """Display statistics for each season."""

    aggregator = F


class CareerStatistic(PlayerStatisticView):
    """Display all statistics for a given player."""

    group_by = ("player",)
    aggregator = Sum


class MatchesCareerView(CareerStatistic):
    """Most career games."""

    aggregates = Sum("matches")
    ordering = "-matches_sum"


class BattingRunsCareerView(CareerStatistic):
    """Most career batting runs."""

    aggregates = Sum("batting_runs")
    ordering = "-batting_runs__sum"


class BattingRunsSeasonView(SeasonStatistic):
    """Most batting runs in a season."""

    ordering = "-batting_runs"


class BattingAverageMixin:
    """Mixin for calculating batting average."""

    ordering = "-batting_average"

    @classmethod
    def get_aggregates(cls):
        """Return the required aggregate values for annotation."""
        return {
            "batting_outs__sum": cls.aggregator("batting_innings")
            - cls.aggregator("batting_not_outs"),
            "batting_runs__sum": cls.aggregator("batting_runs"),
            "batting_average": (
                Case(
                    When(
                        batting_outs__sum__gt=0,
                        then=F("batting_runs__sum") / F("batting_outs__sum"),
                    ),
                    default=None,
                ),
            ),
        }


class BattingAverageCareerView(BattingAverageMixin, CareerStatistic):
    """Best career batting average."""


class BattingAverageSeasonView(BattingAverageMixin, SeasonStatistic):
    """Best season batting average."""


# class BestBattingInningsView(CareerStatistic):
# class HundredsCareerView(CareerStatistic):
# class HundredsSeasonView(CareerStatistic):


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
    def get_aggregates(cls):
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


class BowlingEconomyRateMixin:
    """Mixin for calculating bowling economy rate."""

    ordering = "bowling_economy_rate"

    @classmethod
    def get_aggregates(cls):
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


class BowlingStrikeRateMixin:
    """Mixin for calculating bowling strike rate."""

    ordering = "bowling_strike_rate"

    @classmethod
    def get_aggregates(cls):
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


# class BestBowlingInningsView(CareerStatistic):
# class FiveWicketInningsSeasonView(SeasonStatistic):
# class FiveWicketInningsCareerView(CareerStatistic):


# class AllRounder1000Runs100WicketsView(CareerStatistic):


# class WicketkeepingDismissalsCareerView(CareerStatistic):
# class WicketkeepingDismissalsSeasonView(SeasonStatistic):
# class WicketkeepingCatchesCareerView(CareerStatistic):
# class WicketkeepingCatchesSeasonView(SeasonStatistic):
# class WicketkeepingStumpingsCareerView(CareerStatistic):
# class WicketkeepingStumpingsSeasonView(SeasonStatistic):


# class FieldingCatchesCareerView(CareerStatistic):
# class FieldingCatchesSeasonView(SeasonStatistic):
