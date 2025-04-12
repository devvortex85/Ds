/**
 * Reddit-style Comment System
 * Implements collapsible comment threads and other interactive features
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize comment system
    initRedditComments();
});

/**
 * Initialize the Reddit-style comment system
 */
function initRedditComments() {
    console.log("Initializing Reddit-style comments");
    
    // Set up collapsible threads
    setupThreadCollapsing();
    
    // Set up reply functionality 
    setupCommentReplies();
    
    // Set up comment voting
    setupCommentVoting();
    
    // Initialize any collapsed threads from localStorage
    loadCollapsedThreads();
}

/**
 * Set up the collapsible thread functionality
 */
function setupThreadCollapsing() {
    // Get all thread collapse lines
    const collapseLines = document.querySelectorAll('.thread-collapse-line');
    const rootComments = document.querySelectorAll('.comment-thread > .comment-item .collapse-indicator');
    
    // Add event listeners to thread collapse lines
    collapseLines.forEach(line => {
        line.addEventListener('click', toggleThreadCollapse);
        line.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                toggleThreadCollapse.call(this, e);
            }
        });
    });
    
    // Add event listeners to root comment collapse indicators
    rootComments.forEach(indicator => {
        indicator.parentElement.addEventListener('click', function(e) {
            // Only collapse if clicking on the meta area with the username/etc
            if (e.target.closest('.comment-body') || e.target.closest('.comment-actions') || e.target.closest('.reply-form')) {
                return;
            }
            
            // Get the thread-id from the parent comment-thread
            const threadItem = this.closest('.comment-thread');
            if (threadItem) {
                const threadId = threadItem.dataset.commentId;
                toggleThreadCollapseById(threadId);
            }
        });
    });
}

/**
 * Toggle thread collapse/expand
 */
function toggleThreadCollapse(e) {
    e.preventDefault();
    const threadId = this.dataset.threadId;
    toggleThreadCollapseById(threadId);
}

/**
 * Toggle thread collapse/expand by comment ID
 */
function toggleThreadCollapseById(threadId) {
    const thread = document.getElementById(`thread-${threadId}`);
    
    if (!thread) return;
    
    const isCollapsed = thread.classList.contains('collapsed');
    const nestedComments = thread.querySelector('.nested-comments');
    
    if (isCollapsed) {
        // Expand the thread
        thread.classList.remove('collapsed');
        if (nestedComments) {
            nestedComments.classList.add('animate-in');
            nestedComments.classList.remove('animate-out');
        }
        // Remove from localStorage
        removeCollapsedThread(threadId);
    } else {
        // Collapse the thread
        thread.classList.add('collapsed');
        if (nestedComments) {
            nestedComments.classList.remove('animate-in');
            nestedComments.classList.add('animate-out');
        }
        // Save to localStorage
        saveCollapsedThread(threadId);
    }
}

/**
 * Save collapsed thread state to localStorage
 */
function saveCollapsedThread(threadId) {
    // Get current collapsed threads
    let collapsedThreads = JSON.parse(localStorage.getItem('collapsedThreads') || '[]');
    
    // Add this thread if not already included
    if (!collapsedThreads.includes(threadId)) {
        collapsedThreads.push(threadId);
        localStorage.setItem('collapsedThreads', JSON.stringify(collapsedThreads));
    }
}

/**
 * Remove thread from collapsed state in localStorage
 */
function removeCollapsedThread(threadId) {
    // Get current collapsed threads
    let collapsedThreads = JSON.parse(localStorage.getItem('collapsedThreads') || '[]');
    
    // Remove this thread if included
    const index = collapsedThreads.indexOf(threadId);
    if (index !== -1) {
        collapsedThreads.splice(index, 1);
        localStorage.setItem('collapsedThreads', JSON.stringify(collapsedThreads));
    }
}

/**
 * Load collapsed threads from localStorage
 */
function loadCollapsedThreads() {
    // Get collapsed threads from localStorage
    const collapsedThreads = JSON.parse(localStorage.getItem('collapsedThreads') || '[]');
    
    // Collapse each thread
    collapsedThreads.forEach(threadId => {
        const thread = document.getElementById(`thread-${threadId}`);
        if (thread) {
            thread.classList.add('collapsed');
        }
    });
}

/**
 * Set up comment reply functionality
 */
