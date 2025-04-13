from django import template
from django.forms import widgets
import os

register = template.Library()

@register.filter
def fieldtype(field):
    """
    Return the name of the field's widget class.
    Used for conditional rendering in form templates.
    
    Usage:
    {% if field|fieldtype == 'CheckboxInput' %}
        {# Custom rendering for checkboxes #}
    {% endif %}
    """
    return field.field.widget.__class__.__name__

@register.filter
def is_image(file_value):
    """
    Check if a file is an image based on file extension.
    Used for displaying preview of images in form templates.
    
    Usage:
    {% if field.value|is_image %}
        <img src="{{ field.value.url }}" alt="Preview">
    {% endif %}
    """
    if not file_value:
        return False
    
    try:
        # Get the file extension
        _, ext = os.path.splitext(file_value.name.lower())
        # Check if it's an image extension
        return ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg']
    except (AttributeError, ValueError):
        return False