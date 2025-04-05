// Main JavaScript for Discuss app

document.addEventListener('DOMContentLoaded', function() {
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
            // For now, we're using the server-side vote handling
            // AJAX implementation can be added later
        });
    });
}

// Function to set up comment reply functionality
function setupCommentReplies() {
    // Reply toggle buttons
    const replyToggles = document.querySelectorAll('.reply-toggle');
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
            
            // Toggle the current reply form
            if (replyForm) {
                replyForm.style.display = replyForm.style.display === 'none' ? 'block' : 'none';
                
                // Focus on the textarea if the form is visible
                if (replyForm.style.display === 'block') {
                    const textarea = replyForm.querySelector('textarea');
                    if (textarea) {
                        textarea.focus();
                    }
                }
            }
        });
    });
    
    // Cancel reply buttons
    const cancelReplyButtons = document.querySelectorAll('.cancel-reply');
    cancelReplyButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const commentId = this.getAttribute('data-comment-id');
            const replyForm = document.getElementById(`reply-form-${commentId}`);
            if (replyForm) {
                replyForm.style.display = 'none';
            }
        });
    });
}
