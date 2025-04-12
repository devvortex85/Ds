document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM loaded - initializing Discuss app features");
    
    // Set up comment replies
    setupCommentReplies();
    
    // Set up AJAX voting - load votes from localStorage first, then apply AJAX handlers
    loadVotesFromLocalStorage();
    setupAjaxVoting();
    
    // Initialize any tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });
    
    // Add responsive layout adjustments
    applyResponsiveLayout();
    
    // Add keyboard navigation support
    setupKeyboardNavigation();
    
    // Handle window resize events for responsive adjustments
    window.addEventListener('resize', debounce(applyResponsiveLayout, 250));
});

/**
 * Applies specific layout adjustments based on screen size
 */
function applyResponsiveLayout() {
    const isMobile = window.innerWidth < 768;
    const isTablet = window.innerWidth >= 768 && window.innerWidth <= 1024;
    
    console.log(`Applying responsive layout: Mobile: ${isMobile}, Tablet: ${isTablet}`);
    
    // Apply mobile-specific layouts
    if (isMobile) {
        // Convert vote controls to horizontal on mobile
        document.querySelectorAll('.vote-controls').forEach(control => {
            control.classList.add('d-flex');
            control.classList.add('flex-row');
            control.classList.add('align-items-center');
            control.classList.remove('flex-column');
        });
        
        // Make sure tap targets are large enough (44px minimum)
        document.querySelectorAll('.btn, .nav-link, .vote-btn').forEach(elem => {
            elem.classList.add('mobile-friendly-tap');
        });
        
        // Stack flexbox elements that should be vertical on mobile
        document.querySelectorAll('.d-flex:not(.flex-column)').forEach(flex => {
            if (!flex.classList.contains('no-mobile-stack') && 
                !flex.classList.contains('navbar-nav') && 
                !flex.classList.contains('pagination')) {
                flex.classList.add('mobile-stack');
            }
        });
    } else {
        // Revert mobile changes for larger screens
        document.querySelectorAll('.vote-controls').forEach(control => {
            control.classList.remove('d-flex');
            control.classList.remove('flex-row');
            control.classList.remove('align-items-center');
            control.classList.add('flex-column');
        });
        
        document.querySelectorAll('.mobile-stack').forEach(elem => {
            elem.classList.remove('mobile-stack');
        });
    }
    
    // Apply tablet-specific layouts
    if (isTablet) {
        document.querySelectorAll('.sidebar').forEach(sidebar => {
            sidebar.classList.add('tablet-sidebar');
        });
    } else {
        document.querySelectorAll('.tablet-sidebar').forEach(sidebar => {
            sidebar.classList.remove('tablet-sidebar');
        });
    }
}

/**
 * Debounce function to limit how often a function is called
 */
function debounce(func, wait) {
    let timeout;
    return function() {
        const context = this;
        const args = arguments;
        clearTimeout(timeout);
        timeout = setTimeout(() => {
            func.apply(context, args);
        }, wait);
    };
}

/**
 * Sets up keyboard navigation for interactive elements
 */
