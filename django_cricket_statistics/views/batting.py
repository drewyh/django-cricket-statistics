"""Views for batting statistics."""

from django_cricket_statistics.views.common import CareerStatistic, SeasonStatistic
from django_cricket_statistics.statistics import BATTING_RUNS, BATTING_AVERAGE, HUNDREDS


class BattingRunsCareerView(CareerStatistic):
    """Most career batting runs."""

    aggregates = BATTING_RUNS
    ordering = "-batting_runs__sum"
    filters = {"batting_runs__sum__gt": 0}
    columns_extra = {"batting_runs__sum": "Runs"}


class BattingRunsSeasonView(SeasonStatistic):
    """Most batting runs in a season."""

    aggregates = BATTING_RUNS
    ordering = "-batting_runs__sum"
    filters = {"batting_runs__sum__gt": 0}
    columns_extra = {"batting_runs__sum": "Runs"}


class BattingAverageCareerView(CareerStatistic):
    """Best career batting average."""

    aggregates = BATTING_AVERAGE
    ordering = "-batting_average"
    filters = {"batting_innings__sum__gte": 20}
    columns_extra = {"batting_average": "Ave"}


class BattingAverageSeasonView(SeasonStatistic):
    """Best season batting average."""

    aggregates = BATTING_AVERAGE
    ordering = "-batting_average"
    filters = {"batting_runs__sum__gte": 200, "batting_innings__sum__gte": 9}
    columns_extra = {"batting_average": "Ave"}


class BattingBestInningsView(CareerStatistic):
    """Best batting innings."""

    ordering = (
        "-batting_high_score",
        "-batting_high_score_is_not_out",
        "grade",
        "-season",
    )


class BattingHundredsCareerView(CareerStatistic):
    """Number of career hundreds."""

    aggregates = HUNDREDS
    ordering = "-hundreds"
    filters = {"hundreds__gt": 0}
    columns_extra = {"hundreds": "Hundreds"}


class BattingHundredsSeasonView(SeasonStatistic):
    """Number of season hundreds."""

    aggregates = HUNDREDS
    ordering = "-hundreds"
    filters = {"hundreds__gt": 0}
    columns_extra = {"hundreds": "Hundreds"}
