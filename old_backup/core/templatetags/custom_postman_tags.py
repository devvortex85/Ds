from django import template
from django.utils.translation import gettext_lazy as _

register = template.Library()

@register.filter
def or_me(value, user):
    """
    Displays the username, or 'me' if the user is the logged in user.
    
    Args:
        value: The username to display or a user object
        user: The current logged in user
        
    Returns:
        str: Either the username or translated "me"
    """
    if hasattr(value, 'username'):
        if value.username == user.username:
            return _("me")
        else:
            return value.username
    else:
        if value == user.username:
            return _("me")
        else:
            return value