from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Get an item from a dictionary using the key"""
    if dictionary is None:
        return None
    return dictionary.get(key)

@register.filter(is_safe=True)
def reputation_badge(karma):
    """Display a reputation badge based on karma level"""
    if karma >= 10000:
        badge = '<span class="badge bg-danger" title="Legend: {0} karma">L</span>'
    elif karma >= 5000:
        badge = '<span class="badge bg-warning text-dark" title="Community Leader: {0} karma">CL</span>'
    elif karma >= 2500:
        badge = '<span class="badge bg-primary" title="Expert: {0} karma">E</span>'
    elif karma >= 1000:
        badge = '<span class="badge bg-info text-dark" title="Trusted Contributor: {0} karma">TC</span>'
    elif karma >= 500:
        badge = '<span class="badge bg-success" title="Established Member: {0} karma">EM</span>'
    elif karma >= 100:
        badge = '<span class="badge bg-secondary" title="Regular: {0} karma">R</span>'
    else:
        badge = '<span class="badge bg-light text-dark" title="New User: {0} karma">NU</span>'
    
    return mark_safe(badge.format(karma))