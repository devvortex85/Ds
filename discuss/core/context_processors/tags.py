from taggit.models import Tag
from django.db.models import Count

def popular_tags(request):
    """
    Add popular tags to the template context for all views
    """
    # Get top tags with usage count
    tags = Tag.objects.annotate(num_times=Count('taggit_taggeditem_items')).order_by('-num_times')[:15]
    
    return {
        'all_tags': tags,
    }