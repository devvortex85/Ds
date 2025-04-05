from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q, Count
from django.http import JsonResponse
from django.core.paginator import Paginator
from el_pagination.decorators import page_template
# from notifications.signals import notify  # Temporarily disabled

from .models import Profile, Community, Post, Comment, Vote
from .forms import (
    UserRegisterForm, UserUpdateForm, ProfileUpdateForm,
    CommunityForm, TextPostForm, LinkPostForm, CommentForm, SearchForm
)

@page_template('core/includes/post_list.html')
def home(request, template='core/index.html', extra_context=None):
    posts = Post.objects.annotate(comment_count=Count('comments')).order_by('-created_at')
    
    # Get the communities the user is a member of
    user_communities = []
    popular_communities = Community.objects.annotate(member_count=Count('members')).order_by('-member_count')[:5]
    
    if request.user.is_authenticated:
        user_communities = request.user.communities.all()
    
    search_form = SearchForm()
    
    context = {
        'posts': posts,
        'user_communities': user_communities,
        'popular_communities': popular_communities,
        'search_form': search_form,
    }
    
    if extra_context is not None:
        context.update(extra_context)
        
    return render(request, template, context)

def register(request):
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
    user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=user).order_by('-created_at')
    comments = Comment.objects.filter(author=user).order_by('-created_at')
    communities = user.communities.all()
    
    # Update the user's karma to ensure it's current
    user.profile.update_karma()
    
    # Get the user's reputation level and progress
    reputation_level = user.profile.get_reputation_level()
    reputation_progress = user.profile.get_reputation_progress()
    
    context = {
        'profile_user': user,
        'posts': posts,
        'comments': comments,
        'communities': communities,
        'reputation_level': reputation_level,
        'reputation_progress': reputation_progress,
    }
    return render(request, 'core/profile.html', context)

@login_required
def edit_profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, instance=request.user.profile)
        
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile', username=request.user.username)
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
    
    context = {
        'u_form': u_form,
        'p_form': p_form,
    }
    return render(request, 'core/edit_profile.html', context)

def community_list(request):
    communities = Community.objects.annotate(member_count=Count('members')).order_by('-member_count')
    return render(request, 'core/community_list.html', {'communities': communities})

@login_required
def create_community(request):
    if request.method == 'POST':
        form = CommunityForm(request.POST)
        if form.is_valid():
            community = form.save()
            community.members.add(request.user)
            messages.success(request, f'Community {community.name} has been created!')
            return redirect('community_detail', pk=community.pk)
    else:
        form = CommunityForm()
    return render(request, 'core/create_community.html', {'form': form})

@page_template('core/includes/post_list.html')
def community_detail(request, pk, template='core/community_detail.html', extra_context=None):
    community = get_object_or_404(Community, pk=pk)
    posts = Post.objects.filter(community=community).annotate(comment_count=Count('comments')).order_by('-created_at')
    
    is_member = False
    if request.user.is_authenticated:
        is_member = community.members.filter(id=request.user.id).exists()
    
    context = {
        'community': community,
        'posts': posts,
        'is_member': is_member,
    }
    
    if extra_context is not None:
        context.update(extra_context)
        
    return render(request, template, context)

@login_required
def join_community(request, pk):
    community = get_object_or_404(Community, pk=pk)
    community.members.add(request.user)
    messages.success(request, f'You have joined {community.name}!')
    
    # Send notification to community creator - Temporarily disabled
    # notify.send(
    #     sender=request.user,
    #     recipient=community.members.first(),  # Assuming the first member is the creator
    #     verb=f'{request.user.username} joined your community {community.name}',
    #     target=community,
    #     description=f'{request.user.username} has joined your community {community.name}',
    #     data={'url': f'/communities/{community.pk}/'}
    # )
    
    return redirect('community_detail', pk=pk)

@login_required
def leave_community(request, pk):
    community = get_object_or_404(Community, pk=pk)
    community.members.remove(request.user)
    messages.success(request, f'You have left {community.name}.')
    return redirect('community_detail', pk=pk)

