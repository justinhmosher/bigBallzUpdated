from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def get_item(dictionary, key1_key2):
    """Retrieve a value from a dictionary using two keys."""
    if dictionary and key1_key2 in dictionary:
        return dictionary.get(key1_key2)
    return None

# Custom filter to fetch items using separate keys
@register.filter(name='get_item_with_keys')
def get_item_with_keys(dictionary, key1, key2):
    """Retrieve a value from a dictionary using two separate keys."""
    return dictionary.get((key1, key2))

@register.filter
def add_linebreaks(value, delimiter='/'):
    """
    Splits the string by the specified delimiter and joins it with actual HTML line breaks.
    """
    lines = value.split(delimiter)
    return mark_safe('<br>'.join(lines))
