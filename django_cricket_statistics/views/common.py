"""Views for statistics."""

from typing import Dict, Optional, Tuple

from django.db.models import QuerySet
from django.views.generic import ListView

from django_cricket_statistics.models import Statistic


class PlayerStatisticView(ListView):
    """View for statistics grouped by player."""

    model = Statistic
    paginate_by = 20

    aggregates: Optional[Dict] = None
    filters: Optional[Dict] = None
    group_by: Tuple[str, ...] = tuple()

    def get_queryset(self) -> QuerySet:
        """Return the queryset for the view."""
        # handle filtering from the url
        pre_filters = {
            name: self.kwargs[name]
            for name in ("grade", "season")
            if name in self.kwargs
        }

        aggregates = self.aggregates or {}
        filters = self.filters or {}

        return create_queryset(
            pre_filters=pre_filters,
            group_by=self.group_by,
            aggregates=aggregates,
            filters=filters,
        )


def create_queryset(
    pre_filters: Optional[Dict] = None,
    group_by: Optional[Tuple] = None,
    aggregates: Optional[Dict] = None,
    filters: Optional[Dict] = None,
    select_related: Optional[Tuple] = ("player",),
) -> QuerySet:
    """Create a queryset by applying filters, grouping, aggregation."""
    # only permit senior records to be included
    queryset = Statistic.objects.filter(grade__is_senior=True)

    queryset = queryset.filter(**pre_filters) if pre_filters else queryset

    # group the results for aggregation
    queryset = queryset.values(*group_by) if group_by else queryset

    # the associated player is always required
    if select_related:
        queryset = queryset.select_related(*select_related)

    # annotate the required values
    queryset = queryset.annotate(**aggregates) if aggregates else queryset

    # apply filters
    queryset = queryset.filter(**filters) if filters else queryset

    return queryset


class SeasonStatistic(PlayerStatisticView):
    """Display statistics for each season."""

    group_by = ("player", "season")


class CareerStatistic(PlayerStatisticView):
    """Display all statistics for a given player."""

    group_by = ("player",)