@login_required
def create_text_post(request, community_id):
    community = get_object_or_404(Community, pk=community_id)
    
    # Check if user is a member of the community
    if not community.members.filter(id=request.user.id).exists():
        messages.error(request, 'You must be a member of the community to post.')
        return redirect('community_detail', pk=community_id)
    
    if request.method == 'POST':
        form = TextPostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.community = community
            post.post_type = 'text'
            post.save()
            
            # Notify community members about new post - Temporarily disabled
            # for member in community.members.exclude(id=request.user.id):
            #     notify.send(
            #         sender=request.user,
            #         recipient=member,
            #         verb=f'New post in {community.name}',
            #         target=post,
            #         description=f'{request.user.username} posted in {community.name}: {post.title}',
            #         data={'url': f'/posts/{post.pk}/'}
            #     )
                
            messages.success(request, 'Your post has been created!')
            return redirect('post_detail', pk=post.pk)
    else:
        form = TextPostForm()
    
    context = {
        'form': form,
        'community': community,
        'post_type': 'text'
    }
    return render(request, 'core/create_post.html', context)

@login_required
def create_link_post(request, community_id):
    community = get_object_or_404(Community, pk=community_id)
    
    # Check if user is a member of the community
    if not community.members.filter(id=request.user.id).exists():
        messages.error(request, 'You must be a member of the community to post.')
        return redirect('community_detail', pk=community_id)
    
    if request.method == 'POST':
        form = LinkPostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.community = community
            post.post_type = 'link'
            post.save()
            
            # Notify community members about new post - Temporarily disabled
            # for member in community.members.exclude(id=request.user.id):
            #     notify.send(
            #         sender=request.user,
            #         recipient=member,
            #         verb=f'New link in {community.name}',
            #         target=post,
            #         description=f'{request.user.username} shared a link in {community.name}: {post.title}',
            #         data={'url': f'/posts/{post.pk}/'}
            #     )
                
            messages.success(request, 'Your post has been created!')
            return redirect('post_detail', pk=post.pk)
    else:
        form = LinkPostForm()
    
    context = {
        'form': form,
        'community': community,
        'post_type': 'link'
    }
    return render(request, 'core/create_post.html', context)

def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    # Only get top-level comments (those without a parent)
    comments = post.comments.filter(parent=None).order_by('created_at')
    
    user_post_vote = None
    if request.user.is_authenticated:
        # Check if the user has voted on this post
        user_vote = Vote.objects.filter(user=request.user, post=post).first()
        if user_vote:
            user_post_vote = user_vote.value
    
    # Comment form
    if request.method == 'POST' and request.user.is_authenticated:
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
            messages.success(request, 'Your comment has been added!')
            return redirect('post_detail', pk=post.pk)
    else:
        comment_form = CommentForm()
    
    context = {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
        'user_post_vote': user_post_vote,
    }
    return render(request, 'core/post_detail.html', context)

@login_required
def delete_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    
    # Ensure the user is the author of the post
    if post.author != request.user:
        messages.error(request, 'You do not have permission to delete this post.')
        return redirect('post_detail', pk=pk)
    
    community_id = post.community.id
    post.delete()
    messages.success(request, 'Your post has been deleted.')
    return redirect('community_detail', pk=community_id)

