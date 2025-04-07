from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Get an item from a dictionary using the key"""
    if dictionary is None:
        return None
    return dictionary.get(key)

@register.filter
def reputation_badge(karma):
    """Display a reputation badge based on karma level"""
    if karma >= 10000:
        return f'<span class="badge bg-danger" title="Legend: {karma} karma">L</span>'
    elif karma >= 5000:
        return f'<span class="badge bg-warning text-dark" title="Community Leader: {karma} karma">CL</span>'
    elif karma >= 2500:
        return f'<span class="badge bg-primary" title="Expert: {karma} karma">E</span>'
    elif karma >= 1000:
        return f'<span class="badge bg-info text-dark" title="Trusted Contributor: {karma} karma">TC</span>'
    elif karma >= 500:
        return f'<span class="badge bg-success" title="Established Member: {karma} karma">EM</span>'
    elif karma >= 100:
        return f'<span class="badge bg-secondary" title="Regular: {karma} karma">R</span>'
    else:
        return f'<span class="badge bg-light text-dark" title="New User: {karma} karma">NU</span>'