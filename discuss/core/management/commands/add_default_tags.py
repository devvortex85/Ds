from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Profile, Post
from taggit.models import Tag

class Command(BaseCommand):
    help = 'Adds default tags to all existing users and posts'
    
    def handle(self, *args, **options):
        # Create the 'news' tag if it doesn't exist
        news_tag, created = Tag.objects.get_or_create(name='news', slug='news')
        
        if created:
            self.stdout.write(self.style.SUCCESS(f"Created new tag: 'news'"))
        
        # Add 'news' tag to all user profiles
        user_count = 0
        for user in User.objects.all():
            try:
                profile = user.profile
                if not profile.interests.filter(name='news').exists():
                    profile.interests.add('news')
                    user_count += 1
            except Profile.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"No profile for user {user.username}"))
        
        # Add 'news' tag to all posts that don't have it
        post_count = 0
        for post in Post.objects.all():
            if not post.tags.filter(name='news').exists():
                post.tags.add('news')
                post_count += 1
        
        self.stdout.write(self.style.SUCCESS(f"Added 'news' tag to {user_count} users and {post_count} posts"))