@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    
    if request.method == 'POST':
        # Check if this is a reply to another comment
        parent_id = request.POST.get('parent_id')
        
        # Use the form if it's a top-level comment, or get content directly if it's a reply
        if parent_id:
            content = request.POST.get('content')
            if content:
                parent_comment = get_object_or_404(Comment, pk=parent_id)
                comment = Comment(
                    content=content,
                    author=request.user,
                    post=post,
                    parent=parent_comment
                )
                comment.save()
                messages.success(request, 'Your reply has been added!')
        else:
            form = CommentForm(request.POST)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.author = request.user
                comment.post = post
                comment.save()
                messages.success(request, 'Your comment has been added!')
            
            # Notify the post author about the new comment - Temporarily disabled
            # if post.author != request.user:
            #     notify.send(
            #         sender=request.user,
            #         recipient=post.author,
            #         verb=f'New comment on your post',
            #         target=post,
            #         description=f'{request.user.username} commented on your post: {post.title}',
            #         data={'url': f'/posts/{post.pk}/'}
            #     )
            
            # Notify other commenters on the post - Temporarily disabled
            # commented_users = Comment.objects.filter(post=post).exclude(
            #     author=request.user
            # ).exclude(
            #     author=post.author
            # ).values_list('author', flat=True).distinct()
            
            # for user_id in commented_users:
            #     user = User.objects.get(id=user_id)
            #     notify.send(
            #         sender=request.user,
            #         recipient=user,
            #         verb=f'New activity on a post you commented on',
            #         target=post,
            #         description=f'{request.user.username} also commented on: {post.title}',
            #         data={'url': f'/posts/{post.pk}/'}
            #     )
    
    return redirect('post_detail', pk=post_id)

@login_required
def delete_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    
    # Ensure the user is the author of the comment
    if comment.author != request.user:
        messages.error(request, 'You do not have permission to delete this comment.')
        return redirect('post_detail', pk=comment.post.pk)
    
    post_id = comment.post.id
    comment.delete()
    messages.success(request, 'Your comment has been deleted.')
    return redirect('post_detail', pk=post_id)

@login_required
def vote_post(request, pk, vote_type):
    post = get_object_or_404(Post, pk=pk)
    
    # Determine vote value
    vote_value = 1 if vote_type == 'upvote' else -1
    
    # Check if user has already voted on this post
    existing_vote = Vote.objects.filter(user=request.user, post=post).first()
    
    if existing_vote:
        if existing_vote.value == vote_value:
            # If voting the same way, remove the vote
            existing_vote.delete()
            message = 'Vote removed.'
        else:
            # If voting differently, update the vote
            existing_vote.value = vote_value
            existing_vote.save()
            message = 'Vote updated.'
    else:
        # Create a new vote
        Vote.objects.create(user=request.user, post=post, value=vote_value)
        message = 'Vote recorded.'
    
    # Update karma for the post author
    post.author.profile.update_karma()
    
    # If AJAX request, return JSON response
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'message': message,
            'vote_count': post.vote_count
        })
    
    # Otherwise redirect back to the post
    return redirect('post_detail', pk=pk)

@login_required
def vote_comment(request, pk, vote_type):
    comment = get_object_or_404(Comment, pk=pk)
    
    # Determine vote value
    vote_value = 1 if vote_type == 'upvote' else -1
    
    # Check if user has already voted on this comment
    existing_vote = Vote.objects.filter(user=request.user, comment=comment).first()
    
    if existing_vote:
        if existing_vote.value == vote_value:
            # If voting the same way, remove the vote
            existing_vote.delete()
            message = 'Vote removed.'
        else:
            # If voting differently, update the vote
            existing_vote.value = vote_value
            existing_vote.save()
            message = 'Vote updated.'
    else:
        # Create a new vote
        Vote.objects.create(user=request.user, comment=comment, value=vote_value)
        message = 'Vote recorded.'
    
    # Update karma for the comment author
    comment.author.profile.update_karma()
    
    # If AJAX request, return JSON response
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'message': message,
            'vote_count': comment.vote_count
        })
    
    # Otherwise redirect back to the post
    return redirect('post_detail', pk=comment.post.pk)

def search(request):
    query = request.GET.get('query', '')
    
    if query:
        # Search for posts
        posts = Post.objects.filter(
            Q(title__icontains=query) | 
            Q(content__icontains=query)
        ).order_by('-created_at')
        
        # Search for communities
        communities = Community.objects.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query)
        )
        
        # Search for users
        users = User.objects.filter(username__icontains=query)
    else:
        posts = []
        communities = []
        users = []
    
    context = {
        'query': query,
        'posts': posts,
        'communities': communities,
        'users': users,
        'search_form': SearchForm(initial={'query': query})
    }
    return render(request, 'core/search_results.html', context)