from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q, Count, Sum, Case, When, F, IntegerField
from django.http import JsonResponse
from django.core.paginator import Paginator
from el_pagination.decorators import page_template
from taggit.models import Tag
# from notifications.signals import notify  # Temporarily disabled
from watson import search as watson

from .models import Profile, Community, Post, Comment, Vote
from .forms import (
    UserRegisterForm, UserUpdateForm, ProfileUpdateForm,
    CommunityForm, TextPostForm, LinkPostForm, CommentForm, SearchForm
)
from .filters import PostFilter

@page_template('core/includes/post_list.html')
def home(request, template='core/index.html', extra_context=None):
    # Initialize queryset
    posts_query = Post.objects.annotate(comment_count=Count('comments'))
    
    # Filter by tag if specified in GET parameters
    tag_slug = request.GET.get('tag')
    tag_name = None
    if tag_slug:
        posts_query = posts_query.filter(tags__slug=tag_slug)
        # Correct way to get the tag name
        tag_obj = get_object_or_404(Tag, slug=tag_slug)
        tag_name = tag_obj.name
    
    # Order the posts by creation date
    posts = posts_query.order_by('-created_at')
    
    # Get the communities the user is a member of
    user_communities = []
    popular_communities = Community.objects.annotate(member_count=Count('members')).order_by('-member_count')[:5]
    
    # Get user's votes on posts
    user_post_votes = {}
    if request.user.is_authenticated:
        user_communities = request.user.communities.all()
        post_votes = Vote.objects.filter(user=request.user, post__in=posts)
        for vote in post_votes:
            user_post_votes[vote.post_id] = vote.value
    
    search_form = SearchForm()
    
    # Get popular tags with post count
    all_tags = Tag.objects.annotate(
        num_times=Count('taggit_taggeditem_items')
    ).order_by('-num_times')[:10]  # Get top 10 tags
    
    context = {
        'posts': posts,
        'page_obj': posts,  # Adding this for pagination in template
        'user_communities': user_communities,
        'popular_communities': popular_communities,
        'user_post_votes': user_post_votes,
        'search_form': search_form,
        'all_tags': all_tags,
        'tag_name': tag_name,
    }
    
    if extra_context is not None:
        context.update(extra_context)
    
    return render(request, template, context)

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'core/register.html', {'form': form})

@login_required
def profile(request, username):
    user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=user).order_by('-created_at')
    comments = Comment.objects.filter(author=user).order_by('-created_at')
    
    # Get user's communities
    communities = user.communities.all()
    
    return render(request, 'core/profile.html', {
        'profile_user': user,
        'posts': posts,
        'comments': comments,
        'communities': communities
    })

@login_required
def edit_profile(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile', username=request.user.username)
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)
    
    return render(request, 'core/edit_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })

def community_list(request):
    communities = Community.objects.annotate(member_count=Count('members')).order_by('-member_count')
    
    # For each community, check if the user is a member
    user_memberships = {}
    if request.user.is_authenticated:
        for community in communities:
            user_memberships[community.id] = request.user.communities.filter(id=community.id).exists()
    
    return render(request, 'core/community_list.html', {
        'communities': communities,
        'user_memberships': user_memberships
    })

@login_required
def create_community(request):
    if request.method == 'POST':
        form = CommunityForm(request.POST)
        if form.is_valid():
            community = form.save()
            community.members.add(request.user)  # Add the creator as a member
            messages.success(request, f'Community {community.name} has been created!')
            return redirect('community_detail', pk=community.id)
    else:
        form = CommunityForm()
    
    return render(request, 'core/create_community.html', {'form': form})

@page_template('core/includes/post_list.html')
def community_detail(request, pk, template='core/community_detail.html', extra_context=None):
    community = get_object_or_404(Community, pk=pk)
    posts = Post.objects.filter(community=community).annotate(comment_count=Count('comments')).order_by('-created_at')
    is_member = request.user.is_authenticated and community.members.filter(id=request.user.id).exists()
    
    # Get user's votes on posts
    user_post_votes = {}
    if request.user.is_authenticated:
        post_votes = Vote.objects.filter(user=request.user, post__in=posts)
        for vote in post_votes:
            user_post_votes[vote.post_id] = vote.value
    
    # Get popular tags for this community
    community_tags = Tag.objects.filter(post__community=community).annotate(
        num_times=Count('taggit_taggeditem_items')
    ).order_by('-num_times')[:10]
    
    context = {
        'community': community,
        'posts': posts,
        'page_obj': posts,  # Adding this for pagination in template
        'is_member': is_member,
        'member_count': community.members.count(),
        'user_post_votes': user_post_votes,
        'community_tags': community_tags,
    }
    
    if extra_context is not None:
        context.update(extra_context)
    
    return render(request, template, context)

@login_required
def join_community(request, pk):
    community = get_object_or_404(Community, pk=pk)
    
    if not community.members.filter(id=request.user.id).exists():
        community.members.add(request.user)
    
    return redirect('community_detail', pk=community.id)

@login_required
def leave_community(request, pk):
    community = get_object_or_404(Community, pk=pk)
    
    if community.members.filter(id=request.user.id).exists():
        community.members.remove(request.user)
    
    return redirect('community_detail', pk=community.id)

@login_required
def create_text_post(request, community_id):
    community = get_object_or_404(Community, pk=community_id)
    
    # Check if user is a member of the community
    if not community.members.filter(id=request.user.id).exists():
        messages.error(request, 'You must be a member of this community to create a post.')
        return redirect('community_detail', pk=community_id)
    
    if request.method == 'POST':
        form = TextPostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.community = community
            post.post_type = 'text'
            post.save()
            
            # Process tags manually to ensure they're created if they don't exist
            tag_list = form.cleaned_data['tags']
            if tag_list:
                for tag_name in tag_list:
                    if not Tag.objects.filter(name=tag_name).exists():
                        # Create the tag
                        pass
                    
                    # Add tag to post
                    post.tags.add(tag_name)
            
            messages.success(request, 'Your post has been created!')
            return redirect('post_detail', pk=post.id)
    else:
        form = TextPostForm()
    
    return render(request, 'core/create_post.html', {
        'form': form,
        'community': community,
        'post_type': 'text'
    })

@login_required
def create_link_post(request, community_id):
    community = get_object_or_404(Community, pk=community_id)
    
    # Check if user is a member of the community
    if not community.members.filter(id=request.user.id).exists():
        messages.error(request, 'You must be a member of this community to create a post.')
        return redirect('community_detail', pk=community_id)
    
    if request.method == 'POST':
        form = LinkPostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.community = community
            post.post_type = 'link'
            post.save()
            
            # Process tags
            tag_list = form.cleaned_data['tags']
            if tag_list:
                for tag_name in tag_list.split(','):
                    tag_name = tag_name.strip()
                    if tag_name:
                        post.tags.add(tag_name)
            
            messages.success(request, 'Your post has been created!')
            return redirect('post_detail', pk=post.id)
    else:
        form = LinkPostForm()
    
    return render(request, 'core/create_post.html', {
        'form': form,
        'community': community,
        'post_type': 'link'
    })

def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    comments = post.comments.filter(parent=None)  # Only get top-level comments
    
    # Get the total count including replies for display
    total_comments_count = post.comments.count()
    
    # Get user's vote on this post
    user_post_vote = None
    user_comment_votes = {}
    
    if request.user.is_authenticated:
        try:
            vote = Vote.objects.get(user=request.user, post=post)
            user_post_vote = vote.value
        except Vote.DoesNotExist:
            pass
        
        # Get user's votes on comments for this post
        comment_votes = Vote.objects.filter(
            user=request.user,
            comment__post=post
        )
        for vote in comment_votes:
            user_comment_votes[vote.comment_id] = vote.value
    
    comment_form = CommentForm()
    
    return render(request, 'core/post_detail.html', {
        'post': post,
        'comments': comments,
        'total_comments_count': total_comments_count,
        'comment_form': comment_form,
        'user_post_vote': user_post_vote,
        'user_comment_votes': user_comment_votes,
    })

@login_required
def delete_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    
    # Check if user is the author of the post
    if request.user != post.author:
        messages.error(request, 'You can only delete your own posts.')
        return redirect('post_detail', pk=post.id)
    
    community_id = post.community.id
    post.delete()
    messages.success(request, 'Your post has been deleted.')
    
    return redirect('community_detail', pk=community_id)

@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            
            # Check if this is a reply to another comment
            parent_id = request.POST.get('parent_id')
            if parent_id:
                comment.parent = get_object_or_404(Comment, pk=parent_id)
            
            comment.save()
            
            # Notify post author about the new comment (if not their own post)
            # if comment.author != post.author:
            #     notify.send(
            #         comment.author,
            #         recipient=post.author,
            #         verb='commented on',
            #         target=post,
            #         description=comment.content[:50] + '...' if len(comment.content) > 50 else comment.content
            #     )
            
            messages.success(request, 'Your comment has been added.')
    
    return redirect('post_detail', pk=post_id)

@login_required
def delete_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    
    # Check if user is the author of the comment
    if request.user != comment.author:
        messages.error(request, 'You can only delete your own comments.')
        return redirect('post_detail', pk=comment.post.id)
    
    post_id = comment.post.id
    comment.delete()
    messages.success(request, 'Your comment has been deleted.')
    
    return redirect('post_detail', pk=post_id)

@login_required
def vote_post(request, pk, vote_type):
    post = get_object_or_404(Post, pk=pk)
    
    # Don't allow voting on your own posts
    if post.author == request.user:
        messages.error(request, 'You cannot vote on your own posts.')
        return redirect('post_detail', pk=post.id)
    
    value = 1 if vote_type == 'upvote' else -1
    
    try:
        # Check if user has already voted
        vote = Vote.objects.get(user=request.user, post=post)
        
        if vote.value == value:
            # If voting the same way, remove the vote
            vote.delete()
        else:
            # If voting differently, change the vote
            vote.value = value
            vote.save()
            
    except Vote.DoesNotExist:
        # If no vote exists, create a new one
        Vote.objects.create(user=request.user, post=post, value=value)
    
    # Update user karma
    post.author.profile.update_karma()
    
    # Return to the referring page (could be home, community, or post detail)
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    else:
        return redirect('post_detail', pk=post.id)

@login_required
def vote_comment(request, pk, vote_type):
    comment = get_object_or_404(Comment, pk=pk)
    
    # Don't allow voting on your own comments
    if comment.author == request.user:
        messages.error(request, 'You cannot vote on your own comments.')
        return redirect('post_detail', pk=comment.post.id)
    
    value = 1 if vote_type == 'upvote' else -1
    
    try:
        # Check if user has already voted
        vote = Vote.objects.get(user=request.user, comment=comment)
        
        if vote.value == value:
            # If voting the same way, remove the vote
            vote.delete()
        else:
            # If voting differently, change the vote
            vote.value = value
            vote.save()
            
    except Vote.DoesNotExist:
        # If no vote exists, create a new one
        Vote.objects.create(user=request.user, comment=comment, value=value)
    
    # Update user karma
    comment.author.profile.update_karma()
    
    return redirect('post_detail', pk=comment.post.id)

def search(request):
    """
    Perform a search across multiple models using django-watson
    with a fallback to basic Django Q objects if Watson fails.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    query = request.GET.get('query', '')
    posts = []
    communities = []
    users = []
    tags = []
    using_fallback = False
    
    if query:
        try:
            # Try full-text search using django-watson's unified search
            # This returns a SearchResults object with model instances from all registered models
            search_results = watson.search(query, ranking=True)
            
            # Track the number of results we find
            result_count = 0
            
            # Process search results and categorize them by model type
            for result in search_results:
                result_count += 1
                model_obj = result.object
                
                # Categorize results by model type
                if isinstance(model_obj, Post):
                    posts.append(model_obj)
                elif isinstance(model_obj, Community):
                    communities.append(model_obj)
                elif isinstance(model_obj, User):
                    users.append(model_obj)
                elif isinstance(model_obj, Profile):
                    # Add the user associated with this profile if not already added
                    if model_obj.user not in users:
                        users.append(model_obj.user)
            
            # If we got no results at all, try fallback search
            if result_count == 0:
                raise Exception("Watson search returned no results, using fallback")
                
        except Exception as e:
            # Log the error
            logger.error(f"Watson search failed: {str(e)}. Using fallback search.")
            
            # Set flag for template to show message
            using_fallback = True
            
            # Fallback search using Q objects
            posts = Post.objects.filter(
                Q(title__icontains=query) | 
                Q(content__icontains=query) |
                Q(tags__name__icontains=query)
            ).distinct().select_related('author', 'community').order_by('-created_at')
            
            communities = Community.objects.filter(
                Q(name__icontains=query) | 
                Q(description__icontains=query)
            ).order_by('name')
            
            users = User.objects.filter(
                Q(username__icontains=query) |
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query) |
                Q(profile__bio__icontains=query)
            ).distinct().select_related('profile')
        
        # Always search tags directly (not registered with Watson)
        tags = Tag.objects.filter(name__icontains=query)
    
    # Prepare search result counts for the template
    try:
        posts_count = len(posts) if isinstance(posts, list) else posts.count()
    except (TypeError, AttributeError):
        posts_count = 0
        
    try:
        communities_count = len(communities) if isinstance(communities, list) else communities.count()
    except (TypeError, AttributeError):
        communities_count = 0
        
    try:
        users_count = len(users) if isinstance(users, list) else users.count()
    except (TypeError, AttributeError):
        users_count = 0
        
    try:
        tags_count = len(tags) if isinstance(tags, list) else tags.count()
    except (TypeError, AttributeError):
        tags_count = 0
    
    result_counts = {
        'posts': posts_count,
        'communities': communities_count,
        'users': users_count,
        'tags': tags_count,
        'total': posts_count + communities_count + users_count + tags_count
    }
    
    # Add a message if we're using fallback search
    if using_fallback and request.user.is_authenticated and request.user.is_staff:
        messages.warning(request, "Using basic search instead of full-text search. Please rebuild the search index.")
    
    return render(request, 'core/search_results.html', {
        'query': query,
        'posts': posts,
        'communities': communities,
        'users': users,
        'tags': tags,
        'result_counts': result_counts,
        'using_fallback': using_fallback
    })

def advanced_search(request):
    """Advanced search with full-text search and filtering capabilities"""
    import logging
    logger = logging.getLogger(__name__)
    
    search_query = request.GET.get('search', '')
    filtered_posts = Post.objects.annotate(comment_count=Count('comments')).order_by('-created_at')
    full_text_results = []
    using_fallback = False
    search_error = None
    
    # If search query is provided, try Watson for text search
    if search_query:
        try:
            # Get full text search results across all registered models
            full_text_results = watson.search(search_query, ranking=True)
            
            # Filter posts separately to apply additional filters later
            filtered_posts = watson.filter(filtered_posts, search_query)
            
            # Check if we have results
            if len(full_text_results) == 0 and filtered_posts.count() == 0:
                # If empty results, use fallback
                raise Exception("Watson search returned no results, using fallback")
                
        except Exception as e:
            # Log the error
            logger.error(f"Watson advanced search failed: {str(e)}. Using fallback search.")
            search_error = str(e)
            
            # Set flag for template to show message
            using_fallback = True
            
            # Fallback search using Q objects for posts
            filtered_posts = Post.objects.filter(
                Q(title__icontains=search_query) | 
                Q(content__icontains=search_query) |
                Q(tags__name__icontains=search_query) |
                Q(author__username__icontains=search_query) |
                Q(community__name__icontains=search_query)
            ).distinct().annotate(comment_count=Count('comments')).order_by('-created_at')
            
            # Empty full_text_results as we can't use it in fallback mode
            full_text_results = []
    
    # Apply all filters from FilterSet
    post_filter = PostFilter(request.GET, queryset=filtered_posts)
    filtered_posts = post_filter.qs
    
    # Add a message if we're using fallback search
    if using_fallback and request.user.is_authenticated and request.user.is_staff:
        messages.warning(
            request, 
            f"Using basic search instead of full-text search. Error: {search_error}. Please rebuild the search index."
        )
    
    # Get communities for filter dropdown
    communities = Community.objects.all().order_by('name')
    
    # Get tags for filter dropdown - limit to most used tags
    tags = Tag.objects.annotate(count=Count('taggit_taggeditem_items')).order_by('-count')[:50]
    
    # Get all tags for sidebar with usage count
    all_tags = Tag.objects.annotate(
        num_times=Count('taggit_taggeditem_items')
    ).order_by('-num_times')[:30]  # Limit to top 30 tags
    
    context = {
        'filter': post_filter,
        'communities': communities,
        'tags': tags,
        'all_tags': all_tags,
        'posts': filtered_posts,
        'search_query': search_query,
        'full_text_results': full_text_results,
        'using_fallback': using_fallback,
        'search_error': search_error
    }
    
    return render(request, 'core/advanced_search.html', context)
