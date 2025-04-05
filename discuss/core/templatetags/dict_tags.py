from django import template

register = template.Library()

@register.filter(name='get_item')
def get_item(dictionary, key):
    """Gets an item from a dictionary safely."""
    return dictionary.get(key)
