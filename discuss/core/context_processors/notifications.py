from core.models import Notification

def notification_count(request):
    """
    Context processor to add unread notification count for authenticated users
    """
    context = {}
    
    if request.user.is_authenticated:
        context['unread_notification_count'] = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).count()
    else:
        context['unread_notification_count'] = 0
    
    return context
