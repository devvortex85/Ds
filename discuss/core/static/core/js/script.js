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
