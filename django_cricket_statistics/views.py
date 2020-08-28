"""Views for statistics."""

from abc import ABC
from typing import Callable, Dict, Optional, Sequence

from django.db.models import Case, F, QuerySet, Sum, When
from django.views.generic import ListView

from django_cricket_statistics.models import Hundred, Statistic, BALLS_PER_OVER


class PlayerStatisticView(ListView):
    """View for statistics grouped by player."""

    model = Statistic
    paginate_by = 20

    aggregates: Optional[Dict] = None
    filters: Optional[Dict] = None
    group_by: Optional[Sequence] = None

    @classmethod
    def get_aggregates(cls) -> Dict:
        """Return aggregates from a method."""
        return {}

    def get_queryset(self) -> QuerySet:
        """Return the queryset for the view."""
        # handle filtering from the url
        pre_filters = {
            name: self.kwargs[name]
            for name in ("grade", "season")
            if name in self.kwargs
        }

        group_by = self.group_by or []

        aggregates = self.get_aggregates()
        if self.aggregates:
            aggregates = {agg.default_alias: agg for agg in self.aggregates}

        filters = self.filters or {}

        return create_queryset(
            pre_filters=pre_filters,
            group_by=group_by,
            aggregates=aggregates,
            filters=filters,
        )


def create_queryset(pre_filters=None, group_by=None, aggregates=None, filters=None):
    """Create a queryset by applying filters, grouping, aggregation."""
    queryset = self.model.objects.all()

    queryset = queryset.filter(**pre_filters) if pre_filters else queryset

    # group the results for aggregation
    queryset = queryset.values(*group_by) if group_by else queryset

    # the associated player is always required
    queryset = queryset.select_related("player")

    # annotate the required values
    queryset = queryset.annotate(**aggregates) if aggregates else queryset

    # apply filters
    queryset = queryset.filter(**filters) if filters else queryset

    return queryset


class AggregatorMixinABC(ABC):
    """Abstract base class for aggregator attribute."""

    aggregator: Callable


class SeasonStatistic(AggregatorMixinABC, PlayerStatisticView):
    """Display statistics for each season."""

    aggregator = F


class CareerStatistic(AggregatorMixinABC, PlayerStatisticView):
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


class BattingAverageMixin(AggregatorMixinABC):
    """Mixin for calculating batting average."""

    ordering = "-batting_average"

    @classmethod
    def get_aggregates(cls) -> Dict:
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


class BestBattingInningsView(CareerStatistic):
    """Best batting innings."""

    ordering = (
        "-batting_high_score",
        "-batting_high_score_is_not_out",
        "grade",
        "-season",
    )


class BattingHundredsMixin(AggregatorMixinABC):
    """Mixin for counting hundreds."""

    ordering = "-hundreds__count"

    @classmethod
    def get_aggregates(cls) -> Dict:
        hundreds = (
            Hundred.objects.filter(statistic=OuterRef("pk"))
            .order_by()
            .values("statistic")
            .annotate(hund=Count("*"))
            .values("hund")
        )

        return {
            "hundreds__count": cls.aggregator(
                Subquery(hundreds, output_field=IntegerField())
            )
        }


class HundredsCareerView(BattingHundredsMixin, CareerStatistic):
    """Number of career hundreds."""


class HundredsSeasonView(BattingHundredsMixin, CareerStatistic):
    """Number of season hundreds."""


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

    ordering = ("-best_bowling_wickets", "best_bowling_runs", "grade", "-season")


class BowlingFiveWicketInningsMixin(AggregatorMixinABC):
    """Mixin for counting five wicket innings."""

    ordering = "-five_wicket_innings__count"

    @classmethod
    def get_aggregates(cls) -> Dict:
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


# class AllRounder1000Runs100WicketsView(CareerStatistic):


# class WicketkeepingDismissalsCareerView(CareerStatistic):
# class WicketkeepingDismissalsSeasonView(SeasonStatistic):
# class WicketkeepingCatchesCareerView(CareerStatistic):
# class WicketkeepingCatchesSeasonView(SeasonStatistic):
# class WicketkeepingStumpingsCareerView(CareerStatistic):
# class WicketkeepingStumpingsSeasonView(SeasonStatistic):


# class FieldingCatchesCareerView(CareerStatistic):
# class FieldingCatchesSeasonView(SeasonStatistic):
