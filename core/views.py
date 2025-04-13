from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count, Q, Sum, F
from django.utils import timezone
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from taggit.models import Tag
import watson
from payments import get_payment_model, RedirectNeeded
from .models import Profile, Community, Post, Comment, Vote, Notification, Payment
from .forms import (
    UserUpdateForm, ProfileUpdateForm,
    CommunityForm, TextPostForm, LinkPostForm, CommentForm,
    SearchForm, DonationForm
)
import random
import datetime
import logging
import json
import uuid
import os
import requests
import sentry_sdk


logger = logging.getLogger(__name__)

def get_unread_notification_count(user):
    """Helper function to get unread notification count for a user"""
    if not user.is_authenticated:
        return 0
    return Notification.objects.filter(recipient=user, is_read=False).count()

@login_required
def notifications_list(request):
    """View to display all notifications for the current user"""
    notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')
    unread_count = get_unread_notification_count(request.user)
    
    return render(request, 'core/notifications_list.html', {
        'notifications': notifications,
        'unread_count': unread_count,
        'title': 'Notifications'
    })

@login_required
def mark_notification_read(request, pk):
    """View to mark a notification as read"""
    notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notification.is_read = True
    notification.save()
    
    # Check first if post exists, then check comment
    if notification.post:
        return redirect('post_detail', pk=notification.post.id)
    elif notification.comment:
        return redirect('post_detail', pk=notification.comment.post.id)
    
    return redirect('notifications_list')

@login_required
def mark_all_notifications_read(request):
    """View to mark all notifications as read"""
    Notification.objects.filter(recipient=request.user).update(is_read=True)
    messages.success(request, 'All notifications marked as read.')
    return redirect('notifications_list')

def home(request, template='core/index.html', extra_context=None):
    """
    Homepage view showing a list of posts with various filtering options
    """
    # Get posts with vote counts
    posts = Post.objects.select_related('author', 'community')\
        .prefetch_related('tags')\
        .annotate(vote_score=Count('votes', filter=Q(votes__value=1)) - 
                 Count('votes', filter=Q(votes__value=-1)))\
        .order_by('-created_at')
    
    # Prepare context
    context = {
        'posts': posts,
        'title': 'Home',
    }
    
    # Add any extra context
    if extra_context:
        context.update(extra_context)
    
    return render(request, template, context)



def profile(request, username):
    """
    View a user's profile
    """
    user = get_object_or_404(User, username=username)
    profile = Profile.objects.get(user=user)
    
    # Get user's posts with vote counts
    posts = Post.objects.filter(author=user)\
        .annotate(vote_score=Count('votes', filter=Q(votes__value=1)) - 
                 Count('votes', filter=Q(votes__value=-1)))\
        .order_by('-created_at')
    
    # Get user's comments
    comments = Comment.objects.filter(author=user).order_by('-created_at')
    
    # Get user's communities
    communities = user.communities.all()
    
    # Get overall karma (upvotes - downvotes across all content)
    post_karma = Vote.objects.filter(post__author=user).aggregate(
        karma=Sum('value', default=0)
    )['karma']
    
    comment_karma = Vote.objects.filter(comment__author=user).aggregate(
        karma=Sum('value', default=0)
    )['karma']
    
    total_karma = (post_karma or 0) + (comment_karma or 0)
    
    context = {
        'profile_user': user,
        'profile': profile,
        'posts': posts,
        'comments': comments,
        'communities': communities,
        'post_karma': post_karma or 0,
        'comment_karma': comment_karma or 0,
        'total_karma': total_karma,
        'title': f'{user.username}\'s Profile',
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
        'title': 'Edit Profile',
    }
    
    return render(request, 'core/edit_profile.html', context)

def community_list(request):
    """
    List all communities
    """
    communities = Community.objects.annotate(
        member_count=Count('members'),
        post_count=Count('posts')
    ).order_by('-created_at')
    
    return render(request, 'core/community_list.html', {
        'communities': communities,
        'title': 'Communities',
    })

@login_required
def create_community(request):
    """
    Create a new community
    """
    if request.method == 'POST':
        form = CommunityForm(request.POST)
        if form.is_valid():
            community = form.save(commit=False)
            community.creator = request.user
            community.save()
            
            # Automatically join the creator to the community
            community.members.add(request.user)
            
            messages.success(request, f'Community "{community.name}" has been created!')
            return redirect('community_detail', pk=community.pk)
    else:
        form = CommunityForm()
    
    return render(request, 'core/create_community.html', {
        'form': form,
        'title': 'Create Community',
    })

