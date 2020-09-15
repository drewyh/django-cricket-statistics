"""Views for misc statistics."""

from django.db.models import Sum

from django_cricket_statistics.views.common import CareerStatistic
from django_cricket_statistics.statistics import BATTING_RUNS, BOWLING_WICKETS


class MatchesCareerView(CareerStatistic):
    """Most career games."""

    aggregates = {"matches__sum": Sum("matches")}
    ordering = "-matches__sum"
    columns_extra = {"matches__sum": "Matches"}


class Allrounder1000Runs100WicketsCareerView(CareerStatistic):
    """All rounders who have made 1000 runs and taken 100 wickets."""

    aggregates = {**BATTING_RUNS, **BOWLING_WICKETS}
    ordering = ("-start_year", "-end_year")
    columns_extra = {"batting_runs__sum": "Runs", "bowling_wickets__sum": "Wkts"}
    filters = {"batting_runs__sum__gte": 1000, "bowling_wickets__sum__gte": 100}
