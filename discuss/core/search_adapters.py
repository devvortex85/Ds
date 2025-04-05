from watson import search as watson
from .models import Post, Comment, Community, Profile
from django.contrib.auth.models import User

# Register models for watson search

# Register Post model with higher priority (1.0)
watson.register(
    Post,
    fields=(
        "title", 
        "content",
        "author__username",
        "community__name",
    ),
    store=("created_at", "author_id", "community_id", "post_type"),
    search_index="post_index",
    title_field="title",
    priority=1.0,
)

# Register Comment model with medium priority (0.8)
watson.register(
    Comment,
    fields=(
        "content", 
        "author__username",
        "post__title",
    ),
    store=("created_at", "author_id", "post_id"),
    search_index="comment_index",
    title_field="content",
    priority=0.8,
)

# Register Community model with medium priority (0.7)
watson.register(
    Community,
    fields=(
        "name", 
        "description",
    ),
    store=("created_at",),
    search_index="community_index",
    title_field="name",
    priority=0.7,
)

# Register Profile model with lower priority (0.5)
watson.register(
    Profile,
    fields=(
        "user__username", 
        "bio",
        "display_name",
    ),
    store=("karma",),
    search_index="profile_index",
    title_field="display_name",
    priority=0.5,
)

# Register User model with lowest priority (0.4)
watson.register(
    User,
    fields=(
        "username", 
        "email", 
        "first_name", 
        "last_name"
    ),
    search_index="user_index",
    title_field="username",
    priority=0.4,
)