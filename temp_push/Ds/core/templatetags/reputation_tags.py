from django import template
from django.utils.safestring import mark_safe
from django_countries.fields import Country

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

@register.filter
def get_item(dictionary, key):
    """
    Get an item from a dictionary using key.
    Used for checking user votes on posts/comments.
    """
    if dictionary is None:
        return None
    return dictionary.get(key)

@register.filter
def country_flag(user):
    """
    Display a country flag for a user if they have a country set in their profile.
    """
    if not hasattr(user, 'profile') or not user.profile.country:
        return ''
    
    country = user.profile.country
    country_name = Country(country).name
    
    return mark_safe(
        f'<img src="{country.flag}" alt="{country_name}" '
        f'title="{country_name}" class="country-flag" '
        f'style="height: 10px; width: auto; margin-left: 3px; margin-right: 2px; vertical-align: baseline; display: inline-block;">'
    )
