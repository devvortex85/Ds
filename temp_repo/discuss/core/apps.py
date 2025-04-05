from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    
    def ready(self):
        """
        Method called by Django when the application is ready.
        We use this to initialize our default tags.
        """
        # Import and call the ready function from __init__.py
        from . import ready
        ready()
