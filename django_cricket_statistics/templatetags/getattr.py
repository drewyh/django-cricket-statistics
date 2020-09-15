"""Attribute getter as a filter so we can define attribute programmatically."""
from typing import Any

from django import template

register = template.Library()


@register.filter
def get(value: Any, arg: str) -> Any:
    """Get an attribute of an object using a variable."""
    if hasattr(value, "get"):
        return value.get(arg, None)

    # recurse for dotted attributes
    if "." in arg:
        first, second = arg.split(".", 1)
        return get(get(value, first), second)

    if hasattr(value, arg):
        return getattr(value, arg)

    return None