function setupKeyboardNavigation() {
    // Add keyboard support for vote buttons
    document.querySelectorAll('.vote-btn').forEach(btn => {
        btn.addEventListener('keydown', function(e) {
            if (e.key === ' ' || e.key === 'Enter') {
                e.preventDefault();
                this.click();
            }
        });
    });
    
    // Add keyboard support for any custom dropdown toggles
    document.querySelectorAll('[data-toggle]').forEach(toggle => {
        toggle.addEventListener('keydown', function(e) {
            if (e.key === ' ' || e.key === 'Enter') {
                e.preventDefault();
                this.click();
            }
        });
    });
}

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
                    const toggleButton = document.querySelector(`.reply-toggle[data-comment-id="${form.id.replace('reply-form-', '')}"]`);
                    if (toggleButton) {
                        toggleButton.setAttribute('aria-expanded', 'false');
                    }
                    form.setAttribute('aria-hidden', 'true');
                }
            });
            
            // Toggle this reply form
            if (replyForm) {
                // Toggle visibility
                const isCurrentlyHidden = replyForm.style.display === 'none' || replyForm.style.display === '';
                replyForm.style.display = isCurrentlyHidden ? 'block' : 'none';
                
                // Update ARIA attributes
                this.setAttribute('aria-expanded', isCurrentlyHidden ? 'true' : 'false');
                replyForm.setAttribute('aria-hidden', isCurrentlyHidden ? 'false' : 'true');
                
                // Announce to screen readers
                if (window.announceToScreenReader) {
                    window.announceToScreenReader(isCurrentlyHidden ? 'Reply form opened' : 'Reply form closed');
                }
                
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
            const replyToggle = document.querySelector(`.reply-toggle[data-comment-id="${commentId}"]`);
            
            if (replyForm) {
                replyForm.style.display = 'none';
                replyForm.setAttribute('aria-hidden', 'true');
                
                if (replyToggle) {
                    replyToggle.setAttribute('aria-expanded', 'false');
                    // Focus back to reply toggle when canceling
                    replyToggle.focus();
                }
                
                // Announce to screen readers
                if (window.announceToScreenReader) {
                    window.announceToScreenReader('Reply canceled');
                }
            }
        });
    });
}