def community_detail(request, pk, template='core/community_detail.html', extra_context=None):
    """
    View a community and its posts
    """
    community = get_object_or_404(Community, pk=pk)
    
    # Get posts with vote counts for this community
    posts = Post.objects.filter(community=community)\
        .select_related('author')\
        .prefetch_related('tags')\
        .annotate(vote_score=Count('votes', filter=Q(votes__value=1)) - 
                 Count('votes', filter=Q(votes__value=-1)))\
        .order_by('-created_at')
    
    # Check if user is a member
    is_member = request.user.is_authenticated and community.members.filter(id=request.user.id).exists()
    
    # Prepare context
    context = {
        'community': community,
        'posts': posts,
        'is_member': is_member,
        'member_count': community.members.count(),
        'title': community.name,
    }
    
    # Add any extra context
    if extra_context:
        context.update(extra_context)
    
    return render(request, template, context)

@login_required
def join_community(request, pk):
    """
    Join a community
    """
    community = get_object_or_404(Community, pk=pk)
    
    if not community.members.filter(id=request.user.id).exists():
        community.members.add(request.user)
        messages.success(request, f'You have joined {community.name}!')
    
    return redirect('community_detail', pk=community.pk)

@login_required
def leave_community(request, pk):
    """
    Leave a community
    """
    community = get_object_or_404(Community, pk=pk)
    
    if community.members.filter(id=request.user.id).exists():
        community.members.remove(request.user)
        messages.success(request, f'You have left {community.name}.')
    
    return redirect('community_detail', pk=community.pk)

@login_required
def create_text_post(request, community_id):
    """
    Create a new text post
    """
    community = get_object_or_404(Community, pk=community_id)
    
    # Check if user is a member of the community
    if not community.members.filter(id=request.user.id).exists():
        messages.error(request, f'You must be a member of {community.name} to post.')
        return redirect('community_detail', pk=community.pk)
    
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
            
            messages.success(request, 'Your post has been created!')
            return redirect('post_detail', pk=post.pk)
    else:
        form = TextPostForm()
    
    return render(request, 'core/create_post.html', {
        'form': form,
        'community': community,
        'post_type': 'text',
        'title': 'Create Text Post',
    })

@login_required
def create_link_post(request, community_id):
    """
    Create a new link post
    """
    community = get_object_or_404(Community, pk=community_id)
    
    # Check if user is a member of the community
    if not community.members.filter(id=request.user.id).exists():
        messages.error(request, f'You must be a member of {community.name} to post.')
        return redirect('community_detail', pk=community.pk)
    
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
            
            messages.success(request, 'Your post has been created!')
            return redirect('post_detail', pk=post.pk)
    else:
        form = LinkPostForm()
    
    return render(request, 'core/create_post.html', {
        'form': form,
        'community': community,
        'post_type': 'link',
        'title': 'Create Link Post',
    })

