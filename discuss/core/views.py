from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count, Q, Sum
from django.utils import timezone
from django.http import JsonResponse, HttpResponseForbidden, HttpResponseRedirect
from django.urls import reverse
from taggit.models import Tag
from watson import search as watson
from payments import get_payment_model, RedirectNeeded
from decimal import Decimal

from .models import Profile, Community, Post, Comment, Vote, Notification, Payment
from .forms import (UserRegisterForm, UserUpdateForm, ProfileUpdateForm, 
                   CommunityForm, TextPostForm, LinkPostForm, CommentForm, SearchForm,
                   DonationForm)
from .filters import PostFilter

def get_unread_notification_count(user):
    """Helper function to get unread notification count for a user"""
    if user.is_authenticated:
        try:
            return Notification.objects.filter(recipient=user, is_read=False).count()
        except:
            return 0
    return 0

@login_required
def notifications_list(request):
    """View to display all notifications for the current user"""
    notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')
    
    context = {
        'notifications': notifications,
        'unread_notification_count': get_unread_notification_count(request.user)
    }
    
    return render(request, 'core/notifications.html', context)

@login_required
def mark_notification_read(request, pk):
    """View to mark a notification as read"""
    notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
    
    if request.method == 'POST':
        notification.is_read = True
        notification.save()
        messages.success(request, 'Notification marked as read.')
    
    return redirect('notifications_list')

@login_required
def mark_all_notifications_read(request):
    """View to mark all notifications as read"""
    if request.method == 'POST':
        Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
        messages.success(request, 'All notifications marked as read.')
    
    return redirect('notifications_list')

def home(request, template='core/index.html', extra_context=None):
    """
    Homepage view showing a list of posts with various filtering options
    """
    # Get query parameters
    community_id = request.GET.get('community')
    tag_slug = request.GET.get('tag')
    sort = request.GET.get('sort', 'recent')
    
    # Start with all posts
    posts = Post.objects.all()
    
    # Filter by community if specified
    if community_id:
        try:
            community = Community.objects.get(id=community_id)
            posts = posts.filter(community=community)
            active_community = community
        except Community.DoesNotExist:
            active_community = None
    else:
        active_community = None
    
    # Filter by tag if specified
    active_tag = None
    if tag_slug:
        try:
            tag = Tag.objects.get(slug=tag_slug)
            posts = posts.filter(tags__slug=tag_slug)
            active_tag = tag
        except Tag.DoesNotExist:
            pass
    
    # Always annotate posts with comment count
    posts = posts.annotate(comment_count_anno=Count('comments'))
    
    # Apply sorting
    if sort == 'popular':
        posts = posts.annotate(vote_count_sum=Sum('votes__value')).order_by('-vote_count_sum')
    elif sort == 'comments':
        posts = posts.order_by('-comment_count_anno')
    elif sort == 'oldest':
        posts = posts.order_by('created_at')
    else:  # Default to 'recent'
        posts = posts.order_by('-created_at')
    
    # Get top communities
    top_communities = Community.objects.annotate(
        member_count=Count('members')
    ).order_by('-member_count')[:5]
    
    # Get popular tags
    popular_tags = Tag.objects.annotate(
        num_times=Count('taggit_taggeditem_items')
    ).order_by('-num_times')[:10]
    
    # Get unread notification count for the current user
    unread_notification_count = get_unread_notification_count(request.user)
    
    context = {
        'posts': posts,
        'top_communities': top_communities,
        'popular_tags': popular_tags,
        'active_community': active_community,
        'active_tag': active_tag,
        'active_sort': sort,
        'unread_notification_count': unread_notification_count,
    }
    
    # Add any extra context if provided
    if extra_context:
        context.update(extra_context)
    
    return render(request, template, context)

def register(request):
    """
    User registration view
    """
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    
    return render(request, 'core/register.html', {'form': form})

