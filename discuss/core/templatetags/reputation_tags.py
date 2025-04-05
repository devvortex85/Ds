from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def reputation_badge(karma, min_value=0):
    """
    Display a reputation badge with appropriate styling based on karma value.
    """
    if karma < min_value:
        return mark_safe(f'<span class="reputation-badge reputation-level-new">{karma}</span>')
    
    if karma < 100:
        css_class = "reputation-level-new"
    elif karma < 500:
        css_class = "reputation-level-regular"
    elif karma < 1000:
        css_class = "reputation-level-established"
    elif karma < 2500:
        css_class = "reputation-level-trusted"
    elif karma < 5000:
        css_class = "reputation-level-expert"
    elif karma < 10000:
        css_class = "reputation-level-leader"
    else:
        css_class = "reputation-level-legend"
    
    return mark_safe(f'<span class="reputation-badge {css_class}">{karma}</span>')

@register.filter
def reputation_level_badge(level_name):
    """
    Display a badge for a reputation level with appropriate styling.
    """
    level_classes = {
        'New User': 'reputation-level-new',
        'Regular': 'reputation-level-regular',
        'Established Member': 'reputation-level-established',
        'Trusted Contributor': 'reputation-level-trusted',
        'Expert': 'reputation-level-expert',
        'Community Leader': 'reputation-level-leader',
        'Legend': 'reputation-level-legend'
    }
    
    css_class = level_classes.get(level_name, 'reputation-level-new')
    return mark_safe(f'<span class="reputation-level {css_class}">{level_name}</span>')
