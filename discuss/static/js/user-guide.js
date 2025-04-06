/**
 * User Guide Functionality
 * Manages the interactive guide functionality
 */

class UserGuide {
    constructor() {
        this.isNewUser = document.body.classList.contains('new-user');
        this.currentPage = document.body.dataset.page || '';
        this.guideType = '';
        this.steps = [];
        this.currentStepIndex = 0;
        
        // Check if we should show a guide
        this.init();
    }
    
    init() {
        // Check if user is new and should see the new user guide
        if (this.isNewUser) {
            this.loadGuide('new_user');
        }
        
        // Check current page and load relevant guide
        switch (this.currentPage) {
            case 'community_form':
                this.loadGuide('community_creation');
                break;
            case 'post_form':
                this.loadGuide('post_creation');
                break;
            case 'post_detail':
                this.loadGuide('commenting');
                break;
        }
        
        // Add event listener for manual guide triggering
        document.querySelectorAll('[data-guide]').forEach(element => {
            element.addEventListener('click', (e) => {
                e.preventDefault();
                const guideType = element.dataset.guide;
                this.loadGuide(guideType);
            });
        });
    }
    
    loadGuide(guideType) {
        this.guideType = guideType;
        
        // Fetch guide data
        fetch(`/user-guide/api/${guideType}/`)
            .then(response => response.json())
            .then(data => {
                this.steps = data.steps;
                if (this.steps && this.steps.length > 0) {
                    this.startGuide();
                }
            })
            .catch(error => console.error('Error loading guide:', error));
    }
    
    startGuide() {
        this.currentStepIndex = 0;
        this.showStep();
    }
    
    showStep() {
        if (!this.steps || this.currentStepIndex >= this.steps.length) return;
        
        const step = this.steps[this.currentStepIndex];
        
        // Remove any existing tooltips/overlays
        this.clearGuideElements();
        
        // Create overlay
        const overlay = document.createElement('div');
        overlay.className = 'guide-overlay';
        overlay.style.position = 'fixed';
        overlay.style.top = '0';
        overlay.style.left = '0';
        overlay.style.width = '100%';
        overlay.style.height = '100%';
        overlay.style.backgroundColor = 'rgba(0, 0, 0, 0.5)';
        overlay.style.zIndex = '9998';
        document.body.appendChild(overlay);
        
        // Find target element
        const targetElement = document.querySelector(step.element_selector);
        
        if (targetElement) {
            // Make target visible through overlay
            const rect = targetElement.getBoundingClientRect();
            const highlight = document.createElement('div');
            highlight.className = 'guide-highlight';
            highlight.style.position = 'absolute';
            highlight.style.top = rect.top + 'px';
            highlight.style.left = rect.left + 'px';
            highlight.style.width = rect.width + 'px';
            highlight.style.height = rect.height + 'px';
            highlight.style.zIndex = '9999';
            highlight.style.boxShadow = '0 0 0 9999px rgba(0, 0, 0, 0.7)';
            highlight.style.borderRadius = '4px';
            document.body.appendChild(highlight);
            
            // Create tooltip
            const tooltip = document.createElement('div');
            tooltip.className = 'guide-tooltip';
            tooltip.style.position = 'absolute';
            tooltip.style.zIndex = '10000';
            tooltip.style.backgroundColor = '#ffffff';
            tooltip.style.padding = '15px';
            tooltip.style.borderRadius = '5px';
            tooltip.style.boxShadow = '0 0 10px rgba(0, 0, 0, 0.3)';
            tooltip.style.maxWidth = '300px';
            
            // Position tooltip
            let tooltipTop, tooltipLeft;
            
            switch(step.position) {
                case 'top':
                    tooltipTop = rect.top - 10;
                    tooltipLeft = rect.left + rect.width / 2;
                    break;
                case 'bottom':
                    tooltipTop = rect.bottom + 10;
                    tooltipLeft = rect.left + rect.width / 2;
                    break;
                case 'left':
                    tooltipTop = rect.top + rect.height / 2;
                    tooltipLeft = rect.left - 10;
                    break;
                case 'right':
                    tooltipTop = rect.top + rect.height / 2;
                    tooltipLeft = rect.right + 10;
                    break;
                default:
                    tooltipTop = rect.bottom + 10;
                    tooltipLeft = rect.left + rect.width / 2;
            }
            
            // Add tooltip content
            tooltip.innerHTML = `
                <h4>${step.title}</h4>
                <p>${step.content}</p>
                <div class="tooltip-buttons">
                    <button class="btn btn-sm btn-secondary guide-prev-btn" ${this.currentStepIndex === 0 ? 'disabled' : ''}>Previous</button>
                    <button class="btn btn-sm btn-primary guide-next-btn">
                        ${this.currentStepIndex === this.steps.length - 1 ? 'Finish' : 'Next'}
                    </button>
                    <button class="btn btn-sm btn-danger guide-close-btn">Skip Guide</button>
                </div>
            `;
            
            tooltip.style.top = tooltipTop + 'px';
            tooltip.style.left = tooltipLeft + 'px';
            tooltip.style.transform = 'translate(-50%, 0)';
            
            document.body.appendChild(tooltip);
            
            // Add event listeners
            const prevButton = tooltip.querySelector('.guide-prev-btn');
            const nextButton = tooltip.querySelector('.guide-next-btn');
            const closeButton = tooltip.querySelector('.guide-close-btn');
            
            prevButton.addEventListener('click', () => this.prevStep());
            nextButton.addEventListener('click', () => this.nextStep());
            closeButton.addEventListener('click', () => this.closeGuide());
        } else {
            console.warn(`Element with selector '${step.element_selector}' not found`);
            this.showErrorTooltip();
        }
    }
    