function setupCommentReplies() {
    // Get all reply toggle buttons
    const replyToggles = document.querySelectorAll('.reply-toggle');
    console.log("Found reply toggles:", replyToggles.length);
    
    // Get all cancel buttons
    const cancelButtons = document.querySelectorAll('.cancel-reply');
    console.log("Found cancel buttons:", cancelButtons.length);
    
    // Add click event listener to each reply toggle
    replyToggles.forEach(toggle => {
        toggle.addEventListener('click', function(e) {
            e.preventDefault();
            
            const commentId = this.dataset.commentId;
            const replyForm = document.getElementById(`reply-form-${commentId}`);
            const commentItem = this.closest('.comment-item');
            
            // Hide all other reply forms and reset all comment items
            document.querySelectorAll('.reply-form').forEach(form => {
                if (form.id !== `reply-form-${commentId}`) {
                    form.style.display = 'none';
                }
            });
            
            document.querySelectorAll('.comment-item').forEach(item => {
                if (item !== commentItem) {
                    item.classList.remove('replying-to');
                }
            });
            
            // Toggle this reply form
            if (replyForm) {
                const isVisible = replyForm.style.display === 'block';
                
                replyForm.style.display = isVisible ? 'none' : 'block';
                this.setAttribute('aria-expanded', isVisible ? 'false' : 'true');
                replyForm.setAttribute('aria-hidden', isVisible ? 'true' : 'false');
                
                // Add 'replying-to' class to the comment
                if (!isVisible) {
                    commentItem.classList.add('replying-to');
                    // Focus the textarea
                    const textarea = replyForm.querySelector('textarea');
                    if (textarea) textarea.focus();
                } else {
                    commentItem.classList.remove('replying-to');
                }
            }
        });
    });
    
    // Add click event listener to cancel buttons
    cancelButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const commentId = this.dataset.commentId;
            const replyForm = document.getElementById(`reply-form-${commentId}`);
            const commentItem = this.closest('.comment-item');
            
            if (replyForm) {
                replyForm.style.display = 'none';
                replyForm.setAttribute('aria-hidden', 'true');
                
                // Find and update the toggle button
                const toggleButton = document.querySelector(`.reply-toggle[data-comment-id="${commentId}"]`);
                if (toggleButton) {
                    toggleButton.setAttribute('aria-expanded', 'false');
                }
                
                // Remove 'replying-to' class
                if (commentItem) {
                    commentItem.classList.remove('replying-to');
                }
            }
        });
    });
}

/**
 * Set up comment voting with AJAX
 */
function setupCommentVoting() {
    // Check if AJAX voting is already set up (typically in script.js)
    if (typeof setupAjaxVoting === 'function') {
        // The main script already handles voting
        console.log("Using global AJAX voting setup");
        return;
    }
    
    // If not, implement our own voting system
    console.log("Setting up comment AJAX voting");
    
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    
    // Get all vote buttons
    const voteButtons = document.querySelectorAll('.comment-vote-btn');
    
    // Add click event listener to each vote button
    voteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            // If user is not authenticated, redirect to login
            if (!this.classList.contains('comment-vote-btn')) {
                window.location.href = this.href;
                return;
            }
            
            const commentId = this.dataset.commentId;
            const voteType = this.dataset.voteType;
            const isActive = this.classList.contains('active');
            
            // Determine the action (add vote, change vote, or remove vote)
            let action;
            if (isActive) {
                action = 'remove'; // Remove the current vote
            } else {
                action = voteType; // Add or change vote
            }
            
            // Update UI immediately for better UX
            const voteCountElement = document.getElementById(`comment-${commentId}-votes`);
            const currentCount = parseInt(voteCountElement.textContent);
            let newCount = currentCount;
            
            // Calculation logic for UI update
            if (isActive) {
                // Removing vote
                newCount = voteType === 'upvote' ? currentCount - 1 : currentCount + 1;
                this.classList.remove('active', 'voted');
            } else {
                // Adding/changing vote
                const oppositeButton = document.querySelector(
                    voteType === 'upvote' 
                    ? `.downvote-btn[data-comment-id="${commentId}"]`
                    : `.upvote-btn[data-comment-id="${commentId}"]`
                );
                
                if (oppositeButton && oppositeButton.classList.contains('active')) {
                    // Changing vote (e.g., from downvote to upvote)
                    oppositeButton.classList.remove('active', 'voted');
                    newCount = voteType === 'upvote' ? currentCount + 2 : currentCount - 2;
                } else {
                    // Just adding a new vote
                    newCount = voteType === 'upvote' ? currentCount + 1 : currentCount - 1;
                }
                
                this.classList.add('active', 'voted');
            }
            
            // Update the vote count
            voteCountElement.textContent = newCount;
            
            // Send AJAX request to server
            fetch(`/vote/comment/${commentId}/${action}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                credentials: 'same-origin'
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                // Update the vote count with the server's response
                voteCountElement.textContent = data.new_count;
                
                // Save vote in localStorage for persistence
                saveVote('comment', commentId, data.vote_value);
            })
            .catch(error => {
                console.error('Error:', error);
                // Revert UI changes on error
                voteCountElement.textContent = currentCount;
                if (isActive) {
                    this.classList.add('active', 'voted');
                } else {
                    this.classList.remove('active', 'voted');
                }
            });
        });
    });
}

/**
 * Save vote in localStorage
 */
function saveVote(type, id, value) {
    const storageKey = `${type}_votes`;
    let votes = JSON.parse(localStorage.getItem(storageKey) || '{}');
    
    if (value === 0) {
        // Remove vote
        delete votes[id];
    } else {
        // Save vote
        votes[id] = value;
    }
    
    localStorage.setItem(storageKey, JSON.stringify(votes));
}