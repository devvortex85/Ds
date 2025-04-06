document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM loaded - initializing Discuss app features");
    
    // Log any existing nested replies for debugging
    const nestedReplies = document.querySelectorAll('.nested-reply');
    console.log("Found nested replies:", nestedReplies.length);
    
    // Log nesting indicators
    const nestingIndicators = document.querySelectorAll('.nesting-indicator');
    console.log("Found nesting indicators:", nestingIndicators.length);
    
    // Log reply forms for debugging
    const replyForms = document.querySelectorAll('.reply-form');
    console.log("Found reply forms:", replyForms.length);
    replyForms.forEach(form => {
        console.log("Form ID:", form.id);
    });
    
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
                
                // If showing the form, scroll to it and focus
                if (isCurrentlyHidden) {
                    // Scroll to the form (with a small delay to ensure display change has taken effect)
                    setTimeout(() => {
                        replyForm.scrollIntoView({ behavior: 'smooth', block: 'center' });
                        
                        // Focus on the textarea
                        const textarea = replyForm.querySelector('textarea');
                        if (textarea) {
                            textarea.focus();
                        }
                    }, 50);
                }
            } else {
                console.error("Reply form not found for comment ID:", commentId);
                // Log all reply forms to debug
                const allReplyForms = document.querySelectorAll('.reply-form');
                console.log("All reply forms:", allReplyForms.length);
                allReplyForms.forEach(form => {
                    console.log("Form ID:", form.id);
                });
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