function setupAjaxVoting() {
    console.log("Setting up AJAX voting");
    
    // Load existing votes from localStorage first
    loadVotesFromLocalStorage();
    
    // For post votes
    const postVoteButtons = document.querySelectorAll('.post-vote-btn');
    console.log("Found post vote buttons:", postVoteButtons.length);
    
    postVoteButtons.forEach(button => {
        // Make sure buttons are focusable and handle keyboard events
        button.setAttribute('role', 'button');
        button.setAttribute('tabindex', '0');
        
        // Add keyboard event listeners
        button.addEventListener('keydown', function(e) {
            if (e.key === ' ' || e.key === 'Enter') {
                e.preventDefault();
                this.click();
            }
        });
        
        button.addEventListener('click', function(e) {
            e.preventDefault();
            console.log("Post vote button clicked:", this.href);
            
            // Only process authenticated user clicks
            if (this.href.includes('login')) {
                window.location.href = this.href;
                return;
            }
            
            // Show loading state
            this.setAttribute('aria-busy', 'true');
            
            const voteUrl = this.href;
            const isUpvote = voteUrl.includes('upvote');
            const voteType = isUpvote ? 'upvote' : 'downvote';
            
            fetch(voteUrl, {
                method: 'GET',  // Django view is only set up for GET requests currently
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': getCsrfToken()
                }
            })
            .then(response => response.json())
            .then(data => {
                console.log("Vote response data:", data);
                
                // Update the vote count display
                const postId = data.post_id;
                const voteCountElement = document.getElementById(`post-${postId}-votes`);
                if (voteCountElement) {
                    voteCountElement.textContent = data.vote_count;
                    console.log(`Updated vote count to ${data.vote_count}`);
                    
                    // Update ARIA attributes for screen readers
                    voteCountElement.setAttribute('aria-label', `Post score: ${data.vote_count}`);
                    
                    // Announce the vote to screen readers
                    if (window.announceToScreenReader) {
                        window.announceToScreenReader(`Post ${voteType}d. Score is now ${data.vote_count}`);
                    }
                } else {
                    console.error(`Vote count element not found for post-${postId}-votes`);
                }
                
                // Update active state of vote buttons for this post
                const upvoteBtn = document.querySelector(`.post-vote-btn[href*="/posts/${postId}/vote/upvote"]`);
                const downvoteBtn = document.querySelector(`.post-vote-btn[href*="/posts/${postId}/vote/downvote"]`);
                
                console.log("Found upvote button:", upvoteBtn ? "yes" : "no");
                console.log("Found downvote button:", downvoteBtn ? "yes" : "no");
                console.log("Current user vote value:", data.user_vote);
                
                if (upvoteBtn) {
                    if (data.user_vote === 1) {
                        upvoteBtn.classList.add('voted');
                        upvoteBtn.classList.add('active');
                        upvoteBtn.setAttribute('aria-pressed', 'true');
                        console.log("Added 'voted' and 'active' classes to upvote button");
                    } else {
                        upvoteBtn.classList.remove('voted');
                        upvoteBtn.classList.remove('active');
                        upvoteBtn.setAttribute('aria-pressed', 'false');
                        console.log("Removed 'voted' and 'active' classes from upvote button");
                    }
                }
                
                if (downvoteBtn) {
                    if (data.user_vote === -1) {
                        downvoteBtn.classList.add('voted');
                        downvoteBtn.classList.add('active');
                        downvoteBtn.setAttribute('aria-pressed', 'true');
                        console.log("Added 'voted' and 'active' classes to downvote button");
                    } else {
                        downvoteBtn.classList.remove('voted');
                        downvoteBtn.classList.remove('active');
                        downvoteBtn.setAttribute('aria-pressed', 'false');
                        console.log("Removed 'voted' and 'active' classes from downvote button");
                    }
                }
                
                // Save the vote state to localStorage
                saveVoteToLocalStorage('post', postId, data.user_vote);
            })
            .catch(error => {
                console.error('Error:', error);
                if (window.announceToScreenReader) {
                    window.announceToScreenReader('Error processing vote');
                }
            })
            .finally(() => {
                // Remove loading state
                this.setAttribute('aria-busy', 'false');
            });
        });
    });
    
    // For comment votes
    const commentVoteButtons = document.querySelectorAll('.comment-vote-btn');
    console.log("Found comment vote buttons:", commentVoteButtons.length);
    
    commentVoteButtons.forEach(button => {
        // Make sure buttons are focusable and handle keyboard events
        button.setAttribute('role', 'button');
        button.setAttribute('tabindex', '0');
        
        // Add keyboard event listeners
        button.addEventListener('keydown', function(e) {
            if (e.key === ' ' || e.key === 'Enter') {
                e.preventDefault();
                this.click();
            }
        });
        
        button.addEventListener('click', function(e) {
            e.preventDefault();
            console.log("Comment vote button clicked:", this.href);
            
            // Only process authenticated user clicks
            if (this.href.includes('login')) {
                window.location.href = this.href;
                return;
            }
            
            // Show loading state
            this.setAttribute('aria-busy', 'true');
            
            const voteUrl = this.href;
            const isUpvote = voteUrl.includes('upvote');
            const voteType = isUpvote ? 'upvote' : 'downvote';
            
            fetch(voteUrl, {
                method: 'GET',  // Django view is only set up for GET requests currently
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': getCsrfToken()
                }
            })
            .then(response => response.json())
            .then(data => {
                console.log("Comment vote response data:", data);
                
                // Update the vote count display
                const commentId = data.comment_id;
                const commentElement = document.getElementById(`comment-${commentId}`);
                if (commentElement) {
                    const voteCountElement = commentElement.querySelector('.vote-count');
                    if (voteCountElement) {
                        voteCountElement.textContent = data.vote_count;
                        console.log(`Updated comment vote count to ${data.vote_count}`);
                        
                        // Update ARIA attributes for screen readers
                        voteCountElement.setAttribute('aria-label', `Comment score: ${data.vote_count}`);
                        
                        // Announce the vote to screen readers
                        if (window.announceToScreenReader) {
                            window.announceToScreenReader(`Comment ${voteType}d. Score is now ${data.vote_count}`);
                        }
                    } else {
                        console.error(`Vote count element not found for comment ${commentId}`);
                    }
                    
                    // Update vote button styles
                    const upvoteBtn = commentElement.querySelector('a[href*="upvote"]');
                    const downvoteBtn = commentElement.querySelector('a[href*="downvote"]');
                    
                    console.log("Found comment upvote button:", upvoteBtn ? "yes" : "no");
                    console.log("Found comment downvote button:", downvoteBtn ? "yes" : "no");
                    console.log("Current user comment vote value:", data.user_vote);
                    
                    if (upvoteBtn) {
                        if (data.user_vote === 1) {
                            upvoteBtn.classList.add('voted');
                            upvoteBtn.classList.add('active');
                            upvoteBtn.setAttribute('aria-pressed', 'true');
                            console.log("Added 'voted' and 'active' classes to comment upvote button");
                        } else {
                            upvoteBtn.classList.remove('voted');
                            upvoteBtn.classList.remove('active');
                            upvoteBtn.setAttribute('aria-pressed', 'false');
                            console.log("Removed 'voted' and 'active' classes from comment upvote button");
                        }
                    }
                    
                    if (downvoteBtn) {
                        if (data.user_vote === -1) {
                            downvoteBtn.classList.add('voted');
                            downvoteBtn.classList.add('active');
                            downvoteBtn.setAttribute('aria-pressed', 'true');
                            console.log("Added 'voted' and 'active' classes to comment downvote button");
                        } else {
                            downvoteBtn.classList.remove('voted');
                            downvoteBtn.classList.remove('active');
                            downvoteBtn.setAttribute('aria-pressed', 'false');
                            console.log("Removed 'voted' and 'active' classes from comment downvote button");
                        }
                    }
                    
                    // Save the vote state to localStorage
                    saveVoteToLocalStorage('comment', commentId, data.user_vote);
                } else {
                    console.error(`Comment element not found for comment-${commentId}`);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                if (window.announceToScreenReader) {
                    window.announceToScreenReader('Error processing vote');
                }
            })
            .finally(() => {
                // Remove loading state
                this.setAttribute('aria-busy', 'false');
            });
        });
    });
}

