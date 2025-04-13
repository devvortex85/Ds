from django import template
from django.db.models import Q

register = template.Library()

@register.simple_tag
def unread_message_count(user):
    """
    Return the count of unread messages for a user
    """
    if not user.is_authenticated:
        return 0
    
    try:
        from postman.models import Message
        return Message.objects.inbox_unread_count(user)
    except ImportError:
        return 0