def post_detail(request, pk):
    """
    View a post and its comments with Reddit-style nested comments
    """
    post = get_object_or_404(Post, pk=pk)
    
    # Update denormalized vote counts for post
    upvotes = post.votes.filter(value=1).count()
    downvotes = post.votes.filter(value=-1).count()
    post.upvote_count = upvotes
    post.downvote_count = downvotes
    post.save(update_fields=['upvote_count', 'downvote_count'])
    
    # Get user's vote for this post if they're logged in
    if request.user.is_authenticated:
        try:
            user_vote = Vote.objects.get(user=request.user, post=post)
            post.user_vote = user_vote.value
        except Vote.DoesNotExist:
            post.user_vote = None
    else:
        post.user_vote = None
    
    # Get all comments for this post
    comments = Comment.objects.filter(post=post, parent=None).order_by('created_at')
    
    # Create comment form if user is logged in
    if request.user.is_authenticated:
        if request.method == 'POST':
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.post = post
                comment.author = request.user
                comment.save()
                
                # Create notification for the post author if they're not the commenter
                if post.author != request.user:
                    Notification.objects.create(
                        recipient=post.author,
                        actor=request.user,
                        verb='commented on',
                        target=post,
                        action_object=comment,
                        link=reverse('post_detail', kwargs={'pk': post.pk})
                    )
                
                messages.success(request, 'Your comment has been added!')
                return redirect('post_detail', pk=post.pk)
        else:
            comment_form = CommentForm()
    else:
        comment_form = None
    
    # Update denormalized vote counts for comments
    for comment in comments:
        # Update denormalized vote counts
        upvotes = comment.votes.filter(value=1).count()
        downvotes = comment.votes.filter(value=-1).count()
        comment.upvote_count = upvotes
        comment.downvote_count = downvotes
        comment.save(update_fields=['upvote_count', 'downvote_count'])
        
        # Get user's vote for this comment if they're logged in
        if request.user.is_authenticated:
            try:
                user_vote = Vote.objects.get(user=request.user, comment=comment)
                comment.user_vote = user_vote.value
            except Vote.DoesNotExist:
                comment.user_vote = None
        else:
            comment.user_vote = None
        
        # Get child comments - store as an attribute without trying to assign to the related manager
        setattr(comment, 'child_comments', get_comment_children(comment, request.user, depth=0, max_depth=3))
    
    context = {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
        'title': post.title,
    }
    
    return render(request, 'core/post_detail.html', context)

def get_comment_children(comment, user, depth=0, max_depth=3):
    """
    Recursively get child comments up to a specified depth
    """
    depth += 1
    if depth > max_depth:
        # Don't fetch children beyond max_depth
        comment.has_more = Comment.objects.filter(parent=comment).exists()
        return []
    
    children = Comment.objects.filter(parent=comment).order_by('created_at')
    
    for child in children:
        # Update denormalized vote counts
        upvotes = child.votes.filter(value=1).count()
        downvotes = child.votes.filter(value=-1).count()
        child.upvote_count = upvotes
        child.downvote_count = downvotes
        child.save(update_fields=['upvote_count', 'downvote_count'])
        
        child.depth = depth
        
        # Get user's vote for this comment
        if user.is_authenticated:
            try:
                user_vote = Vote.objects.get(user=user, comment=child)
                child.user_vote = user_vote.value
            except Vote.DoesNotExist:
                child.user_vote = None
        else:
            child.user_vote = None
        
        # Get grandchildren - store as an attribute without trying to assign to the related manager
        setattr(child, 'child_comments', get_comment_children(child, user, depth, max_depth))
    
    return children

def comment_thread(request, pk):
    """
    View for displaying a continued thread of comments
    This handles deeply nested comments beyond the display limit
    """
    comment = get_object_or_404(Comment, pk=pk)
    post = comment.post
    
    # Update denormalized vote counts for comment
    upvotes = comment.votes.filter(value=1).count()
    downvotes = comment.votes.filter(value=-1).count()
    comment.upvote_count = upvotes
    comment.downvote_count = downvotes
    comment.save(update_fields=['upvote_count', 'downvote_count'])
    
    # Get user's vote for this comment if they're logged in
    if request.user.is_authenticated:
        try:
            user_vote = Vote.objects.get(user=request.user, comment=comment)
            comment.user_vote = user_vote.value
        except Vote.DoesNotExist:
            comment.user_vote = None
    else:
        comment.user_vote = None
    
    # Create comment form if user is logged in
    if request.user.is_authenticated:
        if request.method == 'POST':
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                new_comment = comment_form.save(commit=False)
                new_comment.post = post
                new_comment.author = request.user
                new_comment.parent = comment
                new_comment.save()
                
                # Create notification for the parent comment author if they're not the commenter
                if comment.author != request.user:
                    Notification.objects.create(
                        recipient=comment.author,
                        actor=request.user,
                        verb='replied to',
                        target=comment,
                        action_object=new_comment,
                        link=reverse('comment_thread', kwargs={'pk': comment.pk})
                    )
                
                messages.success(request, 'Your reply has been added!')
                return redirect('comment_thread', pk=comment.pk)
        else:
            comment_form = CommentForm()
    else:
        comment_form = None
    
    # Get child comments - store as an attribute without trying to assign to the related manager
    setattr(comment, 'child_comments', get_comment_children(comment, request.user, depth=0, max_depth=10))
    
    context = {
        'post': post,
        'comment': comment,
        'comment_form': comment_form,
        'title': f'Thread: {post.title}',
    }
    
    return render(request, 'core/comment_thread.html', context)

