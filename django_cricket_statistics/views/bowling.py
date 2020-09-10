"""Views for bowling statistics."""

from django_cricket_statistics.views.common import CareerStatistic, SeasonStatistic
from django_cricket_statistics.statistics import (
    BOWLING_WICKETS,
    BOWLING_AVERAGE,
    BOWLING_STRIKE_RATE,
    BOWLING_ECONOMY_RATE,
    FIVE_WICKET_INNINGS,
)


class BowlingWicketsCareerView(CareerStatistic):
    """Most career bowling wickets."""

    aggregates = BOWLING_WICKETS
    ordering = "-bowling_wickets__sum"


class BowlingWicketsSeasonView(SeasonStatistic):
    """Most bowling wickets in a season."""

    aggregates = BOWLING_WICKETS
    ordering = "-bowling_wickets__sum"


class BowlingAverageCareerView(CareerStatistic):
    """Best career bowling average."""

    aggregates = BOWLING_AVERAGE
    ordering = "bowling_average"
    columns_float = {"bowling_average"}


class BowlingAverageSeasonView(SeasonStatistic):
    """Best season bowling average."""

    aggregates = BOWLING_AVERAGE
    ordering = "bowling_average"
    columns_float = {"bowling_average"}


class BowlingEconomyRateCareerView(CareerStatistic):
    """Best career bowling economy rate."""

    aggregates = BOWLING_ECONOMY_RATE
    ordering = "bowling_economy_rate"
    columns_float = {"bowling_economy_rate"}


class BowlingEconomyRateSeasonView(SeasonStatistic):
    """Best season bowling economy rate."""

    aggregates = BOWLING_ECONOMY_RATE
    ordering = "bowling_economy_rate"
    columns_float = {"bowling_economy_rate"}


class BowlingStrikeRateCareerView(CareerStatistic):
    """Best career bowling strike rate."""

    aggregates = BOWLING_STRIKE_RATE
    ordering = "bowling_strike_rate"
    columns_float = {"bowling_strike_rate"}


class BowlingStrikeRateSeasonView(SeasonStatistic):
    """Best season bowling strike rate."""

    aggregates = BOWLING_STRIKE_RATE
    ordering = "bowling_strike_rate"
    columns_float = {"bowling_strike_rate"}


class BowlingBestInningsView(CareerStatistic):
    """Best bowling innings."""

    ordering = ("-best_bowling_wickets", "best_bowling_runs", "grade", "-season")


class BowlingFiveWicketInningsCareerView(CareerStatistic):
    """Number of career five wicket innings."""

    aggregates = FIVE_WICKET_INNINGS
    ordering = "-five_wicket_innings__count"


class BowlingFiveWicketInningsSeasonView(SeasonStatistic):
    """Number of season five wicket innings."""

    aggregates = FIVE_WICKET_INNINGS
    ordering = "-five_wicket_innings__count"
