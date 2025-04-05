from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.db import connection
from core.models import Post, Comment, Community, Profile
import traceback
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Rebuilds the search index for Watson using a reliable approach'

    def add_arguments(self, parser):
        parser.add_argument('--force', action='store_true', help='Force rebuilding of search index')

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== Rebuilding search index ==='))
        
        # First, check if watson is installed and working properly
        try:
            from watson import search as watson
            has_watson = True
        except ImportError:
            has_watson = False
            raise CommandError("Django-watson is not installed. Please install it first.")
        
        # Delete all entries in the search_index to start fresh
        try:
            with connection.cursor() as cursor:
                self.stdout.write("Clearing existing search index...")
                cursor.execute("DELETE FROM watson_searchentry")
                self.stdout.write(self.style.SUCCESS("Search index cleared."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error clearing search index: {e}"))
            if 'relation "watson_searchentry" does not exist' in str(e):
                self.stdout.write("Trying to continue by building index...")
            else:
                raise CommandError(f"Could not clear search index: {e}")
        
        # Use direct registration approach for all searchable models
        try:
            self.stdout.write("Registering models with search engine...")
            
            # Unregister models first to avoid duplication errors
            self.stdout.write("Unregistering existing model registrations...")
            try:
                watson.unregister(Post)
            except:
                pass
            try:
                watson.unregister(Comment) 
            except:
                pass
            try:
                watson.unregister(Community)
            except:
                pass
            try:
                watson.unregister(User)
            except:
                pass
            try:
                watson.unregister(Profile)
            except:
                pass
                
            # Register models for search
            self.stdout.write("Registering models...")
            
            # Register Post model
            watson.register(
                Post,
                fields=("title", "content", "url", "author__username", "community__name"),
                store=("created_at", "author_id", "community_id", "post_type"),
                title_field="title",
            )
            
            # Register Comment model
            watson.register(
                Comment,
                fields=("content", "author__username", "post__title"),
                store=("created_at", "author_id", "post_id"),
                title_field="content",
            )
            
            # Register Community model
            watson.register(
                Community,
                fields=("name", "description"),
                store=("created_at",),
                title_field="name",
            )
            
            # Register User model
            watson.register(
                User,
                fields=("username", "email", "first_name", "last_name"),
                title_field="username",
            )
            
            # Register Profile model
            watson.register(
                Profile,
                fields=("bio", "display_name"),
                store=("karma",),
                title_field="display_name",
            )
            
            self.stdout.write(self.style.SUCCESS("Models registered successfully."))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error registering models: {e}"))
            traceback.print_exc()
            raise CommandError(f"Failed to register models: {e}")
                
        # Now try to rebuild the index with Watson's built-in command
        try:
            self.stdout.write("Building search index...")
            # Use the buildwatson management command
            from django.core.management import call_command
            call_command('buildwatson', verbosity=3)
            
            # Count entries in search index
            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM watson_searchentry")
                count = cursor.fetchone()[0]
            
            self.stdout.write(self.style.SUCCESS(f'Search index rebuilt successfully. {count} entries indexed.'))
            
            if count == 0:
                self.stdout.write(self.style.WARNING("No entries were indexed. Check your models and data."))
                
                # Check if we have any data
                post_count = Post.objects.count()
                comment_count = Comment.objects.count()
                community_count = Community.objects.count()
                user_count = User.objects.count()
                
                self.stdout.write(f"Current database has: {post_count} posts, {comment_count} comments, "
                                 f"{community_count} communities, {user_count} users")
                
                if post_count + comment_count + community_count + user_count == 0:
                    self.stdout.write(self.style.WARNING("Database appears to be empty. Add some data first."))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error building search index: {e}"))
            traceback.print_exc()
            raise CommandError(f"Failed to build search index: {e}")