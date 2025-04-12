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
    """Display a reputation badge based on karma level with Bootstrap Icons"""
    if karma >= 10000:
        badge = '<span class="badge bg-danger" title="Legend: {0} reputation"><i class="bi bi-trophy-fill"></i></span>'
    elif karma >= 5000:
        badge = '<span class="badge bg-warning text-dark" title="Community Leader: {0} reputation"><i class="bi bi-star-fill"></i></span>'
    elif karma >= 2500:
        badge = '<span class="badge bg-primary" title="Expert: {0} reputation"><i class="bi bi-patch-check-fill"></i></span>'
    elif karma >= 1000:
        badge = '<span class="badge bg-info text-dark" title="Trusted Contributor: {0} reputation"><i class="bi bi-award"></i></span>'
    elif karma >= 500:
        badge = '<span class="badge bg-success" title="Established Member: {0} reputation"><i class="bi bi-shield-fill"></i></span>'
    elif karma >= 100:
        badge = '<span class="badge bg-secondary" title="Regular: {0} reputation"><i class="bi bi-person-check-fill"></i></span>'
    else:
        badge = '<span class="badge bg-light text-dark" title="New User: {0} reputation"><i class="bi bi-person"></i></span>'
    
    return mark_safe(badge.format(karma))

@register.filter(is_safe=True)
def reputation_level_badge(level_name, karma=0):
    """Display a reputation level badge with appropriate styling and icons"""
    level_badges = {
        'New User': '<span class="badge bg-light text-dark" title="New User"><i class="bi bi-person"></i></span>',
        'Regular': '<span class="badge bg-secondary" title="Regular"><i class="bi bi-person-check-fill"></i></span>',
        'Established Member': '<span class="badge bg-success" title="Established Member"><i class="bi bi-shield-fill"></i></span>',
        'Trusted Contributor': '<span class="badge bg-info text-dark" title="Trusted Contributor"><i class="bi bi-award"></i></span>',
        'Expert': '<span class="badge bg-primary" title="Expert"><i class="bi bi-patch-check-fill"></i></span>',
        'Community Leader': '<span class="badge bg-warning text-dark" title="Community Leader"><i class="bi bi-star-fill"></i></span>',
        'Legend': '<span class="badge bg-danger" title="Legend"><i class="bi bi-trophy-fill"></i></span>',
    }
    
    if level_name in level_badges:
        return mark_safe(level_badges[level_name])
    else:
        # Default badge if level name not found
        return mark_safe('<span class="badge bg-secondary" title="{0}"><i class="bi bi-question-circle"></i></span>'.format(level_name))