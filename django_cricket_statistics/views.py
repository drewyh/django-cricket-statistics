"""Views for statistics."""

from django.shortcuts import render, get_object_or_404
from django.db.models import Max, Min, Sum, Count
from django.views.generic import ListView

from django_cricket_statistics.models import Player, Statistic, BALLS_PER_OVER


class PlayerStatisticView(ListView):
    """View for statistics grouped by player."""

    model = Statistic
    paginate_by = 20

    aggregates = None
    filters = None
    group_by = None

    def get_queryset(self):

        # handle filtering from the url
        pre_filters = {
            name: self.kwargs[name]
            for name in ("grade", "season")
            if name in self.kargs
        }
        qs = self.model.objects.filter(**pre_filters)

        # group the results
        if self.group_by is not None:
            qs = qs.values(*self.group_by)

        # the associated player is always required
        qs = qs.select_related("player")

        # annotate the required value
        aggregates = self.aggregates or self.get_aggregates()
        if self.aggregates is not None:
            if isinstance(aggregates, dict):
                qs = qs.annotate(**aggregates)
            else:
                qs = qs.annotate(aggregates)

        # apply filters
        if self.filters is not None:
            qs = qs.filter(**self.filters)

        return qs


class SeasonStatistic(PlayerStatisticView):
    """Display statistics for each season."""

    aggregator = F


class CareerStatistic(PlayerStatisticView):
    """Display all statistics for a given player."""

    group_by = ("player",)
    aggregator = Sum


class MatchesCareerView(CareerStatistic):

    aggregates = Sum("matches")
    ordering = "-matches_sum"


class BattingRunsCareerView(CareerStatistic):

    aggregates = Sum("batting_runs")
    ordering = "-batting_runs__sum"


class BattingRunsSeasonView(SeasonStatistic):

    ordering = "-batting_runs"


class BattingAverageMixin:

    ordering = "-batting_average"

    @classmethod
    def get_aggregates(cls):
        return {
            batting_outs__sum: cls.aggregator("batting_innings")
            - cls.aggregator("batting_not_outs"),
            batting_runs__sum: cls.aggregator("batting_runs"),
            batting_average: (
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
    pass


class BattingAverageSeasonView(BattingAverageMixin, SeasonStatistic):
    pass


# class BestBattingInningsView(CareerStatistic):
# class HundredsCareerView(CareerStatistic):
# class HundredsSeasonView(CareerStatistic):


class WicketsCareerView(CareerStatistic):

    aggregates = Sum("wickets")
    ordering = "-wickets__sum"


class WicketsSeasonView(SeasonStatistic):

    ordering = "-wickets"


class BowlingAverageMixin:

    ordering = "bowling_average"

    @classmethod
    def get_aggregates(cls):
        return {
            bowling_runs__sum: cls.aggregator("bowling_runs"),
            bowling_wickets__sum: cls.aggregator("bowling_wickets"),
            bowling_average: (
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
    pass


class BowlingAverageSeasonView(BowlingAverageMixin, SeasonStatistic):
    pass


class EconomyRateMixin:

    ordering = "bowling_economy_rate"

    @classmethod
    def get_aggregates(cls):
        return {
            bowling_balls__sum: cls.aggregator("bowling_balls"),
            bowling_runs__sum: cls.aggregator("bowling_runs"),
            bowling_economy_rate: (
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


class EconomyRateCareerView(EconomyRateMixin, CareerStatistic):
    pass


class EconomyRateSeasonView(EconomyRateMixin, SeasonStatistic):
    pass


class StrikeRateMixin:

    ordering = "bowling_strike_rate"

    @classmethod
    def get_aggregates(cls):
        return {
            bowling_wickets__sum: cls.aggregator("bowling_wickets"),
            bowling_balls__sum: cls.aggregator("bowling_balls"),
            bowling_strike_rate: (
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


class StrikeRateCareerView(StrikeRateMixin, CareerStatistic):
    pass


class StrikeRateSeasonView(StrikeRateMixin, SeasonStatistic):
    pass


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
