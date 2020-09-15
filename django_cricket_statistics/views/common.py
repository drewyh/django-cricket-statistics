"""Views for statistics."""

from collections import namedtuple
from typing import Dict, Optional, Set, Tuple

from django.db.models import QuerySet
from django.views.generic import ListView

from django_cricket_statistics.models import Player, Season, Statistic
from django_cricket_statistics.views.statistics import ALL_STATISTIC_NAMES, SEASON_RANGE


Table = namedtuple("Table", ["columns", "columns_float", "data", "caption"])

CLASS_LOOKUP = {"player": Player, "season": Season}


class PlayerStatisticView(ListView):
    """View for statistics grouped by player."""

    model = Statistic
    paginate_by = 20

    aggregates: Optional[Dict] = None
    filters: Optional[Dict] = None
    group_by: Tuple[str, ...] = tuple()
    columns_default: Optional[Dict] = None
    columns_extra: Optional[Dict] = None
    columns_float: Optional[Set] = None
    title: str = ""

    def get_queryset(self) -> QuerySet:
        """Return the queryset for the view."""
        # handle filtering from the url
        pre_filters = {
            name: self.request.GET.get(name, None) for name in ("grade", "season")
        }
        pre_filters = {k: v for k, v in pre_filters.items() if v is not None}

        aggregates = self.get_aggregates()
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
        context["statistics_names"] = {
            **(self.columns_default or {}),
            **(self.columns_extra or {}),
        }
        context["statistics_float_fields"] = self.columns_float or set()
        context["caption"] = create_caption(self.filters)

        object_list = context["object_list"]

        for name in self.group_by:
            cls = CLASS_LOOKUP[name]
            pks = {s[name] for s in object_list}

            objs = {
                obj.pk: obj for obj in cls.objects.filter(pk__in=pks)  # type: ignore
            }

            for stat in object_list:
                stat[name] = objs[stat[name]]

        context["title"] = self.title

        return context

    def get_aggregates(self) -> Dict:
        """Return the aggregates required."""
        return self.aggregates or {}


def create_caption(filters: Optional[Dict]) -> Optional[str]:
    """Create a caption based on the filters applied."""
    if not filters:
        return None

    # remove any filters which are simply removing irrelevant stats
    filters = {k.rstrip("__gte"): v for k, v in filters.items() if k.endswith("__gte")}

    if not filters:
        return None

    return "Minimum qualification: " + " ".join(
        f"{v} {ALL_STATISTIC_NAMES[k].lower()}" for k, v in filters.items()
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
    columns_default = {"player": "Player", "season": "Season"}


class CareerStatistic(PlayerStatisticView):
    """Display all statistics for a given player."""

    group_by = ("player",)
    columns_default = {"player": "Player", "season_range": "Span"}

    def get_aggregates(self) -> Dict:
        """Return the aggregates required."""
        aggregates = super().get_aggregates()
        return {**SEASON_RANGE, **aggregates}
