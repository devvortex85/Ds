from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Get an item from a dictionary using key."""
    if dictionary is None:
        return None
    return dictionary.get(key)

@register.filter
def nesting_color(comment_id):
    """Returns a number from 1-5 based on the comment ID, for colorizing nested comments."""
    if comment_id is None:
        return 1
    return (int(comment_id) % 5) + 1