@login_required
def delete_post(request, pk):
    """
    Delete a post
    """
    post = get_object_or_404(Post, pk=pk)
    
    # Check if the user is the author of the post
    if post.author != request.user and not request.user.is_staff:
        messages.error(request, 'You do not have permission to delete this post.')
        return redirect('post_detail', pk=post.pk)
    
    if request.method == 'POST':
        community_id = post.community.id
        post.delete()
        messages.success(request, 'Your post has been deleted.')
        return redirect('community_detail', pk=community_id)
    
    return render(request, 'core/delete_confirm.html', {
        'object': post,
        'object_type': 'post',
        'title': 'Delete Post',
    })

@login_required
def add_comment(request, post_id):
    """
    Add a comment to a post
    """
    post = get_object_or_404(Post, pk=post_id)
    
    if request.method == 'POST':
        parent_id = request.POST.get('parent_id')
        parent = None
        
        if parent_id:
            parent = get_object_or_404(Comment, pk=parent_id)
        
        content = request.POST.get('content')
        
        if content:
            comment = Comment.objects.create(
                post=post,
                author=request.user,
                content=content,
                parent=parent
            )
            
            # Create notification for the post author if they're not the commenter
            if not parent and post.author != request.user:
                Notification.objects.create(
                    recipient=post.author,
                    actor=request.user,
                    verb='commented on',
                    target=post,
                    action_object=comment,
                    link=reverse('post_detail', kwargs={'pk': post.pk})
                )
            
            # Create notification for the parent comment author if they're not the commenter
            elif parent and parent.author != request.user:
                Notification.objects.create(
                    recipient=parent.author,
                    actor=request.user,
                    verb='replied to',
                    target=parent,
                    action_object=comment,
                    link=reverse('post_detail', kwargs={'pk': post.pk})
                )
            
            messages.success(request, 'Your comment has been added!')
            
            # Redirect to the appropriate URL based on the presence of a parent comment
            if parent:
                return redirect('comment_thread', pk=parent.pk)
            else:
                return redirect('post_detail', pk=post.pk)
    
    return redirect('post_detail', pk=post.pk)

@login_required
def delete_comment(request, pk):
    """
    Delete a comment
    """
    comment = get_object_or_404(Comment, pk=pk)
    
    # Check if the user is the author of the comment
    if comment.author != request.user and not request.user.is_staff:
        messages.error(request, 'You do not have permission to delete this comment.')
        return redirect('post_detail', pk=comment.post.pk)
    
    if request.method == 'POST':
        post_id = comment.post.id
        comment.delete()
        messages.success(request, 'Your comment has been deleted.')
        return redirect('post_detail', pk=post_id)
    
    return render(request, 'core/delete_confirm.html', {
        'object': comment,
        'object_type': 'comment',
        'title': 'Delete Comment',
    })

@login_required
def vote_post(request, pk, vote_type):
    """
    Vote on a post (upvote or downvote) using Reddit-style direct vote counting
    
    This view is protected by Django's CSRF middleware and requires login.
    It accepts both GET and POST requests to work with multiple client methods.
    """
    post = get_object_or_404(Post, pk=pk)
    
    # Determine vote value
    vote_value = 1 if vote_type == 'upvote' else -1
    
    # Check if user already voted on this post
    try:
        vote = Vote.objects.get(user=request.user, post=post)
        
        if vote.value == vote_value:
            # User is toggling their vote off
            vote.delete()
            vote_status = 'removed'
        else:
            # User is changing their vote
            vote.value = vote_value
            vote.save()
            vote_status = 'changed'
    except Vote.DoesNotExist:
        # User hasn't voted yet, create a new vote
        Vote.objects.create(user=request.user, post=post, value=vote_value)
        vote_status = 'added'
        
        # Create notification for upvotes on user's post
        if vote_value == 1 and post.author != request.user:
            Notification.objects.create(
                recipient=post.author,
                actor=request.user,
                verb='upvoted',
                target=post,
                link=reverse('post_detail', kwargs={'pk': post.pk})
            )
    
    # Get the updated vote count
    upvotes = Vote.objects.filter(post=post, value=1).count()
    downvotes = Vote.objects.filter(post=post, value=-1).count()
    vote_count = upvotes - downvotes
    
    # Determine if this is an AJAX request or a regular request
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # Return a JSON response
        return JsonResponse({
            'vote_count': vote_count,
            'vote_status': vote_status,
            'upvotes': upvotes,
            'downvotes': downvotes
        })
    else:
        # Redirect to the appropriate page
        return redirect('post_detail', pk=post.pk)

