from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Get an item from a dictionary using the key.
    This is useful in templates to access dictionary values by key, since Django 
    templates don't allow dictionary lookups with variables.
    
    Usage:
    {{ dictionary|get_item:key_variable }}
    """
    if dictionary is None:
        return None
    return dictionary.get(key)