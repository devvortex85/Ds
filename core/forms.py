from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile, Community, Post, Comment

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()
    
    class Meta:
        model = User
        fields = ['username', 'email']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio']

class CommunityForm(forms.ModelForm):
    class Meta:
        model = Community
        fields = ['name', 'description']
        
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Community name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Community description', 'rows': 4}),
        }

class TextPostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content']
        
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Post title'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Post content', 'rows': 6}),
        }
    
class LinkPostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'url']
        
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Post title'}),
            'url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'URL'}),
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Write a comment...', 'rows': 3}),
        }

class SearchForm(forms.Form):
    query = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search...'}),
    )