@login_required
def vote_comment(request, pk, vote_type):
    """
    Vote on a comment (upvote or downvote) using Reddit-style direct vote counting
    
    This view is protected by Django's CSRF middleware and requires login.
    It accepts both GET and POST requests to work with multiple client methods.
    """
    comment = get_object_or_404(Comment, pk=pk)
    
    # Determine vote value
    vote_value = 1 if vote_type == 'upvote' else -1
    
    # Check if user already voted on this comment
    try:
        vote = Vote.objects.get(user=request.user, comment=comment)
        
        if vote.value == vote_value:
            # User is toggling their vote off
            vote.delete()
            vote_status = 'removed'
        else:
            # User is changing their vote
            vote.value = vote_value
            vote.save()
            vote_status = 'changed'
    except Vote.DoesNotExist:
        # User hasn't voted yet, create a new vote
        Vote.objects.create(user=request.user, comment=comment, value=vote_value)
        vote_status = 'added'
        
        # Create notification for upvotes on user's comment
        if vote_value == 1 and comment.author != request.user:
            Notification.objects.create(
                recipient=comment.author,
                actor=request.user,
                verb='upvoted',
                target=comment,
                link=reverse('post_detail', kwargs={'pk': comment.post.pk}) + f'#comment-{comment.pk}'
            )
    
    # Get the updated vote count
    upvotes = Vote.objects.filter(comment=comment, value=1).count()
    downvotes = Vote.objects.filter(comment=comment, value=-1).count()
    vote_count = upvotes - downvotes
    
    # Determine if this is an AJAX request or a regular request
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # Return a JSON response
        return JsonResponse({
            'vote_count': vote_count,
            'vote_status': vote_status,
            'upvotes': upvotes,
            'downvotes': downvotes
        })
    else:
        # Redirect to the appropriate page (either post detail or comment thread)
        if comment.parent is None:
            return redirect('post_detail', pk=comment.post.pk)
        else:
            return redirect('comment_thread', pk=comment.parent.pk)

def search(request):
    """
    Perform a search across multiple models using django-watson
    with a fallback to basic Django Q objects if Watson fails.
    """
    query = request.GET.get('query', '')
    search_form = SearchForm(initial={'query': query})
    
    results = []
    result_count = 0
    
    if query:
        try:
            # Try using watson for full-text search
            results = watson.search(query)
            result_count = results.count()
        except Exception as e:
            logger.error(f"Watson search failed with error: {e}")
            
            # Fallback to basic Django search
            post_results = Post.objects.filter(
                Q(title__icontains=query) | 
                Q(content__icontains=query) |
                Q(author__username__icontains=query)
            )
            
            community_results = Community.objects.filter(
                Q(name__icontains=query) | 
                Q(description__icontains=query)
            )
            
            comment_results = Comment.objects.filter(content__icontains=query)
            
            user_results = User.objects.filter(username__icontains=query)
            
            # Combine results
            results = list(post_results) + list(community_results) + list(comment_results) + list(user_results)
            result_count = len(results)
    
    context = {
        'search_form': search_form,
        'query': query,
        'results': results,
        'result_count': result_count,
        'title': 'Search Results',
    }
    
    return render(request, 'core/search_results.html', context)

