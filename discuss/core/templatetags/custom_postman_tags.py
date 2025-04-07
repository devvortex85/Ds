from django import template
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

register = template.Library()

@register.filter
def or_me(value, user):
    """
    Replace the username of the logged user by the translated 'me'.
    
    This is a custom implementation of the or_me filter used in django-postman 
    templates to show 'me' instead of the current user's username when viewing 
    messages.
    """
    if isinstance(value, User) and user.is_authenticated and value == user:
        return str(_('me'))
    else:
        return str(value)