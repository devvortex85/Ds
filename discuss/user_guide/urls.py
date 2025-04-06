from django.urls import path
from . import views

urlpatterns = [
    path('user-guide/<str:guide_type>/', views.user_guide_view, name='user_guide'),
    path('user-guide/api/<str:guide_type>/', views.get_guide_steps, name='get_guide_steps'),
]