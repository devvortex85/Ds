from watson import search as watson
from .models import Post, Community, Profile
from django.contrib.auth.models import User

# Register models for watson search
watson.register(Post, fields=("title", "content"), store=("author", "community", "created_at", "post_type"))
watson.register(Community, fields=("name", "description"), store=("created_at",))
watson.register(User, fields=("username", "email", "first_name", "last_name"))