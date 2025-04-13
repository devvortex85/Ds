from django import template
from core.models import Profile
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def get_reputation_level(user):
    """
    Get the current reputation level of a user based on their karma.
    
    Usage:
    {{ user|get_reputation_level }}
    """
    if user.is_anonymous:
        return "Guest"
    
    try:
        profile = user.profile
        return profile.get_reputation_level()
    except (Profile.DoesNotExist, AttributeError):
        return "New User"

@register.filter
def get_reputation_progress(user):
    """
    Get the progress to the next reputation level as a percentage.
    
    Usage:
    {{ user|get_reputation_progress }}
    """
    if user.is_anonymous:
        return 0
    
    try:
        profile = user.profile
        return profile.get_reputation_progress()
    except (Profile.DoesNotExist, AttributeError):
        return 0

@register.filter
def reputation_badge(user_or_karma):
    """
    Generate an HTML badge for user reputation level.
    Can be given either a user object or a karma integer value.
    
    Usage:
    {{ user|reputation_badge }}
    {{ karma_value|reputation_badge }}
    """
    try:
        # Handle if we're given a karma value directly
        if isinstance(user_or_karma, int):
            karma = user_or_karma
            # Get the reputation level based on karma
            level = "New User"
            if karma >= 10000:
                level = "Legend"
            elif karma >= 5000:
                level = "Community Leader"
            elif karma >= 2500:
                level = "Expert"
            elif karma >= 1000:
                level = "Trusted Contributor"
            elif karma >= 500:
                level = "Established Member"
            elif karma >= 100:
                level = "Regular"
        # Handle user object
        elif hasattr(user_or_karma, 'is_anonymous'):
            if user_or_karma.is_anonymous:
                return ""
            profile = user_or_karma.profile
            level = profile.get_reputation_level()
            karma = profile.karma
        else:
            return ""
        
        # Determine badge style based on karma
        badge_class = "bg-secondary"  # Default badge style
        
        if karma >= 10000:  # Legend
            badge_class = "bg-danger"
        elif karma >= 5000:  # Community Leader
            badge_class = "bg-warning text-dark"
        elif karma >= 2500:  # Expert
            badge_class = "bg-info text-dark"
        elif karma >= 1000:  # Trusted Contributor
            badge_class = "bg-primary"
        elif karma >= 500:   # Established Member
            badge_class = "bg-success"
        elif karma >= 100:   # Regular
            badge_class = "bg-light text-dark"
        
        return mark_safe(f'<span class="badge {badge_class} ms-1">{level}</span>')
    except (Profile.DoesNotExist, AttributeError, TypeError):
        return ""