def notification_count(request):
    """
    Context processor that provides the count of unread notifications for the current user.
    """
    unread_count = 0
    
    if request.user.is_authenticated:
        try:
            unread_count = request.user.notifications.filter(is_read=False).count()
        except:
            # If notification model doesn't exist yet or any other error
            unread_count = 0
    
    return {
        'unread_notification_count': unread_count,
    }