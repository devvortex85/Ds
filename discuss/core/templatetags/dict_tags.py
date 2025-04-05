from django import template

register = template.Library()

@register.filter(name='get_item')
def get_item(dictionary, key):
    """Gets an item from a dictionary safely."""
    return dictionary.get(key)

@register.filter(name='nesting_color')
def nesting_color(level):
    """Returns a color index for nested comments based on level."""
    # Use modulo to cycle through 6 colors (0-5)
    return level % 6
