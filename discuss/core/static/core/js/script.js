document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM loaded - initializing Discuss app features");
    
    // Set up comment replies
    setupCommentReplies();
    
    // Initialize any tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });
});

function setupCommentReplies() {
    console.log("Setting up comment replies");
    
    // Get all reply toggle buttons
    const replyToggles = document.querySelectorAll('.reply-toggle');
    console.log("Found reply toggles:", replyToggles.length);
    
    // Add click event listener to each reply toggle
    replyToggles.forEach(toggle => {
        toggle.addEventListener('click', function(e) {
            e.preventDefault();
            const commentId = this.getAttribute('data-comment-id');
            const replyForm = document.getElementById(`reply-form-${commentId}`);
            
            console.log("Toggling reply form for comment ID:", commentId);
            console.log("Reply form element:", replyForm);
            
            // Hide all other reply forms first
            document.querySelectorAll('.reply-form').forEach(form => {
                if (form.id !== `reply-form-${commentId}`) {
                    form.style.display = 'none';
                }
            });
            
            // Toggle this reply form
            if (replyForm) {
                // Toggle visibility
                const isCurrentlyHidden = replyForm.style.display === 'none' || replyForm.style.display === '';
                replyForm.style.display = isCurrentlyHidden ? 'block' : 'none';
                
                // If showing the form, focus on the textarea
                if (isCurrentlyHidden) {
                    // Focus on the textarea
                    const textarea = replyForm.querySelector('textarea');
                    if (textarea) {
                        setTimeout(() => {
                            textarea.focus();
                        }, 50);
                    }
                }
            } else {
                console.error("Reply form not found for comment ID:", commentId);
            }
        });
    });
    
    // Get all cancel reply buttons
    const cancelButtons = document.querySelectorAll('.cancel-reply');
    console.log("Found cancel buttons:", cancelButtons.length);
    
    // Add click event to each cancel button
    cancelButtons.forEach(button => {
        button.addEventListener('click', function() {
            const commentId = this.getAttribute('data-comment-id');
            const replyForm = document.getElementById(`reply-form-${commentId}`);
            if (replyForm) {
                replyForm.style.display = 'none';
            }
        });
    });

    // Add AJAX voting to avoid page refresh
    setupAjaxVoting();
}

function setupAjaxVoting() {
    // Get all vote buttons
    const voteButtons = document.querySelectorAll('.vote-btn, .upvote-btn, .downvote-btn');
    
    voteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Only handle clicks for authenticated users (skip login redirects)
            if (this.getAttribute('href').includes('login')) {
                window.location = this.getAttribute('href');
                return;
            }
            
            const voteUrl = this.getAttribute('href');
            
            // Make AJAX request to vote URL
            fetch(voteUrl, {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                }
            })
            .then(response => {
                if (response.ok) {
                    // Update UI based on the element voted
                    if (voteUrl.includes('vote_post')) {
                        // Extract post ID from URL
                        const postId = voteUrl.split('/').filter(part => part !== '')[2];
                        updatePostVoteUI(postId);
                    } else if (voteUrl.includes('vote_comment')) {
                        // Extract comment ID from URL
                        const commentId = voteUrl.split('/').filter(part => part !== '')[2];
                        updateCommentVoteUI(commentId);
                    }
                } else {
                    console.error('Error voting:', response.status);
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
        });
    });
}

function updatePostVoteUI(postId) {
    // Fetch the updated post vote count
    fetch(`/api/post/${postId}/votes/`)
    .then(response => response.json())
    .then(data => {
        // Update vote count
        const voteCountElement = document.querySelector(`#post-${postId}-votes`);
        if (voteCountElement) {
            voteCountElement.textContent = data.vote_count;
        }
        
        // Update vote button styles
        const upvoteBtn = document.querySelector(`a[href*="vote_post/${postId}/upvote"]`);
        const downvoteBtn = document.querySelector(`a[href*="vote_post/${postId}/downvote"]`);
        
        if (upvoteBtn) {
            if (data.user_vote === 1) {
                upvoteBtn.classList.add('active');
            } else {
                upvoteBtn.classList.remove('active');
            }
        }
        
        if (downvoteBtn) {
            if (data.user_vote === -1) {
                downvoteBtn.classList.add('active');
            } else {
                downvoteBtn.classList.remove('active');
            }
        }
    })
    .catch(error => {
        console.error('Error updating post vote UI:', error);
    });
}

function updateCommentVoteUI(commentId) {
    // Fetch the updated comment vote count
    fetch(`/api/comment/${commentId}/votes/`)
    .then(response => response.json())
    .then(data => {
        // Find the vote count element for this comment
        const voteCountElement = document.querySelector(`#comment-${commentId} .vote-count`);
        if (voteCountElement) {
            voteCountElement.textContent = data.vote_count;
        }
        
        // Update vote button styles
        const upvoteBtn = document.querySelector(`a[href*="vote_comment/${commentId}/upvote"]`);
        const downvoteBtn = document.querySelector(`a[href*="vote_comment/${commentId}/downvote"]`);
        
        if (upvoteBtn) {
            if (data.user_vote === 1) {
                upvoteBtn.classList.add('voted');
            } else {
                upvoteBtn.classList.remove('voted');
            }
        }
        
        if (downvoteBtn) {
            if (data.user_vote === -1) {
                downvoteBtn.classList.add('voted');
            } else {
                downvoteBtn.classList.remove('voted');
            }
        }
    })
    .catch(error => {
        console.error('Error updating comment vote UI:', error);
    });
}
