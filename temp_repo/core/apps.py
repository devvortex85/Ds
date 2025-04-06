from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    
    def ready(self):
        """
        Method called by Django when the application is ready.
        We use this to initialize our default tags and register models for search.
        """
        # Import and call the ready function from __init__.py
        from . import ready
        ready()
        
        # We register models with Watson for search in search_adapters.py which is 
        # imported in the ready() function of __init__.py
