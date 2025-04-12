/**
 * Discuss User Guide
 * A simple step-by-step guide for new users to learn how to use the platform
 */

class DiscussUserGuide {
    constructor(options = {}) {
        this.options = {
            cookieName: 'discuss_user_guide_completed',
            cookieExpireDays: 365,
            steps: [],
            ...options
        };
        
        this.currentStep = 0;
        this.overlay = null;
        this.tooltip = null;
        this.initialized = false;
    }

    /**
     * Initialize the user guide
     */
    init() {
        if (this.initialized) return;
        
        // Create styles if not already added
        this.addStyles();
        
        // Create the overlay
        this.overlay = document.createElement('div');
        this.overlay.className = 'discuss-guide-overlay';
        document.body.appendChild(this.overlay);
        
        // Create the tooltip
        this.tooltip = document.createElement('div');
        this.tooltip.className = 'discuss-guide-tooltip';
        document.body.appendChild(this.tooltip);
        
        // Setup event listeners
        this.setupEventListeners();
        
        this.initialized = true;
    }

    /**
     * Add required styles to the document
     */
    addStyles() {
        if (document.getElementById('discuss-user-guide-styles')) return;
        
        const style = document.createElement('style');
        style.id = 'discuss-user-guide-styles';
        style.textContent = `
            .discuss-guide-overlay {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background-color: rgba(0, 0, 0, 0.5);
                z-index: 9998;
                display: none;
            }
            
            .discuss-guide-highlight {
                position: relative;
                z-index: 9999;
                box-shadow: 0 0 0 2000px rgba(0, 0, 0, 0.5);
                border-radius: 4px;
            }
            
            .discuss-guide-tooltip {
                position: absolute;
                background: #fff;
                max-width: 350px;
                border-radius: 5px;
                box-shadow: 0 0 15px rgba(0, 0, 0, 0.2);
                padding: 15px;
                z-index: 10000;
                display: none;
            }
            
            .discuss-guide-tooltip-title {
                font-size: 18px;
                font-weight: bold;
                margin-bottom: 10px;
                color: #333;
            }
            
            .discuss-guide-tooltip-content {
                margin-bottom: 15px;
                color: #555;
                line-height: 1.4;
            }
            
            .discuss-guide-tooltip-buttons {
                display: flex;
                justify-content: space-between;
            }
            
            .discuss-guide-btn {
                padding: 8px 15px;
                border-radius: 4px;
                border: none;
                cursor: pointer;
                font-weight: bold;
                transition: background-color 0.2s;
            }
            
            .discuss-guide-btn-primary {
                background-color: #007bff;
                color: white;
            }
            
            .discuss-guide-btn-primary:hover {
                background-color: #0069d9;
            }
            
            .discuss-guide-btn-secondary {
                background-color: #f0f0f0;
                color: #333;
            }
            
            .discuss-guide-btn-secondary:hover {
                background-color: #e0e0e0;
            }
            
            .discuss-guide-progress {
                height: 4px;
                background-color: #eee;
                margin-top: 10px;
                border-radius: 2px;
                overflow: hidden;
            }
            
            .discuss-guide-progress-bar {
                height: 100%;
                background-color: #007bff;
                width: 0%;
                transition: width 0.3s;
            }
            
            .discuss-guide-checkbox {
                margin-top: 10px;
                display: flex;
                align-items: center;
            }
            
            .discuss-guide-checkbox input {
                margin-right: 5px;
            }
        `;
        
        document.head.appendChild(style);
    }

