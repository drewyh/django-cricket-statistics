"""Views for statistics."""

from django.shortcuts import render, get_object_or_404
from django.db.models import Max, Min, Sum, Count
from django.views.generic import ListView

from django_cricket_statistics.models import Player, Statistic, BALLS_PER_OVER


class PlayerStatisticView(ListView):
    """View for statistics grouped by player."""

    model = Statistic
    paginate_by = 20

    aggregator = None
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
        if self.aggregator is not None:
            if isinstance(self.aggregator, dict):
                qs = qs.annotate(**self.aggregator)
            else:
                qs = qs.annotate(self.aggregator)

        # apply filters
        if self.filters is not None:
            qs = qs.filter(**self.filters)

        return qs


class SeasonStatistic(PlayerStatisticView):
    """Display statistics for each season."""


class CareerStatistic(PlayerStatisticView):
    """Display all statistics for a given player."""

    group_by = ("player",)


class MatchesCareerView(CareerStatistic):

    aggregator = Sum("matches")
    ordering = "-matches_sum"


class BattingRunsCareerView(CareerStatistic):

    aggregator = Sum("batting_runs")
    ordering = "-batting_runs__sum"


class BattingRunsSeasonView(SeasonStatistic):

    ordering = "-batting_runs"


class BattingAverageMixin:

    aggregate_function = None
    aggregator = {
        batting_outs__sum: BattingAverageMixin.aggregate_function("batting_innings")
        - BattingAverageMixin.aggregate_function("batting_not_outs"),
        batting_runs__sum: BattingAverageMixin.aggregate_function("batting_runs"),
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

    aggregate_function = Sum


class BattingAverageCareerView(BattingAverageMixin, CareerStatistic):

    aggregate_function = F


# class BestBattingInningsView(CareerStatistic):
# class HundredsCareerView(CareerStatistic):
# class HundredsSeasonView(CareerStatistic):


class WicketsCareerView(CareerStatistic):

    aggregator = Sum("wickets")
    ordering = "-wickets__sum"


class WicketsSeasonView(SeasonStatistic):

    ordering = "-wickets"


class BowlingAverageMixin:

    aggregate_function = None
    aggregator = {
        bowling_runs__sum: BowlingAverageMixin.aggregate_function("bowling_runs"),
        bowling_wickets__sum: BowlingAverageMixin.aggregate_function("bowling_wickets"),
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

    aggregate_function = Sum


class BowlingAverageSeasonView(BowlingAverageMixin, SeasonStatistic):

    aggregate_function = F


class EconomyRateMixin:

    aggregate_function = None
    aggregator = {
        bowling_balls__sum: EconomyRateMixin.aggregate_function("bowling_balls"),
        bowling_runs__sum: EconomyRateMixin.aggregate_function("bowling_runs"),
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

    aggregate_function = Sum


class EconomyRateSeasonView(EconomyRateMixin, SeasonStatistic):

    aggregate_function = F


class StrikeRateMixin:

    aggregate_function = None
    aggregator = {
        bowling_wickets__sum: StrikeRateMixin.aggregate_function("bowling_wickets"),
        bowling_balls__sum: StrikeRateMixin.aggregate_function("bowling_balls"),
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

    aggregate_function = Sum


class StrikeRateSeasonView(StrikeRateMixin, SeasonStatistic):

    aggregate_function = F


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
