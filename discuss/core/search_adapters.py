from watson import search as watson
from django.conf import settings
from django.db import models
from .models import Post, Comment, Community, Profile
from django.contrib.auth.models import User
import logging

logger = logging.getLogger(__name__)

def register_search_models():
    """
    Register models with Watson for search functionality
    This is a wrapper function to allow for proper error handling and logging
    """
    try:
        logger.info("Registering models with Watson search")
        
        # First, try to unregister models to avoid duplication errors
        # Wrap each in try/except since they might not be registered yet
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
            title_field="username",
            priority=0.4,
        )
        
        # Check if we have entries in the index
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM watson_searchentry")
                count = cursor.fetchone()[0]
                
            if count == 0:
                logger.info("Search index is empty, building initial index")
                # Use the Django management command to rebuild the index
                from django.core.management import call_command
                call_command('buildwatson')
                logger.info("Search index built")
        except Exception as e:
            logger.warning(f"Could not check search index: {e}")
            # Try to create tables and rebuild index
            try:
                from django.core.management import call_command
                call_command('buildwatson')
                logger.info("Search index created")
            except Exception as e2:
                logger.error(f"Failed to build search index: {e2}")
                
        logger.info("Successfully registered models with Watson search")
        return True
    except Exception as e:
        logger.error(f"Error registering models with Watson: {e}")
        return False

# Attempt to register models when this module is imported
register_search_models()