"""Views for misc statistics."""

from django.db.models import Sum

from django_cricket_statistics.views.common import CareerStatistic


class MatchesCareerView(CareerStatistic):
    """Most career games."""

    aggregates = Sum("matches")
    ordering = "-matches_sum"


# class AllRounder1000Runs100WicketsView(CareerStatistic):
