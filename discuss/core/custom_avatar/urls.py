from django.urls import path
from avatar import views as avatar_views
from . import views

app_name = "avatar"

urlpatterns = [
    # Use our custom views for change and delete
    path("change/", views.custom_change, name="change"),
    path("delete/", views.custom_delete, name="delete"),
    
    # Keep the original views for other URLs
    path("add/", avatar_views.add, name="add"),
    path(
        "render_primary/<slug:user>/<int:width>/",
        avatar_views.render_primary,
        name="render_primary",
    ),
    path(
        "render_primary/<slug:user>/<int:width>/<int:height>/",
        avatar_views.render_primary,
        name="render_primary",
    ),
]