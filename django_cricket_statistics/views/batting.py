"""Views for batting statistics."""

from typing import Dict

from django.db.models import Case, Count, F, IntegerField, OuterRef, Subquery, Sum, When

from django_cricket_statistics.models import Hundred
from django_cricket_statistics.views.common import (
    CareerStatistic,
    SeasonStatistic,
    AggregatorMixinABC,
)


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
        """Return the required aggregate values for annotation."""
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
