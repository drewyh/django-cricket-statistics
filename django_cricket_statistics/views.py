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
        if self.aggregates is not None:
            if isinstance(self.aggregates, dict):
                qs = qs.annotate(**self.aggregates)
            else:
                qs = qs.annotate(self.aggregates)

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

    aggregates = {
        batting_outs__sum: BattingAverageMixin.aggregator("batting_innings")
        - BattingAverageMixin.aggregator("batting_not_outs"),
        batting_runs__sum: BattingAverageMixin.aggregator("batting_runs"),
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
    ordering = "-batting_average"


class BattingAverageCareerView(BattingAverageMixin, CareerStatistic):
    pass


class BattingAverageCareerView(BattingAverageMixin, CareerStatistic):
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

    aggregates = {
        bowling_runs__sum: BowlingAverageMixin.aggregator("bowling_runs"),
        bowling_wickets__sum: BowlingAverageMixin.aggregator("bowling_wickets"),
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
    ordering = "bowling_average"


class BowlingAverageCareerView(BowlingAverageMixin, CareerStatistic):
    pass


class BowlingAverageSeasonView(BowlingAverageMixin, SeasonStatistic):
    pass


class EconomyRateMixin:

    aggregates = {
        bowling_balls__sum: EconomyRateMixin.aggregator("bowling_balls"),
        bowling_runs__sum: EconomyRateMixin.aggregator("bowling_runs"),
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
    ordering = "bowling_economy_rate"


class EconomyRateCareerView(EconomyRateMixin, CareerStatistic):
    pass


class EconomyRateSeasonView(EconomyRateMixin, SeasonStatistic):
    pass


class StrikeRateMixin:

    aggregates = {
        bowling_wickets__sum: StrikeRateMixin.aggregator("bowling_wickets"),
        bowling_balls__sum: StrikeRateMixin.aggregator("bowling_balls"),
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
    ordering = "bowling_strike_rate"


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
