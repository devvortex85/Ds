// Discuss - Main JavaScript functionality

document.addEventListener('DOMContentLoaded', function() {
    
    // Enable Bootstrap tooltips
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
    
    // Setup AJAX for CSRF protection with Django
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    
    const csrftoken = getCookie('csrftoken');
    
    // Setup AJAX headers
    function setupAjaxHeaders() {
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                }
            }
        });
    }
    
    setupAjaxHeaders();
    
    // Handle voting via AJAX
    setupVoting();
    
    // Handle dynamic comment form submissions
    setupCommentForms();
    
    // Set active nav item
    setActiveNavItem();
    
    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        $('.alert-dismissible').fadeOut('slow');
    }, 5000);
});

// Voting functionality
function setupVoting() {
    // Use event delegation for vote buttons
    document.addEventListener('click', function(event) {
        // Check if click was on a vote button
        if (event.target.closest('.vote-btn')) {
            const voteBtn = event.target.closest('.vote-btn');
            const voteUrl = voteBtn.getAttribute('href');
            
            // Only proceed if we have a URL and the user is logged in
            if (voteUrl && !voteUrl.includes('login')) {
                event.preventDefault();
                
                // Send the AJAX request
                fetch(voteUrl, {
                    method: 'POST',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                        'X-CSRFToken': getCookie('csrftoken')
                    }
                })
                .then(response => response.json())
                .then(data => {
                    // Find the container with the vote count
                    const voteContainer = voteBtn.closest('.d-flex').querySelector('.vote-count');
                    if (voteContainer) {
                        voteContainer.textContent = data.vote_count;
                    }
                    
                    // Toggle the voted class
                    const upvoteBtn = voteBtn.closest('.vote-column').querySelector('.upvote-btn');
                    const downvoteBtn = voteBtn.closest('.vote-column').querySelector('.downvote-btn');
                    
                    if (voteBtn.classList.contains('upvote-btn')) {
                        if (voteBtn.classList.contains('voted')) {
                            voteBtn.classList.remove('voted');
                        } else {
                            voteBtn.classList.add('voted');
                            if (downvoteBtn.classList.contains('voted')) {
                                downvoteBtn.classList.remove('voted');
                            }
                        }
                    } else if (voteBtn.classList.contains('downvote-btn')) {
                        if (voteBtn.classList.contains('voted')) {
                            voteBtn.classList.remove('voted');
                        } else {
                            voteBtn.classList.add('voted');
                            if (upvoteBtn.classList.contains('voted')) {
                                upvoteBtn.classList.remove('voted');
                            }
                        }
                    }
                })
                .catch(error => {
                    console.error('Error during vote:', error);
                });
            }
        }
    });
}

// Function to set active nav item based on current URL
function setActiveNavItem() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    
    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href === currentPath || 
            (href !== '/' && currentPath.startsWith(href))) {
            link.classList.add('active');
        }
    });
}

// Setup comment form AJAX submissions and reply functionality
function setupCommentForms() {
    const commentForms = document.querySelectorAll('form[action*="comment"]');
    
    commentForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            // For now, we'll use the standard form submission
            // In a future enhancement, this could be converted to AJAX
        });
    });
    
    // Setup reply toggle functionality
    const replyButtons = document.querySelectorAll('.reply-toggle');
    replyButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const commentId = this.getAttribute('data-comment-id');
            const replyForm = document.getElementById(`reply-form-${commentId}`);
            
            // Toggle visibility of the reply form
            if (replyForm.style.display === 'none') {
                // Hide any other open reply forms first
                document.querySelectorAll('.reply-form').forEach(form => {
                    form.style.display = 'none';
                });
                
                // Show this form
                replyForm.style.display = 'block';
                // Focus on the textarea
                const textarea = replyForm.querySelector('textarea');
                if (textarea) {
                    textarea.focus();
                }
            } else {
                replyForm.style.display = 'none';
            }
        });
    });
    
    // Setup cancel reply buttons
    const cancelButtons = document.querySelectorAll('.cancel-reply');
    cancelButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const commentId = this.getAttribute('data-comment-id');
            const replyForm = document.getElementById(`reply-form-${commentId}`);
            replyForm.style.display = 'none';
        });
    });
}

// Get CSRF token from cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Utility function to format numbers (e.g., for large vote counts)
function formatNumber(num) {
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'm';
    }
    if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'k';
    }
    return num;
}

// Function to create confirmation dialogs
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

// Function to handle responsive design adjustments
function handleResponsiveAdjustments() {
    const windowWidth = window.innerWidth;
    
    // Adjust voting buttons on small screens
    if (windowWidth < 576) {
        document.querySelectorAll('.vote-column').forEach(col => {
            col.classList.add('vote-column-sm');
        });
    } else {
        document.querySelectorAll('.vote-column').forEach(col => {
            col.classList.remove('vote-column-sm');
        });
    }
}

// Call responsive adjustments on load and resize
window.addEventListener('load', handleResponsiveAdjustments);
window.addEventListener('resize', handleResponsiveAdjustments);