    showErrorTooltip() {
        const errorTooltip = document.createElement('div');
        errorTooltip.className = 'guide-tooltip';
        errorTooltip.style.position = 'fixed';
        errorTooltip.style.top = '50%';
        errorTooltip.style.left = '50%';
        errorTooltip.style.transform = 'translate(-50%, -50%)';
        errorTooltip.style.zIndex = '10000';
        errorTooltip.style.backgroundColor = '#ffffff';
        errorTooltip.style.padding = '15px';
        errorTooltip.style.borderRadius = '5px';
        errorTooltip.style.boxShadow = '0 0 10px rgba(0, 0, 0, 0.3)';
        errorTooltip.style.maxWidth = '300px';
        
        const step = this.steps[this.currentStepIndex];
        
        errorTooltip.innerHTML = `
            <h4>Element Not Found</h4>
            <p>The guided element "${step.element_selector}" could not be found on this page. You may need to navigate to the appropriate page first.</p>
            <div class="tooltip-buttons">
                <button class="btn btn-sm btn-secondary guide-prev-btn" ${this.currentStepIndex === 0 ? 'disabled' : ''}>Previous</button>
                <button class="btn btn-sm btn-primary guide-next-btn">
                    ${this.currentStepIndex === this.steps.length - 1 ? 'Finish' : 'Next'}
                </button>
                <button class="btn btn-sm btn-danger guide-close-btn">Close Guide</button>
            </div>
        `;
        
        document.body.appendChild(errorTooltip);
        
        // Add event listeners
        const prevButton = errorTooltip.querySelector('.guide-prev-btn');
        const nextButton = errorTooltip.querySelector('.guide-next-btn');
        const closeButton = errorTooltip.querySelector('.guide-close-btn');
        
        prevButton.addEventListener('click', () => this.prevStep());
        nextButton.addEventListener('click', () => this.nextStep());
        closeButton.addEventListener('click', () => this.closeGuide());
    }
    
    prevStep() {
        if (this.currentStepIndex > 0) {
            this.currentStepIndex--;
            this.showStep();
        }
    }
    
    nextStep() {
        if (this.currentStepIndex < this.steps.length - 1) {
            this.currentStepIndex++;
            this.showStep();
        } else {
            // This is the last step
            this.closeGuide();
        }
    }
    
    closeGuide() {
        this.clearGuideElements();
    }
    
    clearGuideElements() {
        document.querySelectorAll('.guide-overlay, .guide-tooltip, .guide-highlight').forEach(el => {
            el.remove();
        });
    }
}

// Initialize the user guide when the DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.userGuide = new UserGuide();
});