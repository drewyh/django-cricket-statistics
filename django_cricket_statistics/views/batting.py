"""Views for batting statistics."""

from django_cricket_statistics.views.common import CareerStatistic, SeasonStatistic
from django_cricket_statistics.statistics import BATTING_RUNS, BATTING_AVERAGE, HUNDREDS


class BattingRunsCareerView(CareerStatistic):
    """Most career batting runs."""

    aggregates = BATTING_RUNS
    ordering = "-batting_runs__sum"


class BattingRunsSeasonView(SeasonStatistic):
    """Most batting runs in a season."""

    aggregates = BATTING_RUNS
    ordering = "-batting_runs__sum"


class BattingAverageCareerView(CareerStatistic):
    """Best career batting average."""

    aggregates = BATTING_AVERAGE
    ordering = "-batting_average"


class BattingAverageSeasonView(SeasonStatistic):
    """Best season batting average."""

    aggregates = BATTING_AVERAGE
    ordering = "-batting_average"
    filters = {"batting_aggregate__sum__gte": 200, "batting_innings__sum__gte": 9}


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
    ordering = "-hundreds__count"


class BattingHundredsSeasonView(CareerStatistic):
    """Number of season hundreds."""

    aggregates = HUNDREDS
    ordering = "-hundreds__count"
