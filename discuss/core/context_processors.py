def notification_count(request):
    """
    Context processor that provides the count of unread notifications for the current user.
    """
    unread_count = 0
    
    if request.user.is_authenticated:
        try:
            # If the user is logged in, query their unread notifications
            unread_count = request.user.notifications.filter(is_read=False).count()
        except Exception as e:
            # If there's any error, default to 0
            unread_count = 0
    
    return {
        'unread_notification_count': unread_count,
    }