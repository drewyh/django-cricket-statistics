"""Views for batting statistics."""

from typing import Dict

from django.db.models import Case, Count, F, IntegerField, OuterRef, Subquery, Sum, When

from django_cricket_statistics.models import Hundred
from django_cricket_statistics.views.common import (
    CareerStatistic,
    SeasonStatistic,
    BATTING_AVERAGE,
    HUNDREDS,
)


class BattingRunsCareerView(CareerStatistic):
    """Most career batting runs."""

    aggregates = Sum("batting_runs")
    ordering = "-batting_runs__sum"


class BattingRunsSeasonView(SeasonStatistic):
    """Most batting runs in a season."""

    aggregates = Sum("batting_runs")
    ordering = "-batting_runs"


class BattingAverageMixin:
    """Mixin for calculating batting average."""

    ordering = "-batting_average"

    @classmethod
    def get_aggregates(cls) -> Dict:
        """Return the required aggregate values for annotation."""
        return BATTING_AVERAGE


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


class BattingHundredsMixin:
    """Mixin for counting hundreds."""

    ordering = "-hundreds__count"

    @classmethod
    def get_aggregates(cls) -> Dict:
        """Return the required aggregate values for annotation."""
        return HUNDREDS


class HundredsCareerView(BattingHundredsMixin, CareerStatistic):
    """Number of career hundreds."""


class HundredsSeasonView(BattingHundredsMixin, CareerStatistic):
    """Number of season hundreds."""
