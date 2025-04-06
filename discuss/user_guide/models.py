from django.db import models

class UserGuideStep(models.Model):
    """
    Model for storing user guide steps
    """
    GUIDE_TYPE_CHOICES = [
        ('new_user', 'New User Guide'),
        ('community_creation', 'Community Creation Guide'),
        ('post_creation', 'Post Creation Guide'),
        ('commenting', 'Commenting Guide'),
    ]
    
    guide_type = models.CharField(max_length=50, choices=GUIDE_TYPE_CHOICES, default='new_user')
    order = models.IntegerField()  # This was previously named step_number
    title = models.CharField(max_length=100)
    content = models.TextField()
    element_selector = models.CharField(max_length=200, help_text="CSS selector for the element to highlight")
    position = models.CharField(max_length=20, choices=[
        ('top', 'Top'),
        ('bottom', 'Bottom'),
        ('left', 'Left'),
        ('right', 'Right'),
    ], default='bottom')
    
    class Meta:
        ordering = ['guide_type', 'order']
        unique_together = ['guide_type', 'order']
    
    def __str__(self):
        return f"{self.get_guide_type_display()} - Step {self.order}: {self.title}"