"""Update the query string with new values."""
from django import template
from django.http.request import HttpRequest

register = template.Library()


@register.simple_tag
def query_update(request: HttpRequest, **kwargs: str) -> str:
    """Update the query string with new values."""
    updated = request.GET.copy()
    for key, value in kwargs.items():
        updated[key] = value
    return updated.urlencode()
