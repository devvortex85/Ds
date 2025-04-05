from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django_countries.fields import CountryField
from taggit.managers import TaggableManager

class Profile(models.Model):
    REPUTATION_LEVELS = [
        (0, 'New User'),
        (100, 'Regular'),
        (500, 'Established Member'),
        (1000, 'Trusted Contributor'),
        (2500, 'Expert'),
        (5000, 'Community Leader'),
        (10000, 'Legend'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    karma = models.IntegerField(default=0)
    country = CountryField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    display_name = models.CharField(max_length=50, blank=True)
    
    # User interests as tags
    interests = TaggableManager(blank=True, verbose_name="Interests", 
                               help_text="A comma-separated list of topics you're interested in")
    
    def __str__(self):
        return f'{self.user.username} Profile'
        
    def update_karma(self):
        """Calculate and update karma based on post and comment votes"""
        # Get points from posts (1 point per upvote, -1 per downvote)
        post_upvotes = sum([
            post.votes.filter(value=1).count() for post in self.user.posts.all()
        ])
        post_downvotes = sum([
            post.votes.filter(value=-1).count() for post in self.user.posts.all()
        ])
        
        # Get points from comments (1 point per upvote, -1 per downvote)
        comment_upvotes = sum([
            comment.votes.filter(value=1).count() for comment in self.user.comments.all()
        ])
        comment_downvotes = sum([
            comment.votes.filter(value=-1).count() for comment in self.user.comments.all()
        ])
        
        # Post creation bonus (2 points per post)
        post_creation_karma = self.user.posts.count() * 2
        
        # Comment creation bonus (1 point per comment)
        comment_creation_karma = self.user.comments.count() * 1
        
        # Calculate total karma
        self.karma = (post_upvotes - post_downvotes) + (comment_upvotes - comment_downvotes) + post_creation_karma + comment_creation_karma
        
        # Ensure karma is never negative for new users
        if self.karma < 0 and self.user.date_joined.date() > (timezone.now().date() - timezone.timedelta(days=30)):
            self.karma = 0
            
        self.save()
        
    def get_reputation_level(self):
        """Return the user's reputation level based on karma"""
        level_name = self.REPUTATION_LEVELS[0][1]  # Default level
        
        for karma_threshold, name in self.REPUTATION_LEVELS:
            if self.karma >= karma_threshold:
                level_name = name
            else:
                break
                
        return level_name
    
    def get_reputation_progress(self):
        """Return progress to the next reputation level"""
        current_level_karma = 0
        next_level_karma = float('inf')
        
        # Find current and next level thresholds
        for i, (karma_threshold, _) in enumerate(self.REPUTATION_LEVELS):
            if self.karma >= karma_threshold:
                current_level_karma = karma_threshold
                if i < len(self.REPUTATION_LEVELS) - 1:
                    next_level_karma = self.REPUTATION_LEVELS[i+1][0]
            else:
                break
        
        # If at max level
        if next_level_karma == float('inf'):
            return 100
        
        # Calculate progress percentage
        progress = ((self.karma - current_level_karma) / (next_level_karma - current_level_karma)) * 100
        return min(100, max(0, progress))  # Ensure between 0-100%

# Create a Profile for each new user
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

class Community(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(max_length=500)
    members = models.ManyToManyField(User, related_name='communities')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('community_detail', kwargs={'pk': self.pk})
    
    class Meta:
        verbose_name_plural = "Communities"

class Post(models.Model):
    POST_TYPE_CHOICES = [
        ('text', 'Text'),
        ('link', 'Link'),
    ]
    
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    post_type = models.CharField(max_length=4, choices=POST_TYPE_CHOICES, default='text')
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='posts')
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('post_detail', kwargs={'pk': self.pk})
    
    @property
    def vote_count(self):
        up_votes = self.votes.filter(value=1).count()
        down_votes = self.votes.filter(value=-1).count()
        return up_votes - down_votes
    
    class Meta:
        ordering = ['-created_at']

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    
    def __str__(self):
        return f'Comment by {self.author.username} on {self.post.title}'
    
    @property
    def vote_count(self):
        up_votes = self.votes.filter(value=1).count()
        down_votes = self.votes.filter(value=-1).count()
        return up_votes - down_votes
    
    class Meta:
        ordering = ['created_at']

class Vote(models.Model):
    VOTE_CHOICES = [
        (1, 'Upvote'),
        (-1, 'Downvote'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='votes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='votes', null=True, blank=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='votes', null=True, blank=True)
    value = models.SmallIntegerField(choices=VOTE_CHOICES)
    
    def __str__(self):
        target = self.post if self.post else self.comment
        return f'{self.get_value_display()} by {self.user.username} on {target}'
    
    class Meta:
        # Ensure a user can only vote once on a post or comment
        constraints = [
            models.UniqueConstraint(fields=['user', 'post'], name='unique_post_vote', condition=models.Q(post__isnull=False)),
            models.UniqueConstraint(fields=['user', 'comment'], name='unique_comment_vote', condition=models.Q(comment__isnull=False)),
        ]
