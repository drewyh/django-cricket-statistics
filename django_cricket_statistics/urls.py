from django.urls import path, include

from tests import test_settings as settings
from django_cricket_statistics import views

urlpatterns = [
    path('players/<int:pk>', views.PlayerCareerView.as_view()),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
