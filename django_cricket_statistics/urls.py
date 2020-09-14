"""URLs for django_cricket_statistics."""
from typing import Callable, Dict, List

from django.urls import path, include

from tests import test_settings as settings
from django_cricket_statistics import views

HOMEPAGE_PATTERNS = {
    "Batting records": "batting-statistics",
    "Bowling records": "bowling-statistics",
}

BATTING_PATTERNS = {
    "Most runs (career)": "batting-runs-career",
    "Most runs (season)": "batting-runs-season",
    "Best batting average (career)": "batting-average-career",
    "Best batting average (season)": "batting-average-season",
    # "Most runs in an innings": "batting/highscore/career",
    "Most hundreds (career)": "batting-hundreds-career",
    "Most hundreds (season)": "batting-hundreds-season",
}

BOWLING_PATTERNS = {
    "Most wickets (career)": "bowling-wickets-career",
    "Most wickets (season)": "bowling-wickets-season",
    "Best bowling average (career)": "bowling-average-career",
    "Best bowling average (season)": "bowling-average-season",
    "Best economy rate (career)": "bowling-economy-rate-career",
    "Best economy rate (season)": "bowling-economy-rate-season",
    "Best strike rate (career)": "bowling-strike-rate-career",
    "Best strike rate (season)": "bowling-strike-rate-season",
    "Most five wicket innings (career)": "bowling-five-wicket-innings-career",
    "Most five wicket innings (season)": "bowling-five-wicket-innings-season",
}


def _name_to_path(name: str) -> str:
    """Convert a view name to its path."""
    # only replace first and last instances so e.g. economy-rate stays complete
    output = name.replace("-", "/", 1)
    output = output[::-1].replace("-", "/", 1)[::-1]
    return output + "/"


def _name_to_view(name: str, views_module: object) -> Callable:
    """Convert a view name to its view class."""
    class_name = name.title().replace("-", "") + "View"
    return getattr(views_module, class_name).as_view()


def _paths_from_patterns(patterns: Dict, views_module: object) -> List:
    """Generate the paths from the patterns for views."""
    return [
        path(_name_to_path(name), _name_to_view(name, views_module), name=name)
        for name in patterns.values()
    ]


urlpatterns = [
    *_paths_from_patterns(BATTING_PATTERNS, views),
    path(
        "batting/",
        views.IndexView.as_view(links=BATTING_PATTERNS),
        name="batting-statistics",
    ),
    *_paths_from_patterns(BOWLING_PATTERNS, views),
    path(
        "bowling/",
        views.IndexView.as_view(links=BOWLING_PATTERNS),
        name="bowling-statistics",
    ),
    path("players/<int:pk>/", views.PlayerCareerView.as_view(), name="player"),
    path("players/<str:letter>/", views.PlayerListView.as_view(), name="player-list-letter"),
    path("players/", views.PlayerListView.as_view(), name="player-list-all"),
    path(
        "",
        views.IndexView.as_view(
            links=HOMEPAGE_PATTERNS,
            template_name="django_cricket_statistics/index.html",
        ),
        name="index",
    ),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
