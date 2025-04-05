from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def reputation_badge(karma, min_value=0):
    """
    Display a reputation badge with appropriate styling based on karma value.
    """
    if karma < min_value:
        return mark_safe(f'<span class="badge bg-secondary reputation-badge">{karma}</span>')
    
    if karma < 100:
        color = "secondary"
        css_class = "reputation-level-new"
    elif karma < 500:
        color = "info"
        css_class = "reputation-level-regular"
    elif karma < 1000:
        color = "primary"
        css_class = "reputation-level-established"
    elif karma < 2500:
        color = "warning"
        css_class = "reputation-level-trusted"
    elif karma < 5000:
        color = "success"
        css_class = "reputation-level-expert"
    elif karma < 10000:
        color = "purple"
        css_class = "reputation-level-leader"
    else:
        color = "danger"
        css_class = "reputation-level-legend"
    
    return mark_safe(f'<span class="badge bg-{color} reputation-badge">{karma}</span>')

@register.filter
def reputation_level_badge(level_name):
    """
    Display a badge for a reputation level with appropriate styling.
    """
    level_colors = {
        'New User': 'secondary reputation-level-new',
        'Regular': 'info reputation-level-regular',
        'Established Member': 'primary reputation-level-established',
        'Trusted Contributor': 'warning reputation-level-trusted',
        'Expert': 'success reputation-level-expert',
        'Community Leader': 'purple reputation-level-leader',
        'Legend': 'danger reputation-level-legend'
    }
    
    css_class = level_colors.get(level_name, 'secondary reputation-level-new')
    return mark_safe(f'<span class="badge bg-{css_class} reputation-level">{level_name}</span>')
