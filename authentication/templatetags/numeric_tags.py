# Inside numeric_tags.py

from django import template

register = template.Library()

@register.filter
def num_range(start, end):
    return range(start, end + 1)