def profile(request, username):
    """
    View a user's profile
    """
    user = get_object_or_404(User, username=username)
    profile = get_object_or_404(Profile, user=user)
    
    # Get user's posts and comments
    posts = Post.objects.filter(author=user).annotate(comment_count_anno=Count('comments')).order_by('-created_at')
    posts_count = posts.count()
    comments = Comment.objects.filter(author=user).order_by('-created_at')
    comments_count = comments.count()
    comments_count = comments.count()
    
    # Get user's communities
    communities = user.communities.all()
    communities_count = communities.count()
    
    # Calculate karma breakdown
    post_karma = Vote.objects.filter(post__author=user).aggregate(Sum('value'))['value__sum'] or 0
    comment_karma = Vote.objects.filter(comment__author=user).aggregate(Sum('value'))['value__sum'] or 0
    
    # Get reputation information
    reputation_level = profile.get_reputation_level()
    reputation_progress = profile.get_reputation_progress()
    
    context = {
        'posts_count': posts_count,
        'comments_count': comments_count,
        'communities_count': communities_count,
        'user_profile': user,
        'profile': profile,
        'posts': posts,
        'comments': comments,
        'communities': communities,
        'post_karma': post_karma,
        'comment_karma': comment_karma,
        'reputation_level': reputation_level,
        'reputation_progress': reputation_progress,
        'profile_user': user,  # Added for template compatibility
        'unread_notification_count': get_unread_notification_count(request.user)
    }
    
    return render(request, 'core/profile.html', context)

@login_required
def edit_profile(request):
    """
    Edit user's profile
    """
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
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'unread_notification_count': get_unread_notification_count(request.user)
    }
    
    return render(request, 'core/edit_profile.html', context)

def community_list(request):
    """
    List all communities
    """
    # Get all communities and annotate with member count
    communities = Community.objects.annotate(
        member_count=Count('members')
    ).order_by('-member_count')
    
    # Get user's communities if authenticated
    if request.user.is_authenticated:
        user_communities = request.user.communities.all()
    else:
        user_communities = Community.objects.none()
    
    context = {
        'communities': communities,
        'user_communities': user_communities,
        'unread_notification_count': get_unread_notification_count(request.user)
    }
    
    return render(request, 'core/community_list.html', context)

@login_required
def create_community(request):
    """
    Create a new community
    """
    if request.method == 'POST':
        form = CommunityForm(request.POST)
        if form.is_valid():
            community = form.save()
            # Add creator as a member
            community.members.add(request.user)
            messages.success(request, f'Community "{community.name}" has been created!')
            return redirect('community_detail', pk=community.pk)
    else:
        form = CommunityForm()
    
    return render(request, 'core/create_community.html', {'form': form})

def community_detail(request, pk, template='core/community_detail.html', extra_context=None):
    """
    View a community and its posts
    """
    community = get_object_or_404(Community, pk=pk)
    
    # Fetch posts with annotated comment_count
    posts = Post.objects.filter(community=community).annotate(
        comment_count_anno=Count('comments')
    ).order_by('-created_at')
    
    # Check if user is a member
    is_member = request.user.is_authenticated and community.members.filter(id=request.user.id).exists()
    
    # Get member count
    member_count = community.members.count()
    
    # Get user's votes on posts
    user_post_votes = {}
    if request.user.is_authenticated:
        post_votes = Vote.objects.filter(user=request.user, post__in=posts)
        for vote in post_votes:
            user_post_votes[vote.post_id] = vote.value
    
    context = {
        'community': community,
        'posts': posts,
        'page_obj': posts,  # Adding this for pagination in template
        'is_member': is_member,
        'member_count': member_count,
        'user_post_votes': user_post_votes,
        'unread_notification_count': get_unread_notification_count(request.user)
    }
    
    # Add any extra context if provided
    if extra_context:
        context.update(extra_context)
    
    print(f"DEBUG: Found {posts.count()} posts in community {community.name}")
    
    return render(request, template, context)

@login_required
def join_community(request, pk):
    """
    Join a community
    """
    community = get_object_or_404(Community, pk=pk)
    community.members.add(request.user)
    messages.success(request, f'You have joined the community "{community.name}"')
    return redirect('community_detail', pk=pk)

