from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q, Count
from django.http import JsonResponse
from django.core.paginator import Paginator

from .models import Profile, Community, Post, Comment, Vote
from .forms import (
    UserRegisterForm, UserUpdateForm, ProfileUpdateForm,
    CommunityForm, TextPostForm, LinkPostForm, CommentForm, SearchForm
)

def home(request):
    posts = Post.objects.annotate(comment_count=Count('comments')).order_by('-created_at')
    
    paginator = Paginator(posts, 10)  # Show 10 posts per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get the communities the user is a member of
    user_communities = []
    popular_communities = Community.objects.annotate(member_count=Count('members')).order_by('-member_count')[:5]
    
    if request.user.is_authenticated:
        user_communities = request.user.communities.all()
    
    search_form = SearchForm()
    
    context = {
        'page_obj': page_obj,
        'user_communities': user_communities,
        'popular_communities': popular_communities,
        'search_form': search_form,
    }
    return render(request, 'core/index.html', context)

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
    
    context = {
        'profile_user': user,
        'posts': posts,
        'comments': comments,
        'communities': communities,
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

def community_detail(request, pk):
    community = get_object_or_404(Community, pk=pk)
    posts = Post.objects.filter(community=community).annotate(comment_count=Count('comments')).order_by('-created_at')
    
    paginator = Paginator(posts, 10)  # Show 10 posts per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    is_member = False
    if request.user.is_authenticated:
        is_member = community.members.filter(id=request.user.id).exists()
    
    context = {
        'community': community,
        'page_obj': page_obj,
        'is_member': is_member,
    }
    return render(request, 'core/community_detail.html', context)

@login_required
def join_community(request, pk):
    community = get_object_or_404(Community, pk=pk)
    community.members.add(request.user)
    messages.success(request, f'You have joined {community.name}!')
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
    comments = post.comments.all()
    
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
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
            messages.success(request, 'Your comment has been added!')
    
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
