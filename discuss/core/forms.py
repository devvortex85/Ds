from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile, Community, Post, Comment, Payment

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
        fields = ['bio', 'display_name', 'country', 'website', 'interests', 'avatar']
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Tell the community about yourself', 'rows': 3}),
            'display_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your display name (optional)'}),
            'country': forms.Select(attrs={'class': 'form-control form-select'}),
            'website': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Your website (optional)'}),
            'interests': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your interests separated by commas'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
        }

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
        fields = ['title', 'content', 'tags']
        
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Post title'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Post content', 'rows': 6}),
            'tags': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tags (comma separated)'}),
        }
    
class LinkPostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'url', 'tags']
        
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Post title'}),
            'url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'URL'}),
            'tags': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tags (comma separated)'}),
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Write a comment...', 'rows': 2}),
        }

class SearchForm(forms.Form):
    query = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search...'}),
    )

class DonationForm(forms.ModelForm):
    custom_amount = forms.DecimalField(
        required=False,
        min_value=1,
        max_value=1000,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Custom amount (optional)',
            'step': '0.01',
            'min': '1',
            'max': '1000'
        })
    )
    
    community = forms.ModelChoiceField(
        queryset=Community.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control form-select'}),
        help_text="Support a specific community (optional)"
    )
    
    class Meta:
        model = Payment
        fields = ['donation_type', 'custom_amount', 'community', 'description']
        widgets = {
            'donation_type': forms.RadioSelect(attrs={'class': 'donation-option'}),
            'description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Reason for donation (optional)'
            }),
        }
        
    def clean(self):
        cleaned_data = super().clean()
        donation_type = cleaned_data.get('donation_type')
        custom_amount = cleaned_data.get('custom_amount')
        
        if custom_amount:
            # If custom amount is provided, use it instead of the predefined amount
            cleaned_data['amount'] = custom_amount
        else:
            # Use the selected donation amount
            cleaned_data['amount'] = donation_type
            
        return cleaned_data