@login_required
def leave_community(request, pk):
    """
    Leave a community
    """
    community = get_object_or_404(Community, pk=pk)
    community.members.remove(request.user)
    messages.success(request, f'You have left the community "{community.name}"')
    return redirect('community_detail', pk=pk)

@login_required
def create_text_post(request, community_id):
    """
    Create a new text post
    """
    community = get_object_or_404(Community, pk=community_id)
    
    # Check if user is a member
    if not community.members.filter(id=request.user.id).exists():
        messages.error(request, 'You must be a member of the community to post')
        return redirect('community_detail', pk=community_id)
    
    if request.method == 'POST':
        form = TextPostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.community = community
            post.post_type = 'text'
            post.save()
            
            # Save the tags
            form.save_m2m()
            
            # Check for mentions in the content
            if post.content:
                Notification.create_mention_notifications(
                    user=request.user,
                    content=post.content,
                    post=post
                )
            
            messages.success(request, 'Your post has been created!')
            return redirect('post_detail', pk=post.pk)
    else:
        form = TextPostForm()
    
    context = {
        'form': form,
        'community': community,
        'post_type': 'text',
        'unread_notification_count': get_unread_notification_count(request.user)
    }
    
    return render(request, 'core/create_post.html', context)

@login_required
def create_link_post(request, community_id):
    """
    Create a new link post
    """
    community = get_object_or_404(Community, pk=community_id)
    
    # Check if user is a member
    if not community.members.filter(id=request.user.id).exists():
        messages.error(request, 'You must be a member of the community to post')
        return redirect('community_detail', pk=community_id)
    
    if request.method == 'POST':
        form = LinkPostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.community = community
            post.post_type = 'link'
            post.save()
            
            # Save the tags
            form.save_m2m()
            
            # Check for mentions in the title
            Notification.create_mention_notifications(
                user=request.user,
                content=post.title,
                post=post
            )
            
            messages.success(request, 'Your post has been created!')
            return redirect('post_detail', pk=post.pk)
    else:
        form = LinkPostForm()
    
    context = {
        'form': form,
        'community': community,
        'post_type': 'link',
        'unread_notification_count': get_unread_notification_count(request.user)
    }
    
    return render(request, 'core/create_post.html', context)

def post_detail(request, pk):
    """
    View a post and its comments
    """
    post = get_object_or_404(Post, pk=pk)
    
    # Get all root comments (no parent) and prefetch all descendants for the nested structure
    comments = Comment.objects.filter(post=post, parent=None).order_by('created_at')
    
    # Calculate total comments including replies
    total_comments_count = Comment.objects.filter(post=post).count()
    
    # Get user's vote on this post if authenticated
    user_post_vote = None
    user_comment_votes = {}
    if request.user.is_authenticated:
        try:
            user_post_vote = Vote.objects.get(user=request.user, post=post).value
        except Vote.DoesNotExist:
            pass
            
        # Get all comment votes for this user and post in one query
        comment_votes = Vote.objects.filter(
            user=request.user,
            comment__post=post
        ).select_related('comment')
        
        # Create a dictionary of comment_id -> vote_value for easy lookup in template
        for vote in comment_votes:
            user_comment_votes[vote.comment.id] = vote.value
    
    # Create a new comment form
    if request.method == 'POST' and request.user.is_authenticated:
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.author = request.user
            
            # Check if it's a reply to another comment
            parent_id = request.POST.get('parent_id')
            if parent_id:
                try:
                    parent_comment = Comment.objects.get(id=parent_id)
                    new_comment.parent = parent_comment
                except Comment.DoesNotExist:
                    pass
            
            new_comment.save()
            messages.success(request, 'Your comment has been added!')
            return redirect('post_detail', pk=post.pk)
    else:
        comment_form = CommentForm()
    
    # Get related posts from the same community
    related_posts = Post.objects.filter(
        community=post.community
    ).exclude(id=post.id).order_by('-created_at')[:5]
    
    context = {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
        'user_post_vote': user_post_vote,
        'user_comment_votes': user_comment_votes,
        'total_comments_count': total_comments_count,
        'related_posts': related_posts,
        'unread_notification_count': get_unread_notification_count(request.user) if request.user.is_authenticated else 0
    }
    
    return render(request, 'core/post_detail.html', context)

@login_required
def delete_post(request, pk):
    """
    Delete a post
    """
    post = get_object_or_404(Post, pk=pk)
    
    # Check if user is the author
    if post.author != request.user:
        return HttpResponseForbidden("You can't delete someone else's post")
    
    if request.method == 'POST':
        community_id = post.community.id
        post.delete()
        messages.success(request, 'Your post has been deleted!')
        return redirect('community_detail', pk=community_id)
    
    return render(request, 'core/confirm_delete_post.html', {'post': post})

@login_required
def add_comment(request, post_id):
    """
    Add a comment to a post
    """
    post = get_object_or_404(Post, pk=post_id)
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            
            # Check if it's a reply to another comment
            parent_id = request.POST.get('parent_id')
            if parent_id:
                try:
                    parent_comment = Comment.objects.get(id=parent_id)
                    comment.parent = parent_comment
                except Comment.DoesNotExist:
                    pass
            
            comment.save()
            
            # Create reply notification
            reply_notification = Notification.create_reply_notification(comment)
            
            # Create mention notifications
            mention_notifications = Notification.create_mention_notifications(
                user=request.user,
                content=comment.content,
                comment=comment
            )
            
            # If AJAX request, return a JSON response
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Comment added successfully',
                    'comment_id': comment.id,
                })
            
            # Otherwise redirect to the post detail page with fragment to the new comment
            messages.success(request, 'Your comment has been added!')
            url = reverse('post_detail', kwargs={'pk': post_id}) + f'#comment-{comment.id}'
            return redirect(url)
    
    # If we get here, there was an error
    return redirect('post_detail', pk=post_id)

@login_required
def delete_comment(request, pk):
    """
    Delete a comment
    """
    comment = get_object_or_404(Comment, pk=pk)
    
    # Check if user is the author
    if comment.author != request.user:
        return HttpResponseForbidden("You can't delete someone else's comment")
    
    if request.method == 'POST':
        post_id = comment.post.id
        comment.delete()
        messages.success(request, 'Your comment has been deleted!')
        return redirect('post_detail', pk=post_id)
    
    return render(request, 'core/confirm_delete_comment.html', {'comment': comment})

@login_required
def vote_post(request, pk, vote_type):
    """
    Vote on a post (upvote or downvote)
    """
    post = get_object_or_404(Post, pk=pk)
    
    # Determine vote value
    vote_value = 1 if vote_type == 'upvote' else -1
    
    # Check if user has already voted on this post
    try:
        vote = Vote.objects.get(user=request.user, post=post)
        
        # If same vote type, remove the vote (toggle off)
        if vote.value == vote_value:
            vote.delete()
        else:
            # If different vote type, update the vote
            vote.value = vote_value
            vote.save()
            # Create a notification for the vote if it's an upvote
            if vote_value == 1:
                Notification.create_vote_notification(vote)
    except Vote.DoesNotExist:
        # Create a new vote
        vote = Vote.objects.create(user=request.user, post=post, value=vote_value)
        # Create a notification for the vote if it's an upvote
        if vote_value == 1:
            Notification.create_vote_notification(vote)
    
    # Update the author's karma
    post.author.profile.update_karma()
    
    # Check if this is an AJAX request
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # Get the current vote count
        current_vote_count = post.vote_count
        
        # Get the user's current vote
        user_vote = 0
        try:
            vote = Vote.objects.get(user=request.user, post=post)
            user_vote = vote.value
        except Vote.DoesNotExist:
            pass
        
        # Return JSON response
        return JsonResponse({
            'post_id': post.id,
            'vote_count': current_vote_count,
            'user_vote': user_vote
        })
    
    # For non-AJAX requests, redirect back to the referring page
    next_url = request.GET.get('next', '')
    if not next_url:
        next_url = reverse('post_detail', kwargs={'pk': pk})
    
    # Add fragment identifier if present (for anchors)
    fragment = ''
    if '#' in next_url:
        next_url, fragment = next_url.split('#', 1)
        fragment = '#' + fragment
    
    return redirect(next_url + fragment)

@login_required
def vote_comment(request, pk, vote_type):
    """
    Vote on a comment (upvote or downvote)
    """
    comment = get_object_or_404(Comment, pk=pk)
    
    # Determine vote value
    vote_value = 1 if vote_type == 'upvote' else -1
    
    # Check if user has already voted on this comment
    try:
        vote = Vote.objects.get(user=request.user, comment=comment)
        
        # If same vote type, remove the vote (toggle off)
        if vote.value == vote_value:
            vote.delete()
        else:
            # If different vote type, update the vote
            vote.value = vote_value
            vote.save()
            # Create a notification for the vote if it's an upvote
            if vote_value == 1:
                Notification.create_vote_notification(vote)
    except Vote.DoesNotExist:
        # Create a new vote
        vote = Vote.objects.create(user=request.user, comment=comment, value=vote_value)
        # Create a notification for the vote if it's an upvote
        if vote_value == 1:
            Notification.create_vote_notification(vote)
    
    # Update the author's karma
    comment.author.profile.update_karma()
    
    # Check if this is an AJAX request
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # Get the current vote count
        current_vote_count = comment.vote_count
        
        # Get the user's current vote
        user_vote = 0
        try:
            vote = Vote.objects.get(user=request.user, comment=comment)
            user_vote = vote.value
        except Vote.DoesNotExist:
            pass
        
        # Return JSON response
        return JsonResponse({
            'comment_id': comment.id,
            'vote_count': current_vote_count,
            'user_vote': user_vote
        })
    
    # For non-AJAX requests, redirect back to the referring page
    next_url = request.GET.get('next', '')
    if not next_url:
        next_url = reverse('post_detail', kwargs={'pk': comment.post.pk})
    
    # Add fragment identifier if present (for comment anchors)
    fragment = ''
    if '#' in next_url:
        next_url, fragment = next_url.split('#', 1)
        fragment = '#' + fragment
    else:
        # If no fragment and we're on a post detail page, add a fragment to scroll to the comment
        post_url = reverse('post_detail', kwargs={'pk': comment.post.pk})
        if post_url in next_url:
            fragment = f'#comment-{comment.id}'
    
    return redirect(next_url + fragment)

def search(request):
    """
    Perform a search across multiple models using django-watson
    with a fallback to basic Django Q objects if Watson fails.
    """
    query = request.GET.get('query', '')
    
    if not query:
        return render(request, 'core/search_results.html', {
            'query': '',
            'result_counts': {
                'total': 0,
                'posts': 0,
                'communities': 0, 
                'users': 0,
                'tags': 0,
            },
            'unread_notification_count': get_unread_notification_count(request.user) if request.user.is_authenticated else 0
        })
    
    try:
        # Search using Watson
        search_results = watson.search(query)
        
        # Separate results by model type
        posts = []
        communities = []
        users = []
        tags = []
        
        for result in search_results:
            obj = result.object
            model_name = obj.__class__.__name__
            
            if model_name == 'Post':
                posts.append(obj)
            elif model_name == 'Community':
                communities.append(obj)
            elif model_name == 'User':
                users.append(obj)
            elif model_name == 'Profile':
                # Add user from profile to ensure uniqueness
                users.append(obj.user)
        
        # Search for tags separately
        tags = Tag.objects.filter(name__icontains=query)
        
        # Count results
        result_counts = {
            'posts': len(posts),
            'communities': len(communities),
            'users': len(users),
            'tags': len(tags),
            'total': len(posts) + len(communities) + len(users) + len(tags),
        }
        
        return render(request, 'core/search_results.html', {
            'query': query,
            'posts': posts,
            'communities': communities,
            'users': users,
            'tags': tags,
            'result_counts': result_counts,
            'using_fallback': False,
            'unread_notification_count': get_unread_notification_count(request.user) if request.user.is_authenticated else 0
        })
        
    except Exception as e:
        # Fallback to basic search if Watson fails
        # Separate basic searches for each model
        posts = Post.objects.filter(
            Q(title__icontains=query) | 
            Q(content__icontains=query) | 
            Q(author__username__icontains=query)
        ).distinct()
        
        communities = Community.objects.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query)
        ).distinct()
        
        users = User.objects.filter(
            Q(username__icontains=query) | 
            Q(profile__bio__icontains=query)
        ).distinct()
        
        tags = Tag.objects.filter(name__icontains=query)
        
        # Count results
        result_counts = {
            'posts': posts.count(),
            'communities': communities.count(),
            'users': users.count(),
            'tags': tags.count(),
            'total': posts.count() + communities.count() + users.count() + tags.count(),
        }
        
        return render(request, 'core/search_results.html', {
            'query': query,
            'posts': posts,
            'communities': communities,
            'users': users,
            'tags': tags,
            'result_counts': result_counts,
            'using_fallback': True,
            'search_error': str(e),
            'unread_notification_count': get_unread_notification_count(request.user) if request.user.is_authenticated else 0
        })

