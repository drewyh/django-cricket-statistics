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


class MostWicketsSeasonView(SeasonStatistic):

    ordering = "-wickets"


class MostWicketsCareerView(CareerStatistic):

    aggregator = Sum("wickets")
    ordering = "-wickets__sum"


class EconomyRateMixin:

    aggregator = {
        economy_rate: (
            Case(
                When(
                    bowling_balls__sum__gt=0,
                    then=F("bowling_runs__sum")
                    / F("bowling_balls__sum")
                    * BALLS_PER_OVER,
                ),
                default=None,
            ),
        )
    }
    ordering = "economy_rate"


class EconomyRateSeasonView(EconomyRateMixin, SeasonStatistic):

    aggregator = {
        bowling_balls__sum: F("bowling_balls"),
        bowling_runs__sum: F("bowling_runs"),
        **EconomyRateMixin.aggregator,
    }


class EconomyRateCareerView(EconomyRateMixin, CareerStatistic):

    aggregator = {
        bowling_balls__sum: Sum("bowling_balls"),
        bowling_runs__sum: Sum("bowling_runs"),
        **EconomyRateMixin.aggregator,
    }


class RunsSeasonView(SeasonStatistic):

    ordering = "-batting_runs"


class RunsCareerView(CareerStatistic):

    aggregator = Sum("batting_runs")
    ordering = "-batting_runs__sum"
