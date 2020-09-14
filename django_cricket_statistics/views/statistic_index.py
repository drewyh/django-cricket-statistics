"""View for statistic indices."""
from typing import Dict

from django.views.generic import TemplateView


class StatisticIndexView(TemplateView):
    """View statistic indices."""

    template_name = "django_cricket_statistics/link_index.html"
    links = None

    def get_context_data(self, **kwargs: str) -> Dict:
        """Add the required context data."""
        context = super().get_context_data(**kwargs)
        context["links"] = self.links or {}

        return context
