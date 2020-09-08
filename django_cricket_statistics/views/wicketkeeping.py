"""Views for wicketkeeping statistics."""

from django_cricket_statistics.views.common import CareerStatistic, SeasonStatistic
from django_cricket_statistics.statistics import (
    WICKETKEEPING_CATCHES,
    WICKETKEEPING_STUMPINGS,
    WICKETKEEPING_DISMISSALS,
)


class WicketkeepingDismissalsCareerView(CareerStatistic):
    """Most career wicketkeeping dismissals."""

    aggregates = WICKETKEEPING_DISMISSALS
    ordering = "-wicketkeeping_dismissals__sum"
    filters = {"wicketkeeping_dismissals__sum__gt": 0}
    columns_extra = {"wicketkeeping_dismissals__sum": "Dis"}


class WicketkeepingDismissalsSeasonView(SeasonStatistic):
    """Most season wicketkeeping dismissals."""

    aggregates = WICKETKEEPING_DISMISSALS
    ordering = "-wicketkeeping_dismissals__sum"
    filters = {"wicketkeeping_dismissals__sum__gt": 0}
    columns_extra = {"wicketkeeping_dismissals__sum": "WK Dis"}


class WicketkeepingCatchesCareerView(CareerStatistic):
    """Most career wicketkeeping catches."""

    aggregates = WICKETKEEPING_CATCHES
    ordering = "-wicketkeeping_catches__sum"
    filters = {"wicketkeeping_catches__sum__gt": 0}
    columns_extra = {"wicketkeeping_catches__sum": "WK Ct"}


class WicketkeepingCatchesSeasonView(SeasonStatistic):
    """Most season wicketkeeping catches."""

    aggregates = WICKETKEEPING_CATCHES
    ordering = "-wicketkeeping_catches__sum"
    filters = {"wicketkeeping_catches__sum__gt": 0}
    columns_extra = {"wicketkeeping_catches__sum": "WK Ct"}


class WicketkeepingStumpingsCareerView(CareerStatistic):
    """Most career wicketkeeping stumpings."""

    aggregates = WICKETKEEPING_STUMPINGS
    ordering = "-wicketkeeping_stumpings__sum"
    filters = {"wicketkeeping_stumpings__sum__gt": 0}
    columns_extra = {"wicketkeeping_stumpings__sum": "WK St"}


class WicketkeepingStumpingsSeasonView(SeasonStatistic):
    """Most season wicketkeeping stumpings."""

    aggregates = WICKETKEEPING_STUMPINGS
    ordering = "-wicketkeeping_stumpings__sum"
    filters = {"wicketkeeping_stumpings__sum__gt": 0}
    columns_extra = {"wicketkeeping_stumpings__sum": "WK St"}
