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

        queryset = create_queryset(
            pre_filters=pre_filters,
            group_by=self.group_by,
            aggregates=aggregates,
            filters=filters,
        )

        ordering = self.get_ordering()
        if ordering:
            if isinstance(ordering, str):
                ordering = (ordering,)
            queryset = queryset.order_by(*ordering)

        return queryset

    def get_context_data(self, **kwargs: str) -> Dict:
        """Add extra context to be passed to the template."""
        context = super().get_context_data(**kwargs)
        context["statistics_names"] = {"season": "Season", "player": "Player"}
        context["statistics_float_fields"] = set()

        return context


def create_queryset(
    pre_filters: Optional[Dict] = None,
    group_by: Optional[Tuple] = None,
    aggregates: Optional[Dict] = None,
    filters: Optional[Dict] = None,
    select_related: Optional[Tuple] = ("player",),
) -> QuerySet:
    """Create a queryset by applying filters, grouping, aggregation."""
    # only permit senior records to be included
    # remove ordering as this affects the grouping
    queryset = Statistic.objects.filter(grade__is_senior=True).order_by()

    queryset = queryset.filter(**pre_filters) if pre_filters else queryset

    # the associated player is always required
    if select_related:
        queryset = queryset.select_related(*select_related)

    # we need to include the select related in values
    # group_by = [*select_related, *group_by]

    # group the results for aggregation
    queryset = queryset.values(*group_by) if group_by else queryset

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
