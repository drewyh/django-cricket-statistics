"""Views for statistics."""

from abc import ABC
from typing import Callable, Dict, Optional, Tuple

from django.db.models import Expression, F, Model, QuerySet, Sum
from django.views.generic import ListView

from django_cricket_statistics.models import Statistic


class PlayerStatisticView(ListView):
    """View for statistics grouped by player."""

    model = Statistic
    paginate_by = 20

    aggregates: Optional[Expression] = None
    filters: Optional[Dict] = None
    group_by: Tuple[str, ...] = tuple()

    @classmethod
    def get_aggregates(cls) -> Dict:
        """Return aggregates from a method."""
        return {}

    def get_queryset(self) -> QuerySet:
        """Return the queryset for the view."""
        # handle filtering from the url
        pre_filters = {
            name: self.kwargs[name]
            for name in ("grade", "season")
            if name in self.kwargs
        }

        aggregates = self.get_aggregates()
        if self.aggregates:
            aggregates = {self.aggregates.default_alias: self.aggregates}

        filters = self.filters or {}

        return create_queryset(
            model=self.model,
            pre_filters=pre_filters,
            group_by=self.group_by,
            aggregates=aggregates,
            filters=filters,
        )


def create_queryset(
    model: Optional[Model] = None,
    pre_filters: Optional[Dict] = None,
    group_by: Optional[Tuple] = None,
    aggregates: Optional[Dict] = None,
    filters: Optional[Dict] = None,
) -> QuerySet:
    """Create a queryset by applying filters, grouping, aggregation."""
    assert model is not None
    queryset = model.objects.all()

    queryset = queryset.filter(**pre_filters) if pre_filters else queryset

    # group the results for aggregation
    queryset = queryset.values(*group_by) if group_by else queryset

    # the associated player is always required
    queryset = queryset.select_related("player")

    # annotate the required values
    queryset = queryset.annotate(**aggregates) if aggregates else queryset

    # apply filters
    queryset = queryset.filter(**filters) if filters else queryset

    return queryset


class AggregatorMixinABC(ABC):
    """Abstract base class for aggregator attribute."""

    aggregator: Callable


class SeasonStatistic(AggregatorMixinABC, PlayerStatisticView):
    """Display statistics for each season."""

    group_by = ("player", "season")
    aggregator = F


class CareerStatistic(AggregatorMixinABC, PlayerStatisticView):
    """Display all statistics for a given player."""

    group_by = ("player",)
    aggregator = Sum
