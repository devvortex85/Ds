document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM loaded - initializing Discuss app features");
    
    // Set up comment replies
    setupCommentReplies();
    
    // Set up AJAX voting for posts and comments
    setupVoting();
    
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
            
            // Hide all other reply forms first
            document.querySelectorAll('.reply-form').forEach(form => {
                if (form.id !== `reply-form-${commentId}`) {
                    form.style.display = 'none';
                }
            });
            
            // Toggle this reply form
            if (replyForm) {
                replyForm.style.display = replyForm.style.display === 'none' ? 'block' : 'none';
                
                // Focus on the textarea if showing the form
                if (replyForm.style.display === 'block') {
                    const textarea = replyForm.querySelector('textarea');
                    if (textarea) {
                        textarea.focus();
                    }
                }
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
}

function setupVoting() {
    // AJAX for post votes
    const postVoteButtons = document.querySelectorAll('.post-content .vote-btn');
    
    postVoteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            // Only prevent default if the user is authenticated
            // (otherwise we want to redirect to login)
            if (this.classList.contains('upvote-btn') || this.classList.contains('downvote-btn')) {
                e.preventDefault();
                
                const url = this.getAttribute('href');
                fetch(url, {
                    method: 'GET',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                })
                .then(response => response.json())
                .then(data => {
                    // Update the vote count
                    const voteCountElement = this.parentElement.querySelector('.vote-count');
                    if (voteCountElement) {
                        voteCountElement.textContent = data.vote_count;
                    }
                    
                    // Update vote button classes
                    const voteType = this.classList.contains('upvote-btn') ? 1 : -1;
                    const otherButton = this.classList.contains('upvote-btn') 
                        ? this.parentElement.querySelector('.downvote-btn')
                        : this.parentElement.querySelector('.upvote-btn');
                    
                    // If the vote was added, add 'voted' class
                    // If the vote was removed, remove 'voted' class
                    if (data.message === 'Vote recorded.') {
                        this.classList.add('voted');
                        if (otherButton) {
                            otherButton.classList.remove('voted');
                        }
                    } else if (data.message === 'Vote removed.') {
                        this.classList.remove('voted');
                    } else if (data.message === 'Vote updated.') {
                        this.classList.add('voted');
                        if (otherButton) {
                            otherButton.classList.remove('voted');
                        }
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                });
            }
        });
    });
    
    // AJAX for comment votes (both top-level and nested)
    const commentVoteButtons = document.querySelectorAll('.list-group-item .vote-btn, .reply .vote-btn');
    
    commentVoteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            // Only prevent default if the user is authenticated
            if (this.classList.contains('upvote-btn') || this.classList.contains('downvote-btn')) {
                e.preventDefault();
                
                const url = this.getAttribute('href');
                fetch(url, {
                    method: 'GET',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                })
                .then(response => response.json())
                .then(data => {
                    // Update the vote count
                    const voteCountElement = this.parentElement.querySelector('.vote-count');
                    if (voteCountElement) {
                        voteCountElement.textContent = data.vote_count;
                    }
                    
                    // Update vote button classes
                    const voteType = this.classList.contains('upvote-btn') ? 1 : -1;
                    const otherButton = this.classList.contains('upvote-btn') 
                        ? this.parentElement.querySelector('.downvote-btn')
                        : this.parentElement.querySelector('.upvote-btn');
                    
                    // If the vote was added, add 'voted' class
                    // If the vote was removed, remove 'voted' class
                    if (data.message === 'Vote recorded.') {
                        this.classList.add('voted');
                        if (otherButton) {
                            otherButton.classList.remove('voted');
                        }
                    } else if (data.message === 'Vote removed.') {
                        this.classList.remove('voted');
                    } else if (data.message === 'Vote updated.') {
                        this.classList.add('voted');
                        if (otherButton) {
                            otherButton.classList.remove('voted');
                        }
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                });
            }
        });
    });
}
