# attribute getter as a filter so we can define attribute programmatically
from django import template

register = template.Library()

@register.filter
def get(value, arg):
    return value.get(arg, "-")
