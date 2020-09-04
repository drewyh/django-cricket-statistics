"""Attribute getter as a filter so we can define attribute programmatically."""
from typing import Any

from django import template

register = template.Library()


@register.filter
def get(value: Any, arg: str) -> Any:
    """Get an attribute of an object using a variable."""
    return value.get(arg, None)
