from django import template
from django.db.models import Q, Count
from django.utils.safestring import mark_safe
from django.forms import widgets
import os

register = template.Library()

@register.simple_tag
def get_unread_notification_count(user):
    """
    Return the count of unread notifications for a user.
    This is a placeholder implementation until a proper notification system is built.
    
    Args:
        user: The user to get notification counts for
        
    Returns:
        int: The number of unread notifications
    """
    if not user or not user.is_authenticated:
        return 0
        
    # For now, return 0 as we don't have a full notification system yet
    # In a real implementation, we would query the notification model
    return 0
    
@register.simple_tag
def unread_message_count(user):
    """
    Return the count of unread messages for a user from django-postman.
    
    Args:
        user: The user to get message counts for
        
    Returns:
        int: The number of unread messages
    """
    if not user or not user.is_authenticated:
        return 0
        
    # Import here to avoid circular imports
    try:
        from postman.models import Message
        return Message.objects.inbox_unread_count(user)
    except ImportError:
        return 0

@register.filter
def class_name(obj):
    """
    Return the class name of an object
    
    Usage:
    {{ object|class_name }}
    
    Example:
    {% if object|class_name == 'User' %}
        <!-- do something -->
    {% endif %}
    """
    return obj.__class__.__name__