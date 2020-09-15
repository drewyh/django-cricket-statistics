"""View for statistic indices."""
from typing import Dict

from django.views.generic import TemplateView


class IndexView(TemplateView):
    """View indices."""

    template_name = "django_cricket_statistics/links_index.html"
    links = None
    title = ""

    def get_context_data(self, **kwargs: str) -> Dict:
        """Add the required context data."""
        context = super().get_context_data(**kwargs)
        context["links"] = self.links or {}
        context["title"] = self.title

        return context
