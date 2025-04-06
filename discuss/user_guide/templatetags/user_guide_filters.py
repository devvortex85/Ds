from django import template

register = template.Library()

@register.filter(name='replace')
def replace(value, arg):
    """
    Replace all instances of the first part of arg with the second part.
    Usage: {{ value|replace:"_: " }} will replace all underscores with spaces.
    """
    if not value or not arg:
        return value
    
    parts = arg.split(':')
    if len(parts) != 2:
        return value
        
    return value.replace(parts[0], parts[1])
