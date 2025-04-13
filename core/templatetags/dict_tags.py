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

@register.filter
def dict_get(dictionary, key):
    """
    Alias for get_item, for backward compatibility with templates.
    
    Usage:
    {{ dictionary|dict_get:key_variable }}
    """
    return get_item(dictionary, key)
    
# Assignment tag version for use with 'as' syntax
@register.simple_tag
def get_dict_item(dictionary, key):
    """
    Get an item from a dictionary using the key, for use with 'as' syntax.
    
    Usage:
    {% get_dict_item dictionary key_variable as value %}
    """
    if dictionary is None:
        return None
    return dictionary.get(key)