def advanced_search(request):
    """Advanced search with full-text search and filtering capabilities"""
    search_query = request.GET.get('search', '')
    
    # Start with all posts
    posts = Post.objects.all()
    
    # Initialize filter
    filter = PostFilter(request.GET, queryset=posts)
    
    # Get filtered queryset
    filtered_posts = filter.qs
    
    # Get full text search results if we have a search query
    full_text_results = []
    all_tags = []
    using_fallback = False
    search_error = None
    
    if search_query:
        try:
            # Use watson search to get posts and other results
            full_text_results = watson.search(search_query)
            
            # Filter out posts as they're handled by PostFilter
            full_text_results = [r for r in full_text_results if r.object.__class__.__name__ != 'Post']
        except Exception as e:
            using_fallback = True
            search_error = str(e)
    
    # Get popular tags for the sidebar
    all_tags = Tag.objects.annotate(num_times=Count('taggit_taggeditem_items')).order_by('-num_times')[:15]
    
    context = {
        'search_query': search_query,
        'filter': filter,
        'posts': filtered_posts,
        'full_text_results': full_text_results,
        'all_tags': all_tags,
        'using_fallback': using_fallback,
        'search_error': search_error,
        'unread_notification_count': get_unread_notification_count(request.user) if request.user.is_authenticated else 0
    }
    
    return render(request, 'core/advanced_search.html', context)

# Notification view function is already defined at the top of the file

# Notification mark_as_read view function is already defined at the top of the file

# mark_all_notifications_read view function is already defined at the top of the file

@login_required
def post_votes_api(request, pk):
    """API endpoint to get post vote count and user's vote"""
    post = get_object_or_404(Post, pk=pk)
    
    # Get current vote count
    vote_count = post.vote_count
    
    # Get the user's vote on this post
    user_vote = 0
    try:
        vote = Vote.objects.get(user=request.user, post=post)
        user_vote = vote.value
    except Vote.DoesNotExist:
        pass
    
    # Return JSON response
    return JsonResponse({
        'post_id': post.id,
        'vote_count': vote_count,
        'user_vote': user_vote
    })

@login_required
def comment_votes_api(request, pk):
    """API endpoint to get comment vote count and user's vote"""
    comment = get_object_or_404(Comment, pk=pk)
    
    # Get current vote count
    vote_count = comment.vote_count
    
    # Get the user's vote on this comment
    user_vote = 0
    try:
        vote = Vote.objects.get(user=request.user, comment=comment)
        user_vote = vote.value
    except Vote.DoesNotExist:
        pass
    
    # Return JSON response
    return JsonResponse({
        'comment_id': comment.id,
        'vote_count': vote_count,
        'user_vote': user_vote
    })

