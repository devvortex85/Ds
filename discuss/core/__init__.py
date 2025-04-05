# Initialize default application tags

default_app_name = 'core.apps.CoreConfig'

def create_default_tags():
    """
    Create default tags for the application if they don't exist.
    This function is called when the application is ready.
    """
    try:
        from taggit.models import Tag
        
        # Default tags to ensure exist
        default_tags = ['news', 'tech', 'politics']
        
        # Create tags if they don't exist
        for tag_name in default_tags:
            Tag.objects.get_or_create(name=tag_name, slug=tag_name)
            
        print("✓ Default tags initialized")
    except Exception as e:
        print(f"Error initializing default tags: {str(e)}")
        
# Define the ready function to be called by Django's app registry
def ready():
    """
    Function called by Django when the application is ready.
    We use this to initialize our default tags and register models for watson search.
    """
    # Avoid importing models at module level to prevent AppRegistryNotReady exception
    import django
    if django.apps.apps.ready:
        create_default_tags()
        
        # Import search adapters to register models with Watson
        try:
            # Use explicit import of registration function to avoid circular imports
            from .search_adapters import register_search_models
            success = register_search_models()
            if success:
                print("✓ Watson search adapters registered and index built")
            else:
                print("✗ Watson search registration failed")
        except Exception as e:
            print(f"Error setting up Watson search: {str(e)}")
