from taggit.models import Tag
from django.db.models import Count

def popular_tags(request):
    """
    Add popular tags to the template context for all views
    """
    # Get top tags with usage count
    tags = Tag.objects.annotate(num_times=Count('taggit_taggeditem_items')).order_by('-num_times')[:15]
    
    # If no tags exist or less than 3 tags, add default popular ones
    default_tags = []
    existing_tag_names = [tag.name for tag in tags]
    
    # Default popular tags
    default_tag_names = ['news', 'tech', 'politics']
    
    # Check if any default tags are missing and should be added to the display
    for tag_name in default_tag_names:
        if tag_name not in existing_tag_names:
            # For display purposes only - we'll handle creation in the models
            default_tags.append({
                'name': tag_name,
                'slug': tag_name,
                'num_times': 0
            })
    
    # If we have default tags to add and actual tags are less than 15
    if default_tags and len(tags) < 15:
        # Convert queryset to list if needed
        if not isinstance(tags, list):
            tags = list(tags)
        # Add default tags
        for default_tag in default_tags:
            tags.append(default_tag)
    
    return {
        'all_tags': tags,
        'default_tag_names': default_tag_names,
    }