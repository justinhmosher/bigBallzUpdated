from django import template

register = template.Library()

@register.simple_tag
def get_past_picks(past_picks_map, username, teamnumber):
    """Retrieve past picks for a given username and teamnumber."""
    return past_picks_map.get((username, teamnumber))
