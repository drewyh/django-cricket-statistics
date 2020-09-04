"""URLs for django_cricket_statistics."""
from django.urls import path, include

from tests import test_settings as settings
from django_cricket_statistics import views

urlpatterns = [
    path(
        "batting/runs/career/",
        views.BattingRunsCareerView.as_view(),
        name="batting-runs-career",
    ),
    path(
        "batting/runs/season/",
        views.BattingRunsSeasonView.as_view(),
        name="batting-runs-season",
    ),
    path(
        "batting/average/career/",
        views.BattingAverageCareerView.as_view(),
        name="batting-average-career",
    ),
    path(
        "batting/average/season/",
        views.BattingAverageSeasonView.as_view(),
        name="batting-average-season",
    ),
    # path(
    #     "batting/highscore/career/",
    #     views.BattingBestInningsView.as_view(),
    #     name="batting-highscore-career",
    # ),
    path(
        "batting/hundreds/career/",
        views.BattingHundredsCareerView.as_view(),
        name="batting-hundreds-career",
    ),
    path(
        "batting/hundreds/season/",
        views.BattingHundredsSeasonView.as_view(),
        name="batting-hundreds-season",
    ),
    path(
        "batting/",
        views.StatisticIndexView.as_view(
            links={
                "Most runs (career)": "batting-runs-career",
                "Most runs (season)": "batting-runs-season",
                "Best batting average (career)": "batting-average-career",
                "Best batting average (season)": "batting-average-season",
                # "Most runs in an innings": "batting-highscore-career",
                "Most hundreds (career)": "batting-hundreds-career",
                "Most hundreds (season)": "batting-hundreds-season",
            }
        ),
        name="batting-statistics",
    ),
    path("players/<int:pk>", views.PlayerCareerView.as_view(), name="player"),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
