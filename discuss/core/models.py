from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    
    def __str__(self):
        return f'{self.user.username} Profile'

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