// Function to get CSRF token
function getCsrfToken() {
    return document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || 
           document.cookie.match(/csrftoken=([^;]+)/)?.[1] || '';
}

// Save vote to localStorage - this is similar to how Reddit persists vote state
function saveVoteToLocalStorage(type, id, value) {
    try {
        if (type && id) {
            const key = `discuss_${type}_vote_${id}`;
            console.log(`Saving vote to localStorage: ${key} = ${value}`);
            localStorage.setItem(key, value);
        }
    } catch (e) {
        console.error('Error saving vote to localStorage:', e);
    }
}

// Load votes from localStorage and apply them
function loadVotesFromLocalStorage() {
    try {
        console.log("Loading votes from localStorage");
        
        // For posts
        document.querySelectorAll('.post-vote-btn').forEach(btn => {
            const href = btn.getAttribute('href');
            if (!href) return;
            
            const postIdMatch = href.match(/posts\/(\d+)\/vote\/(up|down)vote/);
            
            if (postIdMatch && postIdMatch[1]) {
                const postId = postIdMatch[1];
                const voteType = postIdMatch[2]; // 'up' or 'down'
                const key = `discuss_post_vote_${postId}`;
                const savedVote = localStorage.getItem(key);
                
                console.log(`Checking saved vote for post ${postId}: ${savedVote}`);
                
                if (savedVote === '1' && voteType === 'up') {
                    btn.classList.add('voted');
                    btn.classList.add('active');
                    console.log(`Applied saved upvote for post ${postId}`);
                } else if (savedVote === '-1' && voteType === 'down') {
                    btn.classList.add('voted');
                    btn.classList.add('active');
                    console.log(`Applied saved downvote for post ${postId}`);
                }
            }
        });
        
        // For comments
        document.querySelectorAll('.comment-vote-btn').forEach(btn => {
            const href = btn.getAttribute('href');
            if (!href) return;
            
            const commentIdMatch = href.match(/comments\/(\d+)\/vote\/(up|down)vote/);
            
            if (commentIdMatch && commentIdMatch[1]) {
                const commentId = commentIdMatch[1];
                const voteType = commentIdMatch[2]; // 'up' or 'down'
                const key = `discuss_comment_vote_${commentId}`;
                const savedVote = localStorage.getItem(key);
                
                console.log(`Checking saved vote for comment ${commentId}: ${savedVote}`);
                
                if (savedVote === '1' && voteType === 'up') {
                    btn.classList.add('voted');
                    btn.classList.add('active');
                    console.log(`Applied saved upvote for comment ${commentId}`);
                } else if (savedVote === '-1' && voteType === 'down') {
                    btn.classList.add('voted');
                    btn.classList.add('active');
                    console.log(`Applied saved downvote for comment ${commentId}`);
                }
            }
        });
    } catch (e) {
        console.error('Error loading votes from localStorage:', e);
    }
}
