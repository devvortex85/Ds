from django import template
from django.contrib.auth.models import User
from core.models import Notification, Payment

register = template.Library()

@register.filter
def or_me(user, other_user):
    """
    Return 'me' if user == other_user, otherwise return the other_user's username
    """
    if user == other_user:
        return 'me'
    return other_user.username if hasattr(other_user, 'username') else str(other_user)

@register.simple_tag(takes_context=True)
def get_unread_notification_count(context):
    """Return the count of unread notifications for the current user"""
    user = context['user']
    if user.is_authenticated:
        return Notification.objects.filter(recipient=user, is_read=False).count()
    return 0

@register.simple_tag(takes_context=True)
def get_user_donations(context):
    """Return the user's donation history"""
    user = context['user']
    if user.is_authenticated:
        return Payment.objects.filter(user=user).order_by('-created_at')
    return []

@register.filter
def pretty_money(amount):
    """Format a money amount nicely with $ and 2 decimal places"""
    if amount is None:
        return "$0.00"
    return "${:.2f}".format(float(amount))