def advanced_search(request):
    """Advanced search with full-text search and filtering capabilities"""
    query = request.GET.get('query', '')
    search_form = SearchForm(initial={'query': query})
    
    community_filter = request.GET.get('community')
    tag_filter = request.GET.get('tag')
    post_type_filter = request.GET.get('post_type')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    # Get all available filter options for the form
    communities = Community.objects.all().order_by('name')
    tags = Tag.objects.all().order_by('name')
    
    results = []
    result_count = 0
    
    if query or community_filter or tag_filter or post_type_filter or date_from or date_to:
        # Start with all posts
        results = Post.objects.all()
        
        if query:
            try:
                # Try using watson for full-text search
                post_ids = [r.object_id for r in watson.search(query) if r.content_type.model_class() == Post]
                results = results.filter(id__in=post_ids)
            except Exception as e:
                logger.error(f"Watson search failed with error: {e}")
                # Fallback to basic search
                results = results.filter(
                    Q(title__icontains=query) | 
                    Q(content__icontains=query) |
                    Q(author__username__icontains=query)
                )
        
        # Apply filters
        if community_filter:
            results = results.filter(community__id=community_filter)
        
        if tag_filter:
            results = results.filter(tags__slug=tag_filter)
        
        if post_type_filter:
            results = results.filter(post_type=post_type_filter)
        
        if date_from:
            try:
                date_from_obj = datetime.datetime.strptime(date_from, '%Y-%m-%d').date()
                results = results.filter(created_at__gte=date_from_obj)
            except (ValueError, TypeError):
                pass
        
        if date_to:
            try:
                date_to_obj = datetime.datetime.strptime(date_to, '%Y-%m-%d').date()
                # Add one day to include the end date
                date_to_obj = date_to_obj + datetime.timedelta(days=1)
                results = results.filter(created_at__lte=date_to_obj)
            except (ValueError, TypeError):
                pass
        
        # Annotate with vote counts and order by newest
        results = results.select_related('author', 'community')\
            .prefetch_related('tags')\
            .annotate(vote_score=Count('votes', filter=Q(votes__value=1)) - 
                     Count('votes', filter=Q(votes__value=-1)))\
            .order_by('-created_at')
        
        result_count = results.count()
    
    context = {
        'search_form': search_form,
        'query': query,
        'results': results,
        'result_count': result_count,
        'communities': communities,
        'tags': tags,
        'community_filter': community_filter,
        'tag_filter': tag_filter,
        'post_type_filter': post_type_filter,
        'date_from': date_from,
        'date_to': date_to,
        'title': 'Advanced Search',
    }
    
    return render(request, 'core/advanced_search.html', context)

def post_votes_api(request, pk):
    """API endpoint to get post vote count and user's vote"""
    post = get_object_or_404(Post, pk=pk)
    
    # Get vote count
    upvotes = Vote.objects.filter(post=post, value=1).count()
    downvotes = Vote.objects.filter(post=post, value=-1).count()
    vote_count = upvotes - downvotes
    
    # Get user's vote for this post if they're logged in
    user_vote = None
    if request.user.is_authenticated:
        try:
            vote = Vote.objects.get(user=request.user, post=post)
            user_vote = vote.value
        except Vote.DoesNotExist:
            user_vote = None
    
    return JsonResponse({
        'vote_count': vote_count,
        'upvotes': upvotes,
        'downvotes': downvotes,
        'user_vote': user_vote
    })

def comment_votes_api(request, pk):
    """API endpoint to get comment vote count and user's vote"""
    comment = get_object_or_404(Comment, pk=pk)
    
    # Get vote count
    upvotes = Vote.objects.filter(comment=comment, value=1).count()
    downvotes = Vote.objects.filter(comment=comment, value=-1).count()
    vote_count = upvotes - downvotes
    
    # Get user's vote for this comment if they're logged in
    user_vote = None
    if request.user.is_authenticated:
        try:
            vote = Vote.objects.get(user=request.user, comment=comment)
            user_vote = vote.value
        except Vote.DoesNotExist:
            user_vote = None
    
    return JsonResponse({
        'vote_count': vote_count,
        'upvotes': upvotes,
        'downvotes': downvotes,
        'user_vote': user_vote
    })

@login_required
def donate(request):
    """View for creating a new donation"""
    if request.method == 'POST':
        form = DonationForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.user = request.user
            payment.variant = 'default'  # Using the default payment processor
            
            # Set the amount based on the selected option or custom amount
            donation_type = form.cleaned_data.get('donation_type')
            custom_amount = form.cleaned_data.get('custom_amount')
            
            if donation_type == 'custom' and custom_amount:
                payment.total = custom_amount
            elif donation_type == 'small':
                payment.total = 5.00
            elif donation_type == 'medium':
                payment.total = 10.00
            elif donation_type == 'large':
                payment.total = 25.00
            else:
                # Fallback if something goes wrong
                payment.total = 5.00
            
            payment.currency = 'USD'
            payment.status = 'waiting'
            payment.save()
            
            return redirect('donation_confirmation')
    else:
        form = DonationForm()
    
    return render(request, 'core/payment_page.html', {
        'form': form,
        'title': 'Support Discuss',
        'page_type': 'form'
    })

