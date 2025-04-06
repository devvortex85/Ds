from taggit.models import Tag


def popular_tags(request):
    """
    Context processor that provides the most frequently used tags
    """
    # Get the top 10 most popular tags
    top_tags = Tag.objects.most_common()[:10]
    
    return {
        'popular_tags': top_tags,
    }