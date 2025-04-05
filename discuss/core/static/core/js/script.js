// Main JavaScript for Discuss app

document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded - initializing Discuss app features');
    
    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize AJAX voting if enabled
    setupAjaxVoting();
    
    // Initialize comment reply functionality
    setupCommentReplies();
});

// Function to set up AJAX voting
function setupAjaxVoting() {
    const voteButtons = document.querySelectorAll('.vote-btn');
    
    voteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Skip if not authenticated (will redirect to login)
            if (this.getAttribute('href').includes('login')) {
                window.location.href = this.getAttribute('href');
                return;
            }
            
            const url = this.getAttribute('href');
            const voteCount = this.closest('.vote-column').querySelector('.vote-count');
            const isUpvote = this.classList.contains('upvote-btn');
            const isDownvote = this.classList.contains('downvote-btn');
            
            // Make the AJAX request
            fetch(url, {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                console.log('Vote response:', data);
                
                // Update the vote count
                if (voteCount) {
                    voteCount.textContent = data.vote_count;
                }
                
                // Handle the upvote/downvote styling
                if (isUpvote || isDownvote) {
                    const upvoteBtn = this.closest('.vote-column').querySelector('.upvote-btn');
                    const downvoteBtn = this.closest('.vote-column').querySelector('.downvote-btn');
                    
                    // Reset both buttons
                    upvoteBtn?.classList.remove('voted');
                    downvoteBtn?.classList.remove('voted');
                    
                    // Set the active button if vote wasn't removed
                    if (data.message !== 'Vote removed.') {
                        this.classList.add('voted');
                    }
                }
            })
            .catch(error => {
                console.error('Error voting:', error);
            });
        });
    });
}

// Function to set up comment reply functionality
function setupCommentReplies() {
    console.log('Setting up comment replies');
    
    // Reply toggle buttons
    const replyToggles = document.querySelectorAll('.reply-toggle');
    console.log('Found reply toggles:', replyToggles.length);
    
    replyToggles.forEach(toggle => {
        toggle.addEventListener('click', function(e) {
            e.preventDefault();
            const commentId = this.getAttribute('data-comment-id');
            console.log('Reply clicked for comment:', commentId);
            
            const replyForm = document.getElementById(`reply-form-${commentId}`);
            
            // Hide all other reply forms first
            document.querySelectorAll('.reply-form').forEach(form => {
                if (form.id !== `reply-form-${commentId}`) {
                    form.style.display = 'none';
                }
            });
            
            // Toggle the current reply form
            if (replyForm) {
                replyForm.style.display = replyForm.style.display === 'none' || replyForm.style.display === '' ? 'block' : 'none';
                console.log('Toggled reply form display to:', replyForm.style.display);
                
                // Focus on the textarea if the form is visible
                if (replyForm.style.display === 'block') {
                    const textarea = replyForm.querySelector('textarea');
                    if (textarea) {
                        textarea.focus();
                    }
                }
            } else {
                console.error('Reply form not found for comment:', commentId);
            }
        });
    });
    
    // Cancel reply buttons
    const cancelReplyButtons = document.querySelectorAll('.cancel-reply');
    console.log('Found cancel buttons:', cancelReplyButtons.length);
    
    cancelReplyButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const commentId = this.getAttribute('data-comment-id');
            console.log('Cancel clicked for comment:', commentId);
            
            const replyForm = document.getElementById(`reply-form-${commentId}`);
            if (replyForm) {
                replyForm.style.display = 'none';
                
                // Clear the textarea
                const textarea = replyForm.querySelector('textarea');
                if (textarea) {
                    textarea.value = '';
                }
            }
        });
    });
}
