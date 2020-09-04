"""URLs for django_cricket_statistics."""
from django.urls import path, include

from tests import test_settings as settings
from django_cricket_statistics import views

urlpatterns = [
    path(
        "batting/average/career",
        views.BattingAverageCareerView.as_view(),
        name="batting-average-career",
    ),
    path(
        "batting/average/season",
        views.BattingAverageSeasonView.as_view(),
        name="batting-average-season",
    ),
    path("players/<int:pk>", views.PlayerCareerView.as_view(), name="player"),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