# Donation/Payment Views
@login_required
def donate(request):
    """View for creating a new donation"""
    if request.method == 'POST':
        form = DonationForm(request.POST)
        if form.is_valid():
            # Get donation type and determine the amount
            donation_type = form.cleaned_data.get('donation_type', 5)
            
            # Explicitly calculate amount based on donation type or custom amount
            if donation_type == 0:  # Custom amount
                amount_value = form.cleaned_data.get('custom_amount', 5)
            else:
                # Use the donation_type value directly (5, 10, or 25)
                amount_value = donation_type
            
            # Create payment but don't save yet
            payment = form.save(commit=False)
            payment.user = request.user
            payment.variant = 'default'  # Start with the default payment processor
            payment.currency = 'USD'
            
            # Explicitly set total and amount fields
            payment.total = amount_value
            payment.amount = amount_value  # Set amount explicitly to avoid null value error
            
            # Add additional fields required by django-payments
            payment.description = f"Donation to Discuss by {request.user.username}"
            payment.billing_first_name = request.user.username
            payment.billing_last_name = getattr(request.user, 'last_name', 'User')
            payment.billing_email = request.user.email
            payment.customer_ip_address = request.META.get('REMOTE_ADDR', '')
            
            # Debug output to help diagnose issues
            print(f"DEBUG: Creating payment with amount={payment.amount}, total={payment.total}")
            
            # Save the payment record to the database
            try:
                payment.save()
                print(f"DEBUG: Payment saved successfully with ID={payment.id}")
                
                # Store the payment ID in the session for later reference
                request.session['payment_id'] = payment.id
                
                # Redirect to confirmation page
                return redirect('donation_confirmation')
            except Exception as e:
                print(f"DEBUG: Payment save failed: {str(e)}")
                messages.error(request, f"Error processing donation: {str(e)}")
                return redirect('donate')
    else:
        form = DonationForm()
        
    context = {
        'form': form,
        'unread_notification_count': get_unread_notification_count(request.user) if request.user.is_authenticated else 0
    }
    
    return render(request, 'core/donation.html', context)

@login_required
def donation_confirmation(request):
    """Confirm donation details before processing"""
    payment_id = request.session.get('payment_id')
    if not payment_id:
        messages.error(request, 'No donation in progress. Please start a new donation.')
        return redirect('donate')
    
    try:
        payment = get_object_or_404(Payment, id=payment_id)
        
        # Safeguard: ensure payment has an amount set
        if payment.amount is None or payment.amount == 0:
            payment.amount = payment.total or 5  # Fallback to 5 if total is also None
            payment.save(update_fields=['amount'])
        
        # Handle payment confirmation form submission
        if request.method == 'POST':
            # Get selected payment method from form
            variant = request.POST.get('payment_variant', 'default')
            
            # Update the payment with the selected variant
            payment.variant = variant
            
            # Double-check that amount is properly set to prevent null values
            if payment.amount is None or payment.amount == 0:
                payment.amount = payment.total or 5
                
            # Always save to ensure changes are persisted
            payment.save()
            
            try:
                # Get the payment form for the selected provider
                form = payment.get_form()
                
                # Render the payment process page with the provider's form
                return render(request, 'core/payment_process.html', {
                    'form': form,
                    'payment': payment,
                    'unread_notification_count': get_unread_notification_count(request.user)
                })
            except RedirectNeeded as redirect_to:
                # Some payment providers (like PayPal) may redirect immediately
                return redirect(str(redirect_to))
        
        # Display confirmation page for GET requests
        context = {
            'payment': payment,
            'unread_notification_count': get_unread_notification_count(request.user)
        }
        return render(request, 'core/donation_confirmation.html', context)
        
    except Payment.DoesNotExist:
        messages.error(request, 'Donation not found. Please try again.')
        return redirect('donate')

@login_required
def payment_success(request):
    """Payment success page"""
    payment_id = request.session.get('payment_id')
    if payment_id:
        payment = get_object_or_404(Payment, id=payment_id)
        
        # Clear the session
        if 'payment_id' in request.session:
            del request.session['payment_id']
            
        # Add a donation badge for the user or update their profile as needed
        # This is where you could add gamification features
            
        context = {
            'payment': payment,
            'unread_notification_count': get_unread_notification_count(request.user) if request.user.is_authenticated else 0
        }
        return render(request, 'core/payment_success.html', context)
    
    # If no payment ID in session, redirect to donation history
    return redirect('donation_history')

