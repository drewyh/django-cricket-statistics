"""Views for fielding statistics."""

from django_cricket_statistics.views.common import CareerStatistic, SeasonStatistic
from django_cricket_statistics.views.statistics import (
    FIELDING_CATCHES,
    FIELDING_RUN_OUTS,
)


class FieldingCatchesCareerView(CareerStatistic):
    """Most career fielding catches."""

    aggregates = FIELDING_CATCHES
    ordering = "-fielding_catches_non_wk__sum"
    filters = {"fielding_catches_non_wk__sum__gt": 0}
    columns_extra = {"fielding_catches_non_wk__sum": "Ct"}


class FieldingCatchesSeasonView(SeasonStatistic):
    """Most season fielding catches."""

    aggregates = FIELDING_CATCHES
    ordering = "-fielding_catches_non_wk__sum"
    filters = {"fielding_catches_non_wk__sum__gt": 0}
    columns_extra = {"fielding_catches_non_wk__sum": "Ct"}


class FieldingRunOutsCareerView(CareerStatistic):
    """Most career fielding runouts (assisted and unassisted)."""

    aggregates = FIELDING_RUN_OUTS
    ordering = "-fielding_run_outs__sum"
    filters = {"fielding_run_outs__sum__gt": 0}
    columns_extra = {"fielding_run_outs__sum": "RO"}


class FieldingRunOutsSeasonView(SeasonStatistic):
    """Most season fielding runouts (assisted and unassisted)."""

    aggregates = FIELDING_RUN_OUTS
    ordering = "-fielding_run_outs__sum"
    filters = {"fielding_run_outs__sum__gt": 0}
    columns_extra = {"fielding_run_outs__sum": "RO"}
