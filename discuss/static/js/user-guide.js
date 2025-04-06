/**
 * User Guide JavaScript
 * Provides interactive guide functionality for the Discuss platform
 */
document.addEventListener('DOMContentLoaded', function() {
    // Guide state
    let currentGuideType = null;
    let currentStepIndex = 0;
    let guideSteps = [];
    
    // Initialize the user guide if we have the proper URL parameter
    const urlParams = new URLSearchParams(window.location.search);
    const startGuide = urlParams.get('start_guide');
    
    if (startGuide) {
        initGuide(startGuide);
    }
    
    // Guide initialization function
    function initGuide(guideType) {
        fetch(`/user-guide/steps/${guideType}/`)
            .then(response => response.json())
            .then(data => {
                if (data.steps && data.steps.length > 0) {
                    guideSteps = data.steps;
                    currentGuideType = guideType;
                    currentStepIndex = 0;
                    showGuideStep(currentStepIndex);
                    
                    // Create overlay
                    const overlay = document.createElement('div');
                    overlay.className = 'guide-overlay';
                    document.body.appendChild(overlay);
                }
            })
            .catch(error => {
                console.error('Error loading guide steps:', error);
            });
    }
    
    // Show a specific guide step
    function showGuideStep(index) {
        if (!guideSteps || index >= guideSteps.length) {
            endGuide();
            return;
        }
        
        const step = guideSteps[index];
        
        // Find target element
        const targetElement = document.querySelector(step.element_selector);
        if (!targetElement) {
            // If element not found, skip to next step
            currentStepIndex++;
            showGuideStep(currentStepIndex);
            return;
        }
        
        // Highlight the target element
        targetElement.classList.add('guide-highlighted');
        
        // Create tooltip
        const tooltip = document.createElement('div');
        tooltip.className = 'guide-tooltip';
        tooltip.innerHTML = `
            <div class="guide-tooltip-title">${step.title}</div>
            <div class="guide-tooltip-content">${step.content}</div>
            <div class="guide-tooltip-actions">
                <button class="btn-skip">Skip Guide</button>
                <button class="btn-next">${index < guideSteps.length - 1 ? 'Next' : 'Finish'}</button>
            </div>
        `;
        
        // Position tooltip
        positionTooltip(tooltip, targetElement, step.position);
        
        // Add tooltip to body
        document.body.appendChild(tooltip);
        
        // Add event listeners to buttons
        tooltip.querySelector('.btn-skip').addEventListener('click', endGuide);
        tooltip.querySelector('.btn-next').addEventListener('click', function() {
            nextStep();
        });
        
        // Show tooltip with animation
        setTimeout(() => {
            tooltip.classList.add('show');
        }, 50);
    }
    
    // Position the tooltip relative to the target element
    function positionTooltip(tooltip, target, position) {
        const targetRect = target.getBoundingClientRect();
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        const scrollLeft = window.pageXOffset || document.documentElement.scrollLeft;
        
        // Calculate position
        let top, left;
        const arrowSize = 10;
        
        switch (position) {
            case 'top':
                top = targetRect.top + scrollTop - tooltip.offsetHeight - arrowSize;
                left = targetRect.left + scrollLeft + (targetRect.width / 2) - (tooltip.offsetWidth / 2);
                break;
            case 'bottom':
                top = targetRect.bottom + scrollTop + arrowSize;
                left = targetRect.left + scrollLeft + (targetRect.width / 2) - (tooltip.offsetWidth / 2);
                break;
            case 'left':
                top = targetRect.top + scrollTop + (targetRect.height / 2) - (tooltip.offsetHeight / 2);
                left = targetRect.left + scrollLeft - tooltip.offsetWidth - arrowSize;
                break;
            case 'right':
                top = targetRect.top + scrollTop + (targetRect.height / 2) - (tooltip.offsetHeight / 2);
                left = targetRect.right + scrollLeft + arrowSize;
                break;
            default:
                // Default to bottom
                top = targetRect.bottom + scrollTop + arrowSize;
                left = targetRect.left + scrollLeft + (targetRect.width / 2) - (tooltip.offsetWidth / 2);
        }
        
        // Apply position
        tooltip.style.top = `${top}px`;
        tooltip.style.left = `${left}px`;
        
        // Add arrow
        const arrow = document.createElement('div');
        arrow.className = 'guide-tooltip-arrow';
        
        // Position arrow based on tooltip position
        switch (position) {
            case 'top':
                arrow.style.bottom = '-5px';
                arrow.style.left = '50%';
                arrow.style.marginLeft = '-5px';
                break;
            case 'bottom':
                arrow.style.top = '-5px';
                arrow.style.left = '50%';
                arrow.style.marginLeft = '-5px';
                break;
            case 'left':
                arrow.style.right = '-5px';
                arrow.style.top = '50%';
                arrow.style.marginTop = '-5px';
                break;
            case 'right':
                arrow.style.left = '-5px';
                arrow.style.top = '50%';
                arrow.style.marginTop = '-5px';
                break;
        }
        
        tooltip.appendChild(arrow);
    }
    
    // Move to the next step
    function nextStep() {
        // Remove existing tooltip and highlighting
        cleanupCurrentStep();
        
        // Increment step counter
        currentStepIndex++;
        
        // Show next step or end guide
        if (currentStepIndex < guideSteps.length) {
            showGuideStep(currentStepIndex);
        } else {
            endGuide();
        }
    }
    
    // End the guide
    function endGuide() {
        cleanupCurrentStep();
        
        // Remove overlay
        const overlay = document.querySelector('.guide-overlay');
        if (overlay) {
            overlay.remove();
        }
        
        // Reset guide state
        currentGuideType = null;
        currentStepIndex = 0;
        guideSteps = [];
        
        // Remove guide parameter from URL
        const url = new URL(window.location);
        url.searchParams.delete('start_guide');
        window.history.replaceState({}, '', url);
    }
    
    // Clean up the current step
    function cleanupCurrentStep() {
        // Remove existing tooltip
        const existingTooltip = document.querySelector('.guide-tooltip');
        if (existingTooltip) {
            existingTooltip.remove();
        }
        
        // Remove highlighting from all elements
        document.querySelectorAll('.guide-highlighted').forEach(el => {
            el.classList.remove('guide-highlighted');
        });
    }
    
    // Expose guide initialization to global scope
    window.startUserGuide = initGuide;
});
