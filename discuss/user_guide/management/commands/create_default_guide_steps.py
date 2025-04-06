from django.core.management.base import BaseCommand
from user_guide.models import UserGuideStep

class Command(BaseCommand):
    help = 'Creates default guide steps for the user guide'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating default guide steps...'))
        
        # Create guides for different types
        self.create_new_user_guide()
        self.create_community_guide()
        self.create_post_guide()
        self.create_commenting_guide()
        
        self.stdout.write(self.style.SUCCESS('Default guide steps created successfully!'))

    def create_new_user_guide(self):
        """Create steps for the new user guide"""
        steps = [
            {
                'order': 1,
                'title': 'Welcome to Discuss!',
                'content': 'This quick guide will help you get started with the platform. Click "Next" to continue.',
                'element_selector': '.navbar-brand',
                'position': 'bottom'
            },
            {
                'order': 2,
                'title': 'Joining Communities',
                'content': 'Communities are groups dedicated to specific topics. Find and join communities you\'re interested in to see their posts.',
                'element_selector': '.nav-link[href*="communities"]',
                'position': 'bottom'
            },
            {
                'order': 3,
                'title': 'Creating Posts',
                'content': 'Once you\'ve joined a community, you can create text posts or share links with other members.',
                'element_selector': '.btn-primary[href*="create"]',
                'position': 'left'
            },
            {
                'order': 4,
                'title': 'Voting',
                'content': 'Use the upvote and downvote buttons to show your opinion on posts and comments.',
                'element_selector': '.vote-buttons',
                'position': 'right'
            },
            {
                'order': 5,
                'title': 'Your Profile',
                'content': 'Check your profile to see your posts, comments, and karma. You can also customize your profile settings.',
                'element_selector': '.nav-link[href*="profile"]',
                'position': 'bottom'
            }
        ]
        
        self._create_steps(steps, 'new_user')

    def create_community_guide(self):
        """Create steps for the community creation guide"""
        steps = [
            {
                'order': 1,
                'title': 'Creating a Community',
                'content': 'Communities are the heart of Discuss. Let\'s learn how to create your own community.',
                'element_selector': '.nav-link[href*="communities"]',
                'position': 'bottom'
            },
            {
                'order': 2,
                'title': 'Community Name',
                'content': 'Choose a name that clearly describes what your community is about. Keep it concise and memorable.',
                'element_selector': '#id_name',
                'position': 'bottom'
            },
            {
                'order': 3,
                'title': 'Community Description',
                'content': 'Write a clear description that explains the purpose of your community and what kind of content is welcome.',
                'element_selector': '#id_description',
                'position': 'top'
            },
            {
                'order': 4,
                'title': 'Managing Your Community',
                'content': 'As a community creator, you\'ll be responsible for setting the tone and moderating content.',
                'element_selector': '.btn-primary[type="submit"]',
                'position': 'right'
            },
            {
                'order': 5,
                'title': 'Growing Your Community',
                'content': 'Share your community with others and create engaging posts to attract new members.',
                'element_selector': '.card-body',
                'position': 'bottom'
            }
        ]
        
        self._create_steps(steps, 'community_creation')

    def create_post_guide(self):
        """Create steps for the post creation guide"""
        steps = [
            {
                'order': 1,
                'title': 'Creating a Post',
                'content': 'Posts are the main way to share content with your community. Let\'s learn how to create an engaging post.',
                'element_selector': '.btn-primary[href*="create"]',
                'position': 'bottom'
            },
            {
                'order': 2,
                'title': 'Post Title',
                'content': 'Write a clear, descriptive title that summarizes your post. A good title helps attract readers.',
                'element_selector': '#id_title',
                'position': 'bottom'
            },
            {
                'order': 3,
                'title': 'Post Content',
                'content': 'Share your thoughts, questions, or information in the content area. You can use Markdown formatting for rich text.',
                'element_selector': '#id_content',
                'position': 'top'
            },
            {
                'order': 4,
                'title': 'Adding Tags',
                'content': 'Tags help categorize your post and make it more discoverable. Add relevant tags separated by commas.',
                'element_selector': '#id_tags',
                'position': 'bottom'
            },
            {
                'order': 5,
                'title': 'Submitting Your Post',
                'content': 'Review your post and click Submit to share it with the community.',
                'element_selector': '.btn-primary[type="submit"]',
                'position': 'right'
            }
        ]
        
        self._create_steps(steps, 'post_creation')

    def create_commenting_guide(self):
        """Create steps for the commenting guide"""
        steps = [
            {
                'order': 1,
                'title': 'Commenting on Posts',
                'content': 'Comments let you engage with posts and other community members. Let\'s learn how to leave effective comments.',
                'element_selector': '.comment-form',
                'position': 'top'
            },
            {
                'order': 2,
                'title': 'Writing a Comment',
                'content': 'Share your thoughts, opinions, or additional information about the post. Be respectful and constructive.',
                'element_selector': '#id_content',
                'position': 'top'
            },
            {
                'order': 3,
                'title': 'Replying to Comments',
                'content': 'You can reply directly to other comments to create threaded conversations.',
                'element_selector': '.reply-button',
                'position': 'left'
            },
            {
                'order': 4,
                'title': 'Voting on Comments',
                'content': 'Upvote helpful or insightful comments, and downvote those that don\'t contribute to the discussion.',
                'element_selector': '.comment-vote-buttons',
                'position': 'right'
            },
            {
                'order': 5,
                'title': 'Mentioning Users',
                'content': 'You can mention other users by typing @ followed by their username. This will notify them about your comment.',
                'element_selector': '#id_content',
                'position': 'bottom'
            }
        ]
        
        self._create_steps(steps, 'commenting')

    def _create_steps(self, steps, guide_type):
        """
        Helper method to create steps for a specific guide type
        """
        # Delete existing steps for this guide type to avoid duplicates
        UserGuideStep.objects.filter(guide_type=guide_type).delete()
        
        # Create new steps
        for step in steps:
            UserGuideStep.objects.create(
                guide_type=guide_type,
                order=step['order'],
                title=step['title'],
                content=step['content'],
                element_selector=step['element_selector'],
                position=step['position']
            )
            
        self.stdout.write(self.style.SUCCESS(f'Created {len(steps)} steps for {guide_type} guide'))