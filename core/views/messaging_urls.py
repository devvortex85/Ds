from django.urls import path, re_path
from django.views.decorators.csrf import csrf_exempt
from core.views.messaging_views import (
    InboxView, SentView, ArchivesView, TrashView,
    WriteView, ReplyView, MessageView
)
from postman.views import (
    ConversationView, ArchiveView, DeleteView, UndeleteView,
    MarkReadView, MarkUnreadView, IndexView
)

app_name = 'postman'
urlpatterns = [
    path('inbox/', InboxView.as_view(), name='inbox'),
    path('sent/', SentView.as_view(), name='sent'),
    path('archives/', ArchivesView.as_view(), name='archives'),
    path('trash/', TrashView.as_view(), name='trash'),
    path('write/', WriteView.as_view(), name='write'),
    path('reply/<int:message_id>/', ReplyView.as_view(), name='reply'),
    path('<int:message_id>/', MessageView.as_view(), name='view'),
    
    # Keep the original action views
    path('view/t/<int:thread_id>/', ConversationView.as_view(), name='conversation'),
    path('archive/', csrf_exempt(ArchiveView.as_view()), name='archive'),
    path('delete/', csrf_exempt(DeleteView.as_view()), name='delete'),
    path('undelete/', csrf_exempt(UndeleteView.as_view()), name='undelete'),
    path('mark-read/', MarkReadView.as_view(), name='mark-read'),
    path('mark-unread/', MarkUnreadView.as_view(), name='mark-unread'),
    path('', IndexView.as_view()),
]