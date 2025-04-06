document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM loaded - initializing Discuss app features");
    
    // Set up comment replies
    setupCommentReplies();
    
    // Set up AJAX voting
    setupAjaxVoting();
    
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
            e.stopPropagation();
            
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
        button.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const commentId = this.getAttribute('data-comment-id');
            const replyForm = document.getElementById(`reply-form-${commentId}`);
            if (replyForm) {
                replyForm.style.display = 'none';
            }
        });
    });
}

function setupAjaxVoting() {
    // For post votes
    const postVoteButtons = document.querySelectorAll('a[href*="vote/post"]');
    postVoteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Only process authenticated user clicks
            if (this.href.includes('login')) {
                window.location.href = this.href;
                return;
            }
            
            const voteUrl = this.href;
            fetch(voteUrl, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                // Update the vote count display
                const postId = data.post_id;
                const voteCountElement = document.getElementById(`post-${postId}-votes`);
                if (voteCountElement) {
                    voteCountElement.textContent = data.vote_count;
                }
                
                // Update active state of vote buttons
                const upvoteButtons = document.querySelectorAll(`a[href*="vote/post/${postId}/upvote"]`);
                const downvoteButtons = document.querySelectorAll(`a[href*="vote/post/${postId}/downvote"]`);
                
                upvoteButtons.forEach(btn => {
                    if (data.user_vote === 1) {
                        btn.classList.add('active');
                    } else {
                        btn.classList.remove('active');
                    }
                });
                
                downvoteButtons.forEach(btn => {
                    if (data.user_vote === -1) {
                        btn.classList.add('active');
                    } else {
                        btn.classList.remove('active');
                    }
                });
            })
            .catch(error => {
                console.error('Error:', error);
            });
        });
    });
    
    // For comment votes
    const commentVoteButtons = document.querySelectorAll('a[href*="vote/comment"]');
    commentVoteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Only process authenticated user clicks
            if (this.href.includes('login')) {
                window.location.href = this.href;
                return;
            }
            
            const voteUrl = this.href;
            fetch(voteUrl, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                // Update the vote count display
                const commentId = data.comment_id;
                const commentElement = document.getElementById(`comment-${commentId}`);
                if (commentElement) {
                    const voteCountElement = commentElement.querySelector('.vote-count');
                    if (voteCountElement) {
                        voteCountElement.textContent = data.vote_count;
                    }
                    
                    // Update vote button styles
                    const upvoteBtn = commentElement.querySelector('a[href*="upvote"]');
                    const downvoteBtn = commentElement.querySelector('a[href*="downvote"]');
                    
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
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
        });
    });
}
