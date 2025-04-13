from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def class_name(obj):
    """
    Return the class name of an object
    
    Usage:
    {{ object|class_name }}
    
    Example:
    {% if object|class_name == 'User' %}
        <!-- do something -->
    {% endif %}
    """
    return obj.__class__.__name__