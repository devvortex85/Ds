from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Home and authentication
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    
    # User profile
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/<str:username>/', views.profile, name='profile'),
    
    # Communities
    path('communities/', views.community_list, name='community_list'),
    path('communities/new/', views.create_community, name='create_community'),
    path('communities/<int:pk>/', views.community_detail, name='community_detail'),
    path('communities/<int:pk>/join/', views.join_community, name='join_community'),
    path('communities/<int:pk>/leave/', views.leave_community, name='leave_community'),
    
    # Posts
    path('posts/new/text/<int:community_id>/', views.create_text_post, name='create_text_post'),
    path('posts/new/link/<int:community_id>/', views.create_link_post, name='create_link_post'),
    path('posts/<int:pk>/', views.post_detail, name='post_detail'),
    path('posts/<int:pk>/delete/', views.delete_post, name='delete_post'),
    
    # Comments
    path('posts/<int:post_id>/comment/', views.add_comment, name='add_comment'),
    path('comments/<int:pk>/delete/', views.delete_comment, name='delete_comment'),
    
    # Voting
    path('vote/post/<int:pk>/<str:vote_type>/', views.vote_post, name='vote_post'),
    path('vote/comment/<int:pk>/<str:vote_type>/', views.vote_comment, name='vote_comment'),
    
    # API endpoints for AJAX
    path('api/post/<int:pk>/votes/', views.post_votes_api, name='post_votes_api'),
    path('api/comment/<int:pk>/votes/', views.comment_votes_api, name='comment_votes_api'),
    
    # Search
    path('search/', views.search, name='search'),
    path('search/advanced/', views.advanced_search, name='advanced_search'),
    
    # Notifications
    path('notifications/', views.notifications_list, name='notifications_list'),
    path('notifications/<int:pk>/mark-read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    
    # Donations
    path('donate/', views.donation_view, name='donate'),
    path('donate/confirm/', views.donation_confirmation, name='donation_confirmation'),
    path('donate/success/', views.payment_success, name='payment_success'),
    path('donate/failure/', views.payment_failure, name='payment_failure'),
    path('donate/history/', views.donation_history, name='donation_history'),
    
    # Django Payments URLs
    path('payments/', include('payments.urls')),
]