    /**
     * Setup event listeners for guide navigation
     */
    setupEventListeners() {
        // Close on ESC key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.close();
            }
        });
        
        // Close on overlay click
        this.overlay.addEventListener('click', () => {
            this.close();
        });
    }

    /**
     * Start the user guide
     */
    start() {
        if (this.hasCompletedGuide()) return;
        
        this.init();
        this.currentStep = 0;
        
        if (this.options.steps.length > 0) {
            this.showStep(this.currentStep);
        }
    }

    /**
     * Show a specific step
     * @param {number} index - The step index to show
     */
    showStep(index) {
        if (index < 0 || index >= this.options.steps.length) {
            this.close();
            return;
        }
        
        const step = this.options.steps[index];
        
        // Find the target element
        const targetElement = document.querySelector(step.element);
        if (!targetElement) {
            console.error(`Element not found: ${step.element}`);
            this.nextStep();
            return;
        }
        
        // Highlight the element
        this.highlightElement(targetElement);
        
        // Position and show the tooltip
        this.positionTooltip(targetElement, step);
        
        // Update the tooltip content
        this.updateTooltipContent(step, index);
        
        // Show the overlay and tooltip
        this.overlay.style.display = 'block';
        this.tooltip.style.display = 'block';
    }

    /**
     * Highlight an element by adding the highlight class
     * @param {HTMLElement} element - The element to highlight
     */
    highlightElement(element) {
        // Remove previous highlights
        const previousHighlights = document.querySelectorAll('.discuss-guide-highlight');
        previousHighlights.forEach(el => el.classList.remove('discuss-guide-highlight'));
        
        // Add highlight to current element
        element.classList.add('discuss-guide-highlight');
        
        // Scroll element into view if needed
        element.scrollIntoView({
            behavior: 'smooth',
            block: 'center'
        });
    }

    /**
     * Position the tooltip relative to the target element
     * @param {HTMLElement} element - The target element
     * @param {Object} step - The step configuration
     */
    positionTooltip(element, step) {
        const elementRect = element.getBoundingClientRect();
        const tooltipRect = this.tooltip.getBoundingClientRect();
        
        // Default position is 'bottom'
        let position = step.position || 'bottom';
        
        // Calculate positions
        let left, top;
        
        switch (position) {
            case 'top':
                left = elementRect.left + (elementRect.width / 2) - (tooltipRect.width / 2);
                top = elementRect.top - tooltipRect.height - 10;
                break;
            case 'right':
                left = elementRect.right + 10;
                top = elementRect.top + (elementRect.height / 2) - (tooltipRect.height / 2);
                break;
            case 'left':
                left = elementRect.left - tooltipRect.width - 10;
                top = elementRect.top + (elementRect.height / 2) - (tooltipRect.height / 2);
                break;
            case 'bottom':
            default:
                left = elementRect.left + (elementRect.width / 2) - (tooltipRect.width / 2);
                top = elementRect.bottom + 10;
                break;
        }
        
        // Adjust position to ensure tooltip stays within viewport
        const viewportWidth = window.innerWidth;
        const viewportHeight = window.innerHeight;
        
        if (left < 10) left = 10;
        if (left + tooltipRect.width > viewportWidth - 10) {
            left = viewportWidth - tooltipRect.width - 10;
        }
        
        if (top < 10) top = 10;
        if (top + tooltipRect.height > viewportHeight - 10) {
            top = viewportHeight - tooltipRect.height - 10;
        }
        
        // Set position
        this.tooltip.style.left = `${left}px`;
        this.tooltip.style.top = `${top}px`;
    }

    /**
     * Update the tooltip content based on the current step
     * @param {Object} step - The step configuration
     * @param {number} index - The step index
     */
    updateTooltipContent(step, index) {
        const isFirstStep = index === 0;
        const isLastStep = index === this.options.steps.length - 1;
        
        // Create tooltip content
        this.tooltip.innerHTML = `
            <div class="discuss-guide-tooltip-title">${step.title || 'Guide'}</div>
            <div class="discuss-guide-tooltip-content">${step.content || ''}</div>
            <div class="discuss-guide-progress">
                <div class="discuss-guide-progress-bar" style="width: ${((index + 1) / this.options.steps.length) * 100}%"></div>
            </div>
            <div class="discuss-guide-tooltip-buttons">
                ${!isFirstStep ? '<button class="discuss-guide-btn discuss-guide-btn-secondary discuss-guide-prev">Previous</button>' : '<div></div>'}
                ${isLastStep 
                    ? '<button class="discuss-guide-btn discuss-guide-btn-primary discuss-guide-finish">Finish</button>'
                    : '<button class="discuss-guide-btn discuss-guide-btn-primary discuss-guide-next">Next</button>'
                }
            </div>
            ${isLastStep ? `
                <div class="discuss-guide-checkbox">
                    <input type="checkbox" id="discuss-guide-dont-show-again">
                    <label for="discuss-guide-dont-show-again">Don't show this guide again</label>
                </div>
            ` : ''}
        `;
        
        // Add event listeners to buttons
        const prevButton = this.tooltip.querySelector('.discuss-guide-prev');
        if (prevButton) {
            prevButton.addEventListener('click', () => this.prevStep());
        }
        
        const nextButton = this.tooltip.querySelector('.discuss-guide-next');
        if (nextButton) {
            nextButton.addEventListener('click', () => this.nextStep());
        }
        
        const finishButton = this.tooltip.querySelector('.discuss-guide-finish');
        if (finishButton) {
            finishButton.addEventListener('click', () => this.finish());
        }
    }

    /**
     * Go to the next step
     */
    nextStep() {
        this.currentStep++;
        this.showStep(this.currentStep);
    }

    /**
     * Go to the previous step
     */
    prevStep() {
        this.currentStep--;
        this.showStep(this.currentStep);
    }

    /**
     * Finish the guide
     */
    finish() {
        const dontShowAgain = document.getElementById('discuss-guide-dont-show-again');
        if (dontShowAgain && dontShowAgain.checked) {
            this.setCompletedGuide();
        }
        
        this.close();
        
        // Trigger onComplete callback if provided
        if (typeof this.options.onComplete === 'function') {
            this.options.onComplete();
        }
    }

    /**
     * Close the guide
     */
    close() {
        // Remove highlights
        const highlights = document.querySelectorAll('.discuss-guide-highlight');
        highlights.forEach(el => el.classList.remove('discuss-guide-highlight'));
        
        // Hide overlay and tooltip
        if (this.overlay) this.overlay.style.display = 'none';
        if (this.tooltip) this.tooltip.style.display = 'none';
    }

    /**
     * Set a cookie to mark the guide as completed
     */
    setCompletedGuide() {
        const date = new Date();
        date.setTime(date.getTime() + (this.options.cookieExpireDays * 24 * 60 * 60 * 1000));
        const expires = `expires=${date.toUTCString()}`;
        document.cookie = `${this.options.cookieName}=true;${expires};path=/`;
    }

    /**
     * Check if the user has already completed the guide
     * @returns {boolean} True if the guide has been completed
     */
    hasCompletedGuide() {
        const nameEQ = `${this.options.cookieName}=`;
        const ca = document.cookie.split(';');
        for (let i = 0; i < ca.length; i++) {
            let c = ca[i];
            while (c.charAt(0) === ' ') c = c.substring(1, c.length);
            if (c.indexOf(nameEQ) === 0) return c.substring(nameEQ.length, c.length) === 'true';
        }
        return false;
    }

    /**
     * Reset the guide (clear the completed status)
     */
    reset() {
        document.cookie = `${this.options.cookieName}=false;max-age=0;path=/`;
    }
}

// Make available globally
window.DiscussUserGuide = DiscussUserGuide;