@login_required
def donation_confirmation(request):
    """Confirm donation details before processing"""
    # Get the most recent unprocessed payment for this user
    try:
        payment = Payment.objects.filter(
            user=request.user, 
            status='waiting'
        ).latest('created_at')
    except Payment.DoesNotExist:
        messages.error(request, 'No pending donation found.')
        return redirect('donate')
    
    if request.method == 'POST':
        # User confirmed the donation, proceed to payment processing
        return redirect('process_payment', payment_id=payment.id)
    
    return render(request, 'core/payment_page.html', {
        'payment': payment,
        'title': 'Confirm Your Donation',
        'page_type': 'confirmation',
        'footer_message': 'Your support means a lot to our community. Thank you!'
    })

@login_required
def payment_success(request):
    """Payment success page"""
    # Get the most recent completed payment for this user
    try:
        payment = Payment.objects.filter(
            user=request.user, 
            status='confirmed'
        ).latest('created_at')
    except Payment.DoesNotExist:
        payment = None
    
    return render(request, 'core/payment_page.html', {
        'payment': payment,
        'success': True,
        'title': 'Payment Successful',
        'page_type': 'result',
        'result_title': 'Thank You for Your Support!'
    })

@login_required
def process_payment(request, payment_id):
    """Process the payment after form submission"""
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)
    
    # Only process if payment is still in waiting status
    if payment.status != 'waiting':
        messages.error(request, 'This payment has already been processed.')
        return redirect('donation_history')
    
    # Get the Payment model from django-payments
    Payment = get_payment_model()
    
    # Create a payment
    payment.transaction_id = str(uuid.uuid4())
    payment.save()
    
    try:
        # Try to process the payment
        return redirect('payment_success')
    except RedirectNeeded as redirect_to:
        return redirect(str(redirect_to))
    except Exception as e:
        messages.error(request, f'Payment processing error: {str(e)}')
        payment.status = 'error'
        payment.save()
        
        # Store error information in session for the failure page
        request.session['payment_error'] = str(e)
        request.session['payment_details'] = {
            'payment_id': payment.id,
            'status': payment.status,
            'amount': str(payment.total),
            'created_at': str(payment.created_at),
        }
        
        return redirect('payment_failure')

@login_required
def payment_failure(request):
    """Payment failure page"""
    error_reason = request.session.get('payment_error', 'Unknown error')
    payment_details = request.session.get('payment_details', {})
    
    return render(request, 'core/payment_page.html', {
        'success': False,
        'title': 'Payment Failed',
        'error_reason': error_reason,
        'payment_details': payment_details,
        'page_type': 'result',
        'result_title': 'Payment Unsuccessful'
    })

@login_required
def donation_history(request):
    """View user's donation history"""
    payments = Payment.objects.filter(user=request.user).order_by('-created_at')
    
    # Calculate total donated amount
    total_donated = payments.filter(status='confirmed').aggregate(
        total=Sum('total')
    )['total'] or 0
    
    return render(request, 'core/payment_page.html', {
        'payments': payments,
        'total_donated': total_donated,
        'title': 'Your Donation History',
        'page_type': 'history',
        'container_class': 'py-5'
    })

def sentry_status(request):
    """
    View to show the status of Sentry integration
    """
    sentry_dsn = os.environ.get('SENTRY_DSN', '')
    sentry_enabled = bool(sentry_dsn and 'sentry_sdk' in globals())
    
    return render(request, 'core/sentry_status.html', {
        'sentry_enabled': sentry_enabled,
        'title': 'Sentry Status'
    })

def sentry_test(request):
    """
    Test view to verify Sentry error tracking is working.
    This view will deliberately raise an exception that should be captured by Sentry.
    """
    # Trigger a ZeroDivisionError for testing Sentry's error tracking
    division_by_zero = 1 / 0
    
    # This line will never be reached due to the exception above
    return render(request, 'core/home.html')