@login_required
def process_payment(request, payment_id):
    """Process the payment after form submission"""
    payment = get_object_or_404(Payment, id=payment_id)
    
    # Make sure the payment belongs to the current user
    if payment.user != request.user:
        messages.error(request, "Access denied. This payment doesn't belong to you.")
        return redirect('home')
    
    try:
        # Set required fields if not already set
        if payment.status is None:
            payment.status = 'waiting'
        if payment.fraud_status is None:
            payment.fraud_status = 'unknown'
        if not payment.gateway_response:
            payment.gateway_response = '{}'
        
        # Set other required fields with reasonable defaults if empty
        if payment.delivery is None:
            payment.delivery = Decimal('0.00')
        if payment.tax is None:
            payment.tax = Decimal('0.00')
        if payment.captured_amount is None:
            payment.captured_amount = Decimal('0.00')
            
        payment.save()
        
        # Process the payment
        form = payment.get_form(data=request.POST or None)
        if form.is_valid():
            # Try to process the payment with the provider
            try:
                form.save()
                return redirect('payment_success')
            except Exception as e:
                # Log the error
                print(f"Payment processing error: {str(e)}")
                # Set error on payment for debugging
                payment.error = str(e)
                payment.save(update_fields=['error'])
                messages.error(request, f"Payment error: {str(e)}")
                return redirect('payment_failure')
        else:
            # Form has validation errors
            for field in form.errors:
                for error in form.errors[field]:
                    messages.error(request, f"{field}: {error}")
            
            # Render the payment process page again with errors
            context = {
                'form': form,
                'payment': payment,
                'unread_notification_count': get_unread_notification_count(request.user)
            }
            return render(request, 'core/payment_process.html', context)
            
    except Exception as e:
        # General exception handling
        print(f"Payment exception: {str(e)}")
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('payment_failure')

@login_required
def payment_failure(request):
    """Payment failure page"""
    payment_id = request.session.get('payment_id')
    
    context = {
        'unread_notification_count': get_unread_notification_count(request.user) if request.user.is_authenticated else 0
    }
    
    if payment_id:
        try:
            payment = get_object_or_404(Payment, id=payment_id)
            context['payment'] = payment
            
            # Add debug information
            context['error_reason'] = getattr(payment, 'error', 'Unknown error')
            context['payment_status'] = payment.status
            context['payment_details'] = {
                'id': payment.id,
                'variant': payment.variant,
                'status': payment.status,
                'amount': payment.amount,
                'total': payment.total,
                'currency': payment.currency,
                'description': payment.description,
                'billing_first_name': payment.billing_first_name,
                'billing_last_name': getattr(payment, 'billing_last_name', 'N/A'),
                'billing_email': getattr(payment, 'billing_email', 'N/A'),
            }
            
            # Log error information
            print(f"DEBUG: Payment failure for payment {payment.id}")
            print(f"DEBUG: Status: {payment.status}")
            print(f"DEBUG: Error: {getattr(payment, 'error', 'Unknown error')}")
            
            # Clear the session
            if 'payment_id' in request.session:
                del request.session['payment_id']
        except Exception as e:
            context['error_reason'] = str(e)
            print(f"DEBUG: Error retrieving payment details: {str(e)}")
            
    return render(request, 'core/payment_failure.html', context)

@login_required
def donation_history(request):
    """View user's donation history"""
    payments = Payment.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'payments': payments,
        'unread_notification_count': get_unread_notification_count(request.user) if request.user.is_authenticated else 0
    }
    
    return render(request, 'core/donation_history.html', context)


def sentry_status(request):
    """
    View to show the status of Sentry integration
    """
    context = {
        'unread_notification_count': get_unread_notification_count(request.user) if request.user.is_authenticated else 0
    }
    return render(request, 'core/sentry_status.html', context)


def sentry_test(request):
    """
    Test view to verify Sentry error tracking is working.
    This view will deliberately raise an exception that should be captured by Sentry.
    """
    # Trigger a ZeroDivisionError for testing Sentry's error tracking
    division_by_zero = 1 / 0
    
    # This line will never be reached due to the exception above
    return render(request, 'core/home.html')
