"""View for player details."""

from typing import Dict

from django.views.generic import DetailView

from django_cricket_statistics.models import FiveWicketInning, Hundred, Player
from django_cricket_statistics.statistics import ALL_STATISTICS, SEASON_RANGE
from django_cricket_statistics.views.common import create_queryset


class PlayerCareerView(DetailView):
    """View for player career statistics."""

    model = Player

    def get_context_data(self, **kwargs: str) -> Dict:
        """Return the required context data."""
        context = super().get_context_data(**kwargs)

        # add all career statistics
        career_statistics = create_queryset(
            pre_filters={"player__id": self.object.id},
            group_by=("player",),
            aggregates={**SEASON_RANGE, **ALL_STATISTICS},
        )
        # this won't have a grade annotation so we add one
        statistics_career.grade = "All"

        # add career statistics by grade
        statistics_by_grade = create_queryset(
            pre_filters={"player__id": self.object.id},
            group_by=("player", "grade"),
            aggregates={**SEASON_RANGE, **ALL_STATISTICS},
            select_related=("player", "grade"),
        )

        # this will evaluate the queryset immediately since we make it a list
        context["statistics_by_grade_list"] = [
            statistics_career,
            *list(statistics_by_grade),
        ]

        # add display names for this table
        context["statistics_by_grade_names"] = {"grade": "Grade", **ALL_STATISTIC_NAMES}

        # add career statistics by year
        context["statistics_by_year_list"] = create_queryset(
            pre_filters={"player__id": self.object.id},
            group_by=("player", "season"),
            aggregates=ALL_STATISTICS,
            select_related=("player", "season"),
        )

        # add display names for this table
        context["statistics_by_year_names"] = {
            "season": "Season",
            **ALL_STATISTIC_NAMES,
        }

        # add hundreds
        context["hundreds_list"] = Hundred.objects.filter(
            statistic__player__id=self.object.id, statistic__grade__is_senior=True
        ).annotate(
            rank=Window(
                expression=Rank(),
                order_by=[
                    F("runs").desc(),
                    F("is_not_out").desc(),
                    F("is_in_final").desc(),
                ],
            )
        )

        # add display names for this table
        context["hundreds_names"] = {
            "rank": "#",
            "season": "Season",
            "grade": "Grade",
            "score": "Score",
        }

        # add five wicket innings
        context["five_wicket_innings_list"] = FiveWicketInning.objects.filter(
            statistic__player__id=self.object.id, statistic__grade__is_senior=True
        ).annotate(
            rank=Window(
                expression=Rank(),
                order_by=[
                    F("wickets").desc(),
                    F("runs").asc(),
                    F("is_in_final").desc(),
                ],
            )
        )

        # add display names for this table
        context["five_wicket_innings_names"] = {
            "rank": "#",
            "season": "Season",
            "grade": "Grade",
            "figures": "Figures",
        }

        return context
