"""Views for players."""

from typing import Dict

from django.db.models import QuerySet
from django.views.generic import ListView

from django_cricket_statistics.models import Player

from django_cricket_statistics.statistics import SEASON_RANGE_PLAYER


class PlayerListView(ListView):
    """View for list of players."""

    model = Player
    paginate_by = 20

    def get_queryset(self) -> QuerySet:
        """Return the queryset for the view."""
        queryset = super().get_queryset()

        # handle filtering from the url
        initial_letter = self.request.GET.get("letter", None)

        if initial_letter:
            queryset = queryset.filter(last_name__istartswith=initial_letter)

        queryset = queryset.annotate(**SEASON_RANGE_PLAYER)

        return queryset

    def get_context_data(self, **kwargs: str) -> Dict:
        """Add extra context to be passed to the template."""
        context = super().get_context_data(**kwargs)
        context["player_list_names"] = {
            "short_name": "Player",
            "season_range": "Career",
        }

        print(dir(context["page_obj"]))
        return context
