"""Views for misc statistics."""

from django.db.models import Sum

from django_cricket_statistics.views.common import CareerStatistic


class MatchesCareerView(CareerStatistic):
    """Most career games."""

    aggregates = {"number_of_matches__sum": Sum("number_of_matches")}
    ordering = "-number_of_matches__sum"
    columns_extra = {"number_of_matches__sum": "Matches"}


# class AllRounder1000Runs100WicketsView(CareerStatistic):
