"""View for player details."""

import string
from typing import Dict

# from django.db.models import F, Window
# from django.db.models.functions import Rank
from django.db.models import QuerySet
from django.views.generic import DetailView, ListView

from django_cricket_statistics.models import (
    Grade,
    Player,
    FirstElevenNumber,
    Season,
    FiveWicketInning,
    Hundred,
)
from django_cricket_statistics.views.statistics import (
    ALL_STATISTICS,
    ALL_STATISTIC_NAMES,
    ALL_STATISTIC_FLOATS,
    SEASON_RANGE,
    SEASON_RANGE_PLAYER,
)
from django_cricket_statistics.views.common import create_queryset


class PlayerListView(ListView):
    """View for list of players."""

    model = Player
    paginate_by = 20
    ordering = (
        "last_name",
        "first_name",
        "middle_names",
    )  # TODO: why does this need to be specified here?
    title = "Players"

    def get_queryset(self) -> QuerySet:
        """Return the queryset for the view."""
        queryset = super().get_queryset()

        # handle filtering from the url
        initial_letter = self.kwargs.get("letter", None)
        search_term = self.request.GET.get("q", None)

        queryset = queryset.annotate(**SEASON_RANGE_PLAYER)

        if initial_letter:
            return queryset.filter(last_name__istartswith=initial_letter)

        if search_term:
            return queryset.filter(last_name__icontains=search_term)

        return queryset.none()

    def get_context_data(self, **kwargs: str) -> Dict:
        """Add extra context to be passed to the template."""
        context = super().get_context_data(**kwargs)
        context["player_list_names"] = {
            "short_name": "Player",
            "season_range": "Career",
        }
        context["letters"] = string.ascii_uppercase
        context["start_rank"] = context["page_obj"].start_index
        context["title"] = self.title

        return context


class PlayerListFirstElevenNumberView(ListView):
    """View for list of who have played first eleven."""

    model = Player
    paginate_by = 20
    ordering = "-first_eleven_number__pk"
    title = "First eleven numbers"

    def get_queryset(self) -> QuerySet:
        """Return the queryset for the view."""
        queryset = super().get_queryset()

        queryset = (
            queryset.select_related("first_eleven_number")
            .exclude(first_eleven_number__isnull=True)
            .annotate(**SEASON_RANGE_PLAYER)
        )

        return queryset

    def get_context_data(self, **kwargs: str) -> Dict:
        """Add extra context to be passed to the template."""
        context = super().get_context_data(**kwargs)
        context["player_list_names"] = {
            "first_eleven_number": "#",
            "short_name": "Player",
            "season_range": "Career",
        }
        context["start_rank"] = None
        context["title"] = self.title

        return context


class PlayerCareerView(DetailView):
    """View for player career statistics."""

    model = Player

    def get_queryset(self) -> QuerySet:
        """Return the queryset for the view."""
        queryset = super().get_queryset()
        queryset = queryset.select_related("first_eleven_number")
        return queryset

    def get_context_data(self, **kwargs: str) -> Dict:
        """Return the required context data."""
        context = super().get_context_data(**kwargs)

        # retrieve the object primary key
        player_pk = self.kwargs.get(self.pk_url_kwarg)

        # add all career statistics
        career_statistics = create_queryset(
            pre_filters={"player__pk": player_pk},
            group_by=("player__pk",),
            aggregates={**ALL_STATISTICS},
            select_related=("player",),
        ).get()

        # this won't have a grade annotation so we add one
        career_statistics["grade"] = "All"

        # add career statistics by grade
        statistics_by_grade = create_queryset(
            pre_filters={"player__pk": player_pk},
            group_by=("player", "grade"),
            aggregates={**SEASON_RANGE, **ALL_STATISTICS},
            select_related=("player", "grade"),
        )

        # get the associated grades
        pks = {s["grade"] for s in statistics_by_grade}
        objs = {obj.pk: obj for obj in Grade.objects.filter(pk__in=pks)}

        for stat in statistics_by_grade:
            stat["grade"] = objs[stat["grade"]]

        # this will evaluate the queryset immediately since we make it a list
        context["statistics_by_grade_list"] = [
            career_statistics,
            *list(statistics_by_grade),
        ]

        # add display names for this table
        context["statistics_by_grade_names"] = {"grade": "Grade", **ALL_STATISTIC_NAMES}

        # add career statistics by year
        statistics_by_year = create_queryset(
            pre_filters={"player__pk": player_pk},
            group_by=("player", "season"),
            aggregates=ALL_STATISTICS,
            select_related=("player", "season"),
        ).order_by("-season__year")

        # get the associated season
        pks = {s["season"] for s in statistics_by_year}
        objs = {obj.pk: obj for obj in Season.objects.filter(pk__in=pks)}

        for stat in statistics_by_year:
            stat["season"] = objs[stat["season"]]

        context["statistics_by_year_list"] = statistics_by_year

        # add display names for this table
        context["statistics_by_year_names"] = {
            "season": "Season",
            **ALL_STATISTIC_NAMES,
        }

        context["statistics_float_fields"] = ALL_STATISTIC_FLOATS

        # add hundreds
        context["hundreds_list"] = (
            Hundred.objects.filter(
                statistic__player__pk=player_pk, statistic__grade__is_senior=True
            )
            .order_by("-runs", "-is_not_out", "-is_in_final")
            .select_related("statistic__grade", "statistic__season")
        )

        # add display names for this table
        context["hundreds_names"] = {
            "statistic.season": "Season",
            "statistic.grade": "Grade",
            "score": "Score",
        }

        # add five wicket innings
        context["five_wicket_innings_list"] = (
            FiveWicketInning.objects.filter(
                statistic__player__pk=player_pk, statistic__grade__is_senior=True
            )
            .order_by("-wickets", "runs", "-is_in_final")
            .select_related("statistic__grade", "statistic__season")
        )

        # add display names for this table
        context["five_wicket_innings_names"] = {
            "statistic.season": "Season",
            "statistic.grade": "Grade",
            "figures": "Figures",
        }

        return context
