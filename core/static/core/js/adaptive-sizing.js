/**
 * Enhanced Adaptive Sizing System
 * A comprehensive solution for UI adaptability across all devices
 * Provides dynamic sizing for typography, spacing, layout and components
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize the adaptive system
    initAdaptiveSystem();
    
    // Apply initial sizing
    applyAdaptiveSizing();
    
    // Listen for window resize events with debounce for performance
    let resizeTimer;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(function() {
            applyAdaptiveSizing();
        }, 100); // 100ms debounce
    });
    
    // Listen for orientation changes on mobile
    window.addEventListener('orientationchange', function() {
        applyAdaptiveSizing();
    });
    
    /**
     * Initialize adaptive system
     * Sets up global variables and constants
     */
    function initAdaptiveSystem() {
        // Add our custom CSS variables for unified adaptive sizing
        const style = document.createElement('style');
        style.innerHTML = `
            :root {
                --adaptive-scale: 1;
                --mobile-scale: 0.85;
                --tablet-scale: 0.92;
                --desktop-scale: 1;
                --large-desktop-scale: 1.1;
                
                /* Spacing variables */
                --base-spacing: calc(0.5rem * var(--adaptive-scale));
                --spacing-xs: calc(0.25rem * var(--adaptive-scale));
                --spacing-sm: calc(0.5rem * var(--adaptive-scale));
                --spacing-md: calc(1rem * var(--adaptive-scale));
                --spacing-lg: calc(1.5rem * var(--adaptive-scale));
                --spacing-xl: calc(2rem * var(--adaptive-scale));
                
                /* Typography variables */
                --font-size-xs: calc(0.7rem * var(--adaptive-scale));
                --font-size-sm: calc(0.85rem * var(--adaptive-scale));
                --font-size-md: calc(1rem * var(--adaptive-scale));
                --font-size-lg: calc(1.25rem * var(--adaptive-scale));
                --font-size-xl: calc(1.5rem * var(--adaptive-scale));
                
                /* Form element sizes */
                --input-height: calc(38px * var(--adaptive-scale));
                --input-font-size: calc(0.9rem * var(--adaptive-scale));
                --input-padding: calc(0.4rem * var(--adaptive-scale)) calc(0.6rem * var(--adaptive-scale));
                --textarea-height: calc(80px * var(--adaptive-scale));
                --label-font-size: calc(0.9rem * var(--adaptive-scale));
                --helper-font-size: calc(0.85rem * var(--adaptive-scale));
                
                /* Post and content sizes */
                --post-title-size: calc(1.4rem * var(--adaptive-scale));
                --post-meta-size: calc(0.85rem * var(--adaptive-scale));
                --post-content-size: calc(1rem * var(--adaptive-scale));
                --comment-content-size: calc(0.95rem * var(--adaptive-scale));
                --comment-meta-size: calc(0.8rem * var(--adaptive-scale));
                
                /* Components sizes */
                --icon-size-xs: calc(0.7rem * var(--adaptive-scale));
                --icon-size-sm: calc(0.9rem * var(--adaptive-scale));
                --icon-size-md: calc(1.1rem * var(--adaptive-scale));
                --icon-size-lg: calc(1.3rem * var(--adaptive-scale));
                
                /* Touch targets */
                --touch-target-size: calc(44px * var(--adaptive-scale));
                --min-touch-target: calc(32px * var(--adaptive-scale));
            }
        `;
        document.head.appendChild(style);
        
        // Get current scale and log it
        const scale = window.innerWidth < 576 ? '0.85' : (window.innerWidth < 992 ? '0.92' : '1');
        console.log("Setting adaptive scale to:", scale);
        
        // Add adaptive classes to various elements
        addAdaptiveClasses();
    }
    
    /**
     * Apply adaptive sizing to all elements
     * Uses both CSS variables and direct style manipulation
     */
    function applyAdaptiveSizing() {
        const windowWidth = window.innerWidth;
        const windowHeight = window.innerHeight;
        const devicePixelRatio = window.devicePixelRatio || 1;
        
        // Determine device category (with high precision)
        const isExtraSmallMobile = windowWidth < 360;
        const isSmallMobile = windowWidth >= 360 && windowWidth < 480;
        const isMobile = windowWidth < 576;
        const isTablet = windowWidth >= 576 && windowWidth < 992;
        const isDesktop = windowWidth >= 992 && windowWidth < 1400;
        const isLargeDesktop = windowWidth >= 1400;
        
        console.log("Applying responsive layout: Mobile: " + isMobile + ", Tablet: " + isTablet);
        
        // Update root CSS variables based on device
        const root = document.documentElement;
        if (isExtraSmallMobile) {
            root.style.setProperty('--adaptive-scale', '0.75'); // Smallest scale for very small devices
        } else if (isSmallMobile) {
            root.style.setProperty('--adaptive-scale', '0.85'); // Small mobile (phones)
        } else if (isMobile) {
            root.style.setProperty('--adaptive-scale', '0.9'); // Regular mobile
        } else if (isTablet) {
            root.style.setProperty('--adaptive-scale', '0.95'); // Tablets
        } else if (isDesktop) {
            root.style.setProperty('--adaptive-scale', '1'); // Regular desktops
        } else {
            root.style.setProperty('--adaptive-scale', '1.1'); // Large desktops
        }
        
        // Apply typography scaling
        applyTypographyScaling(isMobile, isTablet, isDesktop, isLargeDesktop);
        
        // Apply component sizing
        applyComponentSizing(isMobile, isTablet, isDesktop, isLargeDesktop);
        
        // Apply spacing adjustments
        applySpacingAdjustments(isMobile, isTablet, isDesktop);
        
        // Apply layout specific adjustments
        applyLayoutAdjustments(windowWidth, windowHeight);
        
        // Apply adaptive icon sizing with intelligent calculations
        applyAdaptiveIconSizing();
        
        // Apply special sizing for high-density screens
        if (devicePixelRatio > 2) {
            applyHighDensityAdjustments();
        }
        
        // Optimize touch targets for mobile
        if (isMobile || isTablet) {
            optimizeTouchTargets();
        }
    }
    
    /**
     * Apply typography scaling based on device
     */
    function applyTypographyScaling(isMobile, isTablet, isDesktop, isLargeDesktop) {
        // Post titles with adaptive font sizing
        document.querySelectorAll('.post-title, h1.article-title, .community-title, .profile-name, .page-title, h1').forEach(el => {
            if (isMobile) {
                el.style.fontSize = 'var(--font-size-lg)';
                el.style.lineHeight = '1.3';
                el.style.marginBottom = '0.5rem';
                el.style.fontWeight = '600';
            } else if (isTablet) {
                el.style.fontSize = 'calc(var(--font-size-lg) * 1.1)';
                el.style.lineHeight = '1.4';
                el.style.marginBottom = '0.75rem';
                el.style.fontWeight = '600';
            } else if (isDesktop) {
                el.style.fontSize = 'calc(var(--font-size-lg) * 1.2)';
                el.style.lineHeight = '1.5';
                el.style.marginBottom = '1rem';
                el.style.fontWeight = '700';
            } else {
                el.style.fontSize = 'calc(var(--font-size-lg) * 1.3)';
                el.style.lineHeight = '1.5';
                el.style.marginBottom = '1rem';
                el.style.fontWeight = '700';
            }
        });
        
        // Secondary titles
        document.querySelectorAll('h2, .section-title, .post-subtitle, .card-header, .modal-title').forEach(el => {
            if (isMobile) {
                el.style.fontSize = 'var(--font-size-md)';
                el.style.lineHeight = '1.3';
                el.style.marginBottom = '0.5rem';
                el.style.fontWeight = '600';
            } else if (isTablet) {
                el.style.fontSize = 'calc(var(--font-size-md) * 1.1)';
                el.style.lineHeight = '1.4';
                el.style.marginBottom = '0.75rem';
                el.style.fontWeight = '600';
            } else {
                el.style.fontSize = 'calc(var(--font-size-md) * 1.2)';
                el.style.lineHeight = '1.5';
                el.style.marginBottom = '1rem';
                el.style.fontWeight = '700';
            }
        });
        
        // Tertiary titles
        document.querySelectorAll('h3, h4, h5, h6, .panel-title').forEach(el => {
            if (isMobile) {
                el.style.fontSize = 'calc(var(--font-size-md) * 0.9)';
                el.style.lineHeight = '1.3';
                el.style.marginBottom = '0.5rem';
                el.style.fontWeight = '600';
            } else if (isTablet) {
                el.style.fontSize = 'var(--font-size-md)';
                el.style.lineHeight = '1.4';
                el.style.marginBottom = '0.75rem';
                el.style.fontWeight = '600';
            } else {
                el.style.fontSize = 'calc(var(--font-size-md) * 1.1)';
                el.style.lineHeight = '1.5';
                el.style.marginBottom = '0.75rem';
                el.style.fontWeight = '600';
            }
        });
        
        // Meta information and small text
        document.querySelectorAll('.meta-info, .post-meta, .card-subtitle, .text-muted, small, .text-sm, .comment-meta, .submission-info, .vote-count, .timestamp, .author, .community-name, .meta-text, .badge').forEach(el => {
            if (isMobile) {
                el.style.fontSize = 'var(--font-size-xs)';
                el.style.lineHeight = '1.2';
                el.style.marginBottom = '0.25rem';
            } else if (isTablet) {
                el.style.fontSize = 'var(--font-size-sm)';
                el.style.lineHeight = '1.3';
                el.style.marginBottom = '0.5rem';
            } else {
                el.style.fontSize = 'calc(var(--font-size-sm) * 1.05)';
                el.style.lineHeight = '1.4';
                el.style.marginBottom = '0.5rem';
            }
        });
        
        // Body text and general content
        document.querySelectorAll('.post-content, .comment-content, .card-text, .card-body, p:not(.meta-info):not(.card-subtitle), .list-group-item, .markdown-content, article, .post-text, div.text, .form-text, blockquote, .alert, .notification-text').forEach(el => {
            if (isMobile) {
                el.style.fontSize = 'var(--font-size-sm)';
                el.style.lineHeight = '1.4';
                el.style.marginBottom = '0.5rem';
            } else if (isTablet) {
                el.style.fontSize = 'var(--font-size-md)';
                el.style.lineHeight = '1.5';
                el.style.marginBottom = '0.75rem';
            } else {
                el.style.fontSize = 'calc(var(--font-size-md) * 1.05)';
                el.style.lineHeight = '1.6';
                el.style.marginBottom = '1rem';
            }
        });
        
        // Navigation and menu items
        document.querySelectorAll('.nav-link, .dropdown-item, .menu-item, .list-group-item, .sidebar-link').forEach(el => {
            if (isMobile) {
                el.style.fontSize = 'var(--font-size-sm)';
                el.style.padding = '0.25rem 0.5rem';
            } else if (isTablet) {
                el.style.fontSize = 'var(--font-size-sm)';
                el.style.padding = '0.375rem 0.75rem';
            } else {
                el.style.fontSize = 'var(--font-size-md)';
                el.style.padding = '0.5rem 1rem';
            }
        });
        
        // Form labels and form elements
        document.querySelectorAll('label, .form-label, legend').forEach(el => {
            if (isMobile) {
                el.style.fontSize = 'var(--font-size-sm)';
                el.style.marginBottom = '0.25rem';
                el.style.fontWeight = '600';
            } else {
                el.style.fontSize = 'var(--font-size-md)';
                el.style.marginBottom = '0.5rem';
                el.style.fontWeight = '600';
            }
        });
    }
    
    /**
     * Apply component sizing for cards, buttons, etc.
     */
    function applyComponentSizing(isMobile, isTablet, isDesktop, isLargeDesktop) {
        // Cards and containers
        document.querySelectorAll('.card, .list-group-item').forEach(el => {
            // Adaptive border radius
            el.style.borderRadius = isMobile ? '0.25rem' : '0.375rem';
            
            // Adaptive padding
            if (el.classList.contains('card') && el.querySelector('.card-body')) {
                const cardBody = el.querySelector('.card-body');
                if (isMobile) {
                    cardBody.style.padding = 'var(--spacing-sm)';
                } else if (isTablet) {
                    cardBody.style.padding = 'var(--spacing-md)';
                } else {
                    cardBody.style.padding = 'calc(var(--spacing-md) * 1.1)';
                }
            }
        });
        
        // Buttons scaling - all types of buttons
        document.querySelectorAll('.btn:not(.btn-sm):not(.btn-lg), button:not(.btn-sm):not(.btn-lg):not(.btn-close)').forEach(el => {
            if (isMobile) {
                el.style.padding = '0.2rem 0.5rem';
                el.style.fontSize = 'var(--font-size-sm)';
                el.style.minHeight = '32px';
            } else if (isTablet) {
                el.style.padding = '0.3rem 0.6rem';
                el.style.fontSize = 'var(--font-size-sm)';
                el.style.minHeight = '36px';
            } else {
                el.style.padding = '0.375rem 0.75rem';
                el.style.fontSize = 'var(--font-size-md)';
                el.style.minHeight = '38px';
            }
        });
        
        // Small buttons
        document.querySelectorAll('.btn-sm, button.btn-sm').forEach(el => {
            if (isMobile) {
                el.style.padding = '0.1rem 0.3rem';
                el.style.fontSize = 'var(--font-size-xs)';
                el.style.minHeight = '28px';
            } else {
                el.style.padding = '0.2rem 0.4rem';
                el.style.fontSize = 'var(--font-size-sm)';
                el.style.minHeight = '30px';
            }
        });
        
        // Badges
        document.querySelectorAll('.badge').forEach(el => {
            if (isMobile) {
                el.style.fontSize = 'var(--font-size-xs)';
            } else if (isTablet) {
                el.style.fontSize = 'var(--font-size-sm)';
            } else {
                el.style.fontSize = 'var(--font-size-sm)';
            }
        });
        
        // Adjust form controls - all inputs and textareas
        document.querySelectorAll('.form-control, .form-select, input:not([type="checkbox"]):not([type="radio"]), textarea, select, .comment-form textarea, .post-form textarea, .markdownx-editor, .markdownx-preview, .comment-textarea, .post-textarea, form textarea, form input[type="text"], form input[type="email"], form input[type="password"], form input[type="search"], form input[type="url"], form input[type="number"], form select').forEach(el => {
            if (isMobile) {
                el.style.padding = '0.2rem 0.4rem';
                el.style.fontSize = 'var(--font-size-sm)';
                el.style.minHeight = el.tagName === 'TEXTAREA' ? '80px' : '32px';
                el.style.width = '100%';
                el.style.maxWidth = '100%';
                el.style.borderRadius = '0.25rem';
                el.style.border = '1px solid #444';
                el.style.backgroundColor = '#2c2c2c';
                el.style.color = '#f8f9fa';
            } else if (isTablet) {
                el.style.padding = '0.25rem 0.5rem';
                el.style.fontSize = 'var(--font-size-md)';
                el.style.minHeight = el.tagName === 'TEXTAREA' ? '100px' : '36px';
                el.style.width = '100%';
                el.style.maxWidth = '100%';
                el.style.borderRadius = '0.25rem';
                el.style.border = '1px solid #444';
                el.style.backgroundColor = '#2c2c2c';
                el.style.color = '#f8f9fa';
            } else {
                el.style.padding = '0.3rem 0.6rem';
                el.style.fontSize = 'var(--font-size-md)';
                el.style.minHeight = el.tagName === 'TEXTAREA' ? '120px' : '38px';
                el.style.width = '100%';
                el.style.maxWidth = '100%';
                el.style.borderRadius = '0.25rem';
                el.style.border = '1px solid #444';
                el.style.backgroundColor = '#2c2c2c';
                el.style.color = '#f8f9fa';
            }
            
            // Apply proper focus styles
            el.addEventListener('focus', function() {
                this.style.borderColor = '#4285f4';
                this.style.boxShadow = '0 0 0 0.25rem rgba(66, 133, 244, 0.25)';
            });
            
            el.addEventListener('blur', function() {
                this.style.borderColor = '#444';
                this.style.boxShadow = 'none';
            });
        });
        
        // Image sizing - all content images
        document.querySelectorAll('img:not(.avatar):not(.nav-avatar):not(.fixed-size)').forEach(el => {
            if (isMobile) {
                el.style.maxHeight = '200px';
            } else if (isTablet) {
                el.style.maxHeight = '300px';
            } else if (isDesktop) {
                el.style.maxHeight = '400px';
            } else {
                el.style.maxHeight = '500px';
            }
        });
        
        // Voting buttons and score
        document.querySelectorAll('.vote-btn, .vote-arrow').forEach(el => {
            if (isMobile) {
                el.style.fontSize = '1.3rem';
                el.style.minWidth = '32px';
                el.style.minHeight = '32px';
                // Target the icon inside
                const icon = el.querySelector('i');
                if (icon) {
                    icon.style.fontSize = '1.3rem';
                }
            } else if (isTablet) {
                el.style.fontSize = '1.4rem';
                el.style.minWidth = '36px';
                el.style.minHeight = '36px';
                // Target the icon inside
                const icon = el.querySelector('i');
                if (icon) {
                    icon.style.fontSize = '1.4rem';
                }
            } else {
                el.style.fontSize = '1.5rem';
                el.style.minWidth = '40px';
                el.style.minHeight = '40px';
                // Target the icon inside
                const icon = el.querySelector('i');
                if (icon) {
                    icon.style.fontSize = '1.5rem';
                }
            }
        });
        
        // Vote count
        document.querySelectorAll('.vote-count').forEach(el => {
            if (isMobile) {
                el.style.fontSize = 'var(--font-size-sm)';
                el.style.fontWeight = '600';
            } else if (isTablet) {
                el.style.fontSize = 'var(--font-size-md)';
                el.style.fontWeight = '600';
            } else {
                el.style.fontSize = 'var(--font-size-md)';
                el.style.fontWeight = '700';
            }
        });
        
        // Post fields and text content
        document.querySelectorAll('.post-content, .comment-content, .markdown-content, article, .post-text').forEach(el => {
            if (isMobile) {
                el.style.fontSize = 'var(--font-size-sm)';
                el.style.lineHeight = '1.4';
            } else if (isTablet) {
                el.style.fontSize = 'var(--font-size-md)';
                el.style.lineHeight = '1.5';
            } else {
                el.style.fontSize = 'var(--font-size-md)';
                el.style.lineHeight = '1.6';
            }
        });
        
        // Tables
        document.querySelectorAll('table, .table').forEach(el => {
            if (isMobile) {
                el.style.fontSize = 'var(--font-size-xs)';
            } else if (isTablet) {
                el.style.fontSize = 'var(--font-size-sm)';
            } else {
                el.style.fontSize = 'var(--font-size-md)';
            }
            
            // Adjust table cells
            el.querySelectorAll('th, td').forEach(cell => {
                if (isMobile) {
                    cell.style.padding = '0.25rem 0.5rem';
                } else if (isTablet) {
                    cell.style.padding = '0.5rem 0.75rem';
                } else {
                    cell.style.padding = '0.75rem 1rem';
                }
            });
        });
        
        // Lists
        document.querySelectorAll('ul:not(.nav):not(.navbar-nav), ol').forEach(el => {
            if (isMobile) {
                el.style.fontSize = 'var(--font-size-sm)';
                el.style.padding = '0 0 0 1rem';
            } else if (isTablet) {
                el.style.fontSize = 'var(--font-size-md)';
                el.style.padding = '0 0 0 1.5rem';
            } else {
                el.style.fontSize = 'var(--font-size-md)';
                el.style.padding = '0 0 0 2rem';
            }
        });
    }
    
    /**
     * Apply spacing adjustments to margins and paddings
     */
    function applySpacingAdjustments(isMobile, isTablet, isDesktop) {
        // Page sections and containers
        document.querySelectorAll('.container, .container-fluid, section, main').forEach(el => {
            if (isMobile) {
                el.style.padding = 'var(--spacing-sm)';
                el.style.margin = 'var(--spacing-sm) 0';
            } else if (isTablet) {
                el.style.padding = 'var(--spacing-md)';
                el.style.margin = 'var(--spacing-md) 0';
            } else {
                el.style.padding = 'var(--spacing-lg)';
                el.style.margin = 'var(--spacing-lg) 0';
            }
        });
        
        // Card spacing and padding
        document.querySelectorAll('.card, .card-body, .list-group-item, .alert, .modal-body').forEach(el => {
            if (isMobile) {
                el.style.padding = 'var(--spacing-sm)';
                el.style.marginBottom = 'var(--spacing-sm)';
            } else if (isTablet) {
                el.style.padding = 'var(--spacing-md)';
                el.style.marginBottom = 'var(--spacing-md)';
            } else {
                el.style.padding = 'var(--spacing-md)';
                el.style.marginBottom = 'var(--spacing-md)';
            }
        });
        
        // Lists and content spacing
        document.querySelectorAll('.list-group, .post-item, .comment-item, .notification-item').forEach(el => {
            if (isMobile) {
                el.style.marginBottom = 'var(--spacing-xs)';
            } else if (isTablet) {
                el.style.marginBottom = 'var(--spacing-sm)';
            } else {
                el.style.marginBottom = 'var(--spacing-md)';
            }
        });
        
        // Form groups and input spacing
        document.querySelectorAll('.form-group, .mb-3, .form-control, .form-select, textarea').forEach(el => {
            if (isMobile) {
                el.style.marginBottom = 'var(--spacing-sm)';
            } else {
                el.style.marginBottom = 'var(--spacing-md)';
            }
        });
        
        // Buttons and interactive elements spacing
        document.querySelectorAll('.btn, button, .nav-item, .dropdown-item').forEach(el => {
            if (isMobile) {
                el.style.margin = '0.15rem';
            } else if (isTablet) {
                el.style.margin = '0.25rem';
            } else {
                el.style.margin = '0.3rem';
            }
        });
        
        // Post contents and comment spacing
        document.querySelectorAll('.post-content, .comment-content, .markdown-content').forEach(el => {
            if (isMobile) {
                el.style.padding = 'var(--spacing-sm)';
                el.style.margin = 'var(--spacing-sm) 0';
            } else if (isTablet) {
                el.style.padding = 'var(--spacing-md)';
                el.style.margin = 'var(--spacing-md) 0';
            } else {
                el.style.padding = 'var(--spacing-md)';
                el.style.margin = 'var(--spacing-md) 0';
            }
        });
        
        // Vote button spacing
        document.querySelectorAll('.vote-container, .vote-wrapper').forEach(el => {
            if (isMobile) {
                el.style.gap = '0.25rem';
                el.style.margin = '0 0.5rem 0 0';
            } else {
                el.style.gap = '0.5rem';
                el.style.margin = '0 0.75rem 0 0';
            }
        });
    }
    
    /**
     * Apply layout adjustments specific to certain pages
     */
    function applyLayoutAdjustments(windowWidth, windowHeight) {
        // Check if we're on profile page
        if (document.querySelector('.profile-header')) {
            const profileHeader = document.querySelector('.profile-header');
            if (windowWidth < 576) {
                profileHeader.style.flexDirection = 'column';
                profileHeader.style.alignItems = 'center';
                profileHeader.style.padding = 'var(--spacing-sm)';
                
                // Adjust profile elements for mobile
                const profileAvatar = document.querySelector('.profile-avatar');
                if (profileAvatar) {
                    profileAvatar.style.width = '80px';
                    profileAvatar.style.height = '80px';
                    profileAvatar.style.margin = '0 0 1rem 0';
                }
                
                const profileStats = document.querySelector('.profile-stats');
                if (profileStats) {
                    profileStats.style.flexDirection = 'row';
                    profileStats.style.justifyContent = 'center';
                    profileStats.style.width = '100%';
                    profileStats.style.marginTop = '0.5rem';
                }
            } else {
                profileHeader.style.flexDirection = 'row';
                profileHeader.style.alignItems = 'flex-start';
                profileHeader.style.padding = 'var(--spacing-lg)';
                
                // Adjust profile elements for desktop
                const profileAvatar = document.querySelector('.profile-avatar');
                if (profileAvatar) {
                    profileAvatar.style.width = '120px';
                    profileAvatar.style.height = '120px';
                    profileAvatar.style.margin = '0 1.5rem 0 0';
                }
                
                const profileStats = document.querySelector('.profile-stats');
                if (profileStats) {
                    profileStats.style.flexDirection = 'row';
                    profileStats.style.justifyContent = 'flex-start';
                    profileStats.style.width = 'auto';
                    profileStats.style.marginTop = '1rem';
                }
            }
        }
        
        // Check if we're on community page
        if (document.querySelector('.community-header')) {
            const communityHeader = document.querySelector('.community-header');
            if (windowWidth < 576) {
                communityHeader.style.padding = 'var(--spacing-sm)';
                
                // Adjust community elements for mobile
                const communityTitle = document.querySelector('.community-title');
                if (communityTitle) {
                    communityTitle.style.fontSize = 'var(--font-size-lg)';
                    communityTitle.style.textAlign = 'center';
                    communityTitle.style.marginBottom = '0.5rem';
                }
                
                const communityDescription = document.querySelector('.community-description');
                if (communityDescription) {
                    communityDescription.style.fontSize = 'var(--font-size-sm)';
                    communityDescription.style.textAlign = 'center';
                }
            } else {
                communityHeader.style.padding = 'var(--spacing-lg)';
                
                // Adjust community elements for desktop
                const communityTitle = document.querySelector('.community-title');
                if (communityTitle) {
                    communityTitle.style.fontSize = 'calc(var(--font-size-lg) * 1.2)';
                    communityTitle.style.textAlign = 'left';
                    communityTitle.style.marginBottom = '1rem';
                }
                
                const communityDescription = document.querySelector('.community-description');
                if (communityDescription) {
                    communityDescription.style.fontSize = 'var(--font-size-md)';
                    communityDescription.style.textAlign = 'left';
                }
            }
        }
        
        // Post detail layout
        if (document.querySelector('.post-detail')) {
            const postDetail = document.querySelector('.post-detail');
            const postContent = document.querySelector('.post-content');
            const postTitle = document.querySelector('.post-title');
            const postMeta = document.querySelector('.post-meta');
            const commentSection = document.querySelector('.comment-section');
            
            if (windowWidth < 576) {
                // Simplify layout on mobile
                document.querySelectorAll('.post-sidebar').forEach(el => {
                    el.style.display = 'none';
                });
                
                if (postDetail) postDetail.style.padding = 'var(--spacing-sm)';
                if (postContent) {
                    postContent.style.fontSize = 'var(--font-size-sm)';
                    postContent.style.lineHeight = '1.4';
                    postContent.style.padding = 'var(--spacing-sm)';
                }
                if (postTitle) {
                    postTitle.style.fontSize = 'var(--font-size-lg)';
                    postTitle.style.marginBottom = '0.5rem';
                }
                if (postMeta) {
                    postMeta.style.fontSize = 'var(--font-size-xs)';
                    postMeta.style.marginBottom = '0.75rem';
                }
                if (commentSection) {
                    commentSection.style.marginTop = '1rem';
                    commentSection.style.padding = 'var(--spacing-sm)';
                }
            } else {
                document.querySelectorAll('.post-sidebar').forEach(el => {
                    el.style.display = 'block';
                });
                
                if (postDetail) postDetail.style.padding = 'var(--spacing-lg)';
                if (postContent) {
                    postContent.style.fontSize = 'var(--font-size-md)';
                    postContent.style.lineHeight = '1.6';
                    postContent.style.padding = 'var(--spacing-md)';
                }
                if (postTitle) {
                    postTitle.style.fontSize = 'calc(var(--font-size-lg) * 1.2)';
                    postTitle.style.marginBottom = '1rem';
                }
                if (postMeta) {
                    postMeta.style.fontSize = 'var(--font-size-sm)';
                    postMeta.style.marginBottom = '1.5rem';
                }
                if (commentSection) {
                    commentSection.style.marginTop = '2rem';
                    commentSection.style.padding = 'var(--spacing-md)';
                }
            }
        }
        
        // Notification page layout
        if (document.querySelector('.notifications-page')) {
            const notificationList = document.querySelector('.notification-list');
            const notificationItems = document.querySelectorAll('.notification-item');
            
            if (windowWidth < 576) {
                if (notificationList) {
                    notificationList.style.padding = 'var(--spacing-sm)';
                }
                
                notificationItems.forEach(item => {
                    item.style.padding = 'var(--spacing-sm)';
                    item.style.marginBottom = 'var(--spacing-xs)';
                    item.style.fontSize = 'var(--font-size-sm)';
                });
            } else {
                if (notificationList) {
                    notificationList.style.padding = 'var(--spacing-md)';
                }
                
                notificationItems.forEach(item => {
                    item.style.padding = 'var(--spacing-md)';
                    item.style.marginBottom = 'var(--spacing-sm)';
                    item.style.fontSize = 'var(--font-size-md)';
                });
            }
        }
        
        // Message page layout
        if (document.querySelector('.messages-page, .postman')) {
            const messageList = document.querySelector('.message-list, .pm_list');
            const messageItems = document.querySelectorAll('.message-item, .pm_message');
            
            if (windowWidth < 576) {
                if (messageList) {
                    messageList.style.padding = 'var(--spacing-sm)';
                }
                
                messageItems.forEach(item => {
                    item.style.padding = 'var(--spacing-sm)';
                    item.style.marginBottom = 'var(--spacing-xs)';
                    item.style.fontSize = 'var(--font-size-sm)';
                });
            } else {
                if (messageList) {
                    messageList.style.padding = 'var(--spacing-md)';
                }
                
                messageItems.forEach(item => {
                    item.style.padding = 'var(--spacing-md)';
                    item.style.marginBottom = 'var(--spacing-sm)';
                    item.style.fontSize = 'var(--font-size-md)';
                });
            }
        }
        
        // Form layouts
        document.querySelectorAll('form').forEach(form => {
            if (windowWidth < 576) {
                form.style.padding = 'var(--spacing-sm)';
                
                const formGroups = form.querySelectorAll('.form-group, .mb-3');
                formGroups.forEach(group => {
                    group.style.marginBottom = 'var(--spacing-sm)';
                });
                
                const labels = form.querySelectorAll('label');
                labels.forEach(label => {
                    label.style.fontSize = 'var(--font-size-sm)';
                    label.style.marginBottom = '0.25rem';
                });
            } else {
                form.style.padding = 'var(--spacing-md)';
                
                const formGroups = form.querySelectorAll('.form-group, .mb-3');
                formGroups.forEach(group => {
                    group.style.marginBottom = 'var(--spacing-md)';
                });
                
                const labels = form.querySelectorAll('label');
                labels.forEach(label => {
                    label.style.fontSize = 'var(--font-size-md)';
                    label.style.marginBottom = '0.5rem';
                });
            }
        });
    }
    
    /**
     * Apply adaptive icon sizing with intelligent calculations
     */
    function applyAdaptiveIconSizing() {
        // Adjust all icons with the adaptive-icon class
        document.querySelectorAll('.adaptive-icon').forEach(icon => {
            const containerWidth = icon.parentElement ? icon.parentElement.offsetWidth : 0;
            const containerHeight = icon.parentElement ? icon.parentElement.offsetHeight : 0;
            
            // Intelligent size calculation based on parent container dimensions
            let calculatedSize;
            if (containerWidth < 30 || containerHeight < 30) {
                calculatedSize = 'var(--icon-size-xs)';
            } else if (containerWidth < 60 || containerHeight < 60) {
                calculatedSize = 'var(--icon-size-sm)';
            } else if (containerWidth < 100 || containerHeight < 100) {
                calculatedSize = 'var(--icon-size-md)';
            } else {
                calculatedSize = 'var(--icon-size-lg)';
            }
            
            // Apply the calculated size
            icon.style.fontSize = calculatedSize;
        });
        
        // Special handling for header icons
        adaptHeaderIcons();
    }
    
    /**
     * Apply specialized adjustments for high-density screens
     */
    function applyHighDensityAdjustments() {
        // Adjust for high DPI screens to make touch targets more comfortable
        document.querySelectorAll('button, .btn, a.nav-link, .form-control, .form-select').forEach(el => {
            // Ensure touch targets are optimized for high DPI
            if (el.offsetHeight < 38) {
                el.style.minHeight = '38px';
            }
        });
    }
    
    /**
     * Optimize touch targets for mobile devices
     */
    function optimizeTouchTargets() {
        // Focus on interactive elements
        const touchableElements = document.querySelectorAll('button, .btn, a, input, select, textarea, .nav-link, .dropdown-item');
        
        touchableElements.forEach(el => {
            // Don't modify hidden or specially classed elements
            if (el.offsetHeight === 0 || el.classList.contains('no-touch-optimize')) {
                return;
            }
            
            // Make sure clickable elements are at least 32px high for better touch targeting
            const elHeight = el.offsetHeight;
            if (elHeight > 0 && elHeight < 32) {
                if (el.tagName === 'A' && !el.classList.contains('btn')) {
                    // For inline links, increase padding without breaking layout
                    el.style.padding = '0.3rem 0.1rem';
                    el.style.display = 'inline-block';
                } else {
                    // For other elements, set minimum height
                    el.style.minHeight = 'var(--min-touch-target)';
                    
                    // For buttons, also ensure adequate width
                    if (el.tagName === 'BUTTON' || el.classList.contains('btn')) {
                        el.style.minWidth = 'var(--min-touch-target)';
                    }
                }
            }
        });
        
        // Increase spacing between touch targets if they're too close
        document.querySelectorAll('.btn-group, .nav, .list-group, .dropdown-menu').forEach(container => {
            const children = container.children;
            for (let i = 0; i < children.length; i++) {
                if (children[i].tagName === 'A' || children[i].tagName === 'BUTTON' || 
                    children[i].classList.contains('btn') || children[i].classList.contains('nav-item')) {
                    children[i].style.margin = '0.15rem';
                }
            }
        });
    }
    
    /**
     * Add adaptive classes to various elements that need them
     */
    function addAdaptiveClasses() {
        // Identify elements that should be adaptive but don't have the class
        document.querySelectorAll('.bi').forEach(icon => {
            if (!icon.classList.contains('adaptive-icon')) {
                icon.classList.add('adaptive-icon');
            }
        });
        
        // Add adaptive classes to card elements
        document.querySelectorAll('.card, .post-card, .post-item, .comment-card, .community-card, .profile-card').forEach(el => {
            if (!el.classList.contains('adaptive-card')) {
                el.classList.add('adaptive-card');
                el.style.transition = 'all 0.2s ease-in-out';
                el.style.marginBottom = 'var(--spacing-md)';
                el.style.borderRadius = '0.25rem';
                
                // Find and style card body if exists
                const cardBody = el.querySelector('.card-body');
                if (cardBody) {
                    cardBody.style.padding = 'var(--spacing-md)';
                    cardBody.style.transition = 'padding 0.2s ease-in-out';
                }
            }
        });
        
        // Identify containers that should have adaptive spacing
        document.querySelectorAll('.list-group-item, .nav-item, .dropdown-item').forEach(el => {
            if (!el.classList.contains('adaptive-spacing')) {
                el.classList.add('adaptive-spacing');
                el.style.transition = 'all 0.2s ease-in-out';
            }
        });
        
        // Add form element adaptive classes
        document.querySelectorAll('input:not([type="checkbox"]):not([type="radio"]), textarea, select, .form-control, .form-select').forEach(el => {
            if (!el.classList.contains('adaptive-form-control')) {
                el.classList.add('adaptive-form-control');
                
                // Apply specific styles based on CSS variables
                if (el.tagName === 'TEXTAREA') {
                    el.style.minHeight = 'var(--textarea-height)';
                } else {
                    el.style.minHeight = 'var(--input-height)';
                }
                el.style.fontSize = 'var(--input-font-size)';
                el.style.padding = 'var(--input-padding)';
                el.style.transition = 'all 0.2s ease-in-out';
                el.style.backgroundColor = '#2c2c2c';
                el.style.border = '1px solid #444';
                el.style.color = '#f8f9fa';
                el.style.borderRadius = '0.25rem';
            }
        });
        
        // Add form label adaptive classes
        document.querySelectorAll('label, .form-label').forEach(el => {
            if (!el.classList.contains('adaptive-form-label')) {
                el.classList.add('adaptive-form-label');
                el.style.fontSize = 'var(--label-font-size)';
                el.style.fontWeight = '500';
                el.style.marginBottom = '0.3rem';
                el.style.color = '#e9ecef';
                el.style.transition = 'all 0.2s ease-in-out';
            }
        });
        
        // Add content adaptive classes to all headings
        document.querySelectorAll('.post-title, h1.article-title, .community-title, .profile-name, .page-title, h1, h2.card-title, h2 a.post-title').forEach(el => {
            if (!el.classList.contains('adaptive-post-title')) {
                el.classList.add('adaptive-post-title');
                el.style.fontSize = 'var(--post-title-size)';
                el.style.fontWeight = '600';
                el.style.lineHeight = '1.3';
                el.style.marginBottom = '0.5rem';
                el.style.transition = 'all 0.2s ease-in-out';
            }
        });
        
        // Add adaptive classes to meta information
        document.querySelectorAll('.post-meta, .post-info, .post-details, .meta-info, .card-subtitle, .submission-info, .timestamp, .author, .community-name, .meta-text, .small.text-muted').forEach(el => {
            if (!el.classList.contains('adaptive-meta')) {
                el.classList.add('adaptive-meta');
                el.style.fontSize = 'var(--post-meta-size)';
                el.style.color = '#adb5bd';
                el.style.marginBottom = '0.5rem';
                el.style.transition = 'all 0.2s ease-in-out';
            }
        });
        
        // Add adaptive classes to content
        document.querySelectorAll('.post-content, .post-body, .post-text, .card-text, .markdown-content, article, .text, .content-text, p:not(.meta-info):not(.card-subtitle)').forEach(el => {
            if (!el.classList.contains('adaptive-content')) {
                el.classList.add('adaptive-content');
                el.style.fontSize = 'var(--post-content-size)';
                el.style.lineHeight = '1.5';
                el.style.marginBottom = '1rem';
                el.style.transition = 'all 0.2s ease-in-out';
            }
        });
        
        // Add adaptive classes to URLs and links
        document.querySelectorAll('.post-url, .card a:not(.btn):not(.post-title), .external-link').forEach(el => {
            if (!el.classList.contains('adaptive-link')) {
                el.classList.add('adaptive-link');
                el.style.fontSize = 'calc(var(--post-meta-size) * 1.05)';
                el.style.overflowWrap = 'break-word';
                el.style.wordWrap = 'break-word';
                el.style.wordBreak = 'break-word';
                el.style.transition = 'all 0.2s ease-in-out';
            }
        });
        
        // Add adaptive classes to comments
        document.querySelectorAll('.comment-body, .comment-content, .reply-body, .reply-content, .comment-text').forEach(el => {
            if (!el.classList.contains('adaptive-comment-content')) {
                el.classList.add('adaptive-comment-content');
                el.style.fontSize = 'var(--comment-content-size)';
                el.style.lineHeight = '1.4';
                el.style.transition = 'all 0.2s ease-in-out';
            }
        });
        
        document.querySelectorAll('.comment-meta, .comment-info, .reply-meta, .reply-info').forEach(el => {
            if (!el.classList.contains('adaptive-comment-meta')) {
                el.classList.add('adaptive-comment-meta');
                el.style.fontSize = 'var(--comment-meta-size)';
                el.style.color = '#adb5bd';
                el.style.transition = 'all 0.2s ease-in-out';
            }
        });
        
        // Add adaptive classes to vote controls
        document.querySelectorAll('.vote-column, .vote-controls').forEach(el => {
            if (!el.classList.contains('adaptive-vote-control')) {
                el.classList.add('adaptive-vote-control');
                el.style.display = 'flex';
                el.style.flexDirection = 'column';
                el.style.alignItems = 'center';
                el.style.marginRight = '0.5rem';
                el.style.transition = 'all 0.2s ease-in-out';
                
                // Size based on device width
                const windowWidth = window.innerWidth;
                if (windowWidth < 576) {
                    el.style.minWidth = 'var(--vote-btn-size-mobile)';
                } else if (windowWidth >= 576 && windowWidth < 992) {
                    el.style.minWidth = 'var(--vote-btn-size-tablet)';
                } else {
                    el.style.minWidth = 'var(--vote-btn-size-desktop)';
                }
            }
        });
        
        // Style vote buttons
        document.querySelectorAll('.vote-btn').forEach(el => {
            if (!el.classList.contains('adaptive-vote-btn')) {
                el.classList.add('adaptive-vote-btn');
                el.style.display = 'flex';
                el.style.alignItems = 'center';
                el.style.justifyContent = 'center';
                el.style.transition = 'all 0.2s ease-in-out';
                
                // Size based on device width
                const windowWidth = window.innerWidth;
                if (windowWidth < 576) {
                    el.style.minWidth = 'var(--vote-btn-size-mobile)';
                    el.style.minHeight = 'var(--vote-btn-size-mobile)';
                    
                    // Style icon inside
                    const icon = el.querySelector('i');
                    if (icon) {
                        icon.style.fontSize = 'var(--vote-icon-size-mobile)';
                    }
                } else if (windowWidth >= 576 && windowWidth < 992) {
                    el.style.minWidth = 'var(--vote-btn-size-tablet)';
                    el.style.minHeight = 'var(--vote-btn-size-tablet)';
                    
                    // Style icon inside
                    const icon = el.querySelector('i');
                    if (icon) {
                        icon.style.fontSize = 'var(--vote-icon-size-tablet)';
                    }
                } else {
                    el.style.minWidth = 'var(--vote-btn-size-desktop)';
                    el.style.minHeight = 'var(--vote-btn-size-desktop)';
                    
                    // Style icon inside
                    const icon = el.querySelector('i');
                    if (icon) {
                        icon.style.fontSize = 'var(--vote-icon-size-desktop)';
                    }
                }
            }
        });
        
        // Style vote count
        document.querySelectorAll('.vote-count').forEach(el => {
            if (!el.classList.contains('adaptive-vote-count')) {
                el.classList.add('adaptive-vote-count');
                el.style.textAlign = 'center';
                el.style.fontWeight = '600';
                el.style.transition = 'all 0.2s ease-in-out';
                
                // Size based on device width
                const windowWidth = window.innerWidth;
                if (windowWidth < 576) {
                    el.style.fontSize = 'calc(var(--font-size-xs) * 1.1)';
                    el.style.margin = '0.1rem 0';
                } else if (windowWidth >= 576 && windowWidth < 992) {
                    el.style.fontSize = 'var(--font-size-sm)';
                    el.style.margin = '0.15rem 0';
                } else {
                    el.style.fontSize = 'var(--font-size-md)';
                    el.style.margin = '0.2rem 0';
                    el.style.fontWeight = '700';
                }
            }
        });
        
        // Style avatars
        document.querySelectorAll('.avatar, .profile-avatar, .comment-avatar, img.rounded-circle:not(.nav-avatar)').forEach(el => {
            if (!el.classList.contains('adaptive-avatar')) {
                el.classList.add('adaptive-avatar');
                el.style.transition = 'all 0.2s ease-in-out';
                
                // Size based on device width
                const windowWidth = window.innerWidth;
                if (windowWidth < 576) {
                    if (el.classList.contains('profile-avatar')) {
                        el.style.width = '80px';
                        el.style.height = '80px';
                    } else if (el.classList.contains('comment-avatar')) {
                        el.style.width = '24px';
                        el.style.height = '24px';
                    } else {
                        el.style.width = '32px';
                        el.style.height = '32px';
                    }
                } else if (windowWidth >= 576 && windowWidth < 992) {
                    if (el.classList.contains('profile-avatar')) {
                        el.style.width = '100px';
                        el.style.height = '100px';
                    } else if (el.classList.contains('comment-avatar')) {
                        el.style.width = '28px';
                        el.style.height = '28px';
                    } else {
                        el.style.width = '36px';
                        el.style.height = '36px';
                    }
                } else {
                    if (el.classList.contains('profile-avatar')) {
                        el.style.width = '120px';
                        el.style.height = '120px';
                    } else if (el.classList.contains('comment-avatar')) {
                        el.style.width = '32px';
                        el.style.height = '32px';
                    } else {
                        el.style.width = '40px';
                        el.style.height = '40px';
                    }
                }
                
                // Common styles
                el.style.objectFit = 'cover';
            }
        });
        
        // Style country flags
        document.querySelectorAll('.country-flag').forEach(el => {
            if (!el.classList.contains('adaptive-flag')) {
                el.classList.add('adaptive-flag');
                el.style.verticalAlign = 'middle';
                el.style.transition = 'all 0.2s ease-in-out';
                
                // Size based on device width
                const windowWidth = window.innerWidth;
                if (windowWidth < 576) {
                    el.style.width = 'var(--flag-width-mobile)';
                    el.style.height = 'var(--flag-height-mobile)';
                    el.style.margin = '0 0.15rem';
                } else if (windowWidth >= 576 && windowWidth < 992) {
                    el.style.width = 'var(--flag-width-tablet)';
                    el.style.height = 'var(--flag-height-tablet)';
                    el.style.margin = '0 0.2rem';
                } else {
                    el.style.width = 'var(--flag-width-desktop)';
                    el.style.height = 'var(--flag-height-desktop)';
                    el.style.margin = '0 0.25rem';
                }
            }
        });
        
        // Style tags and badges
        document.querySelectorAll('.badge, .tag, .post-tags .badge, .tag-list .tag, .tag-item').forEach(el => {
            if (!el.classList.contains('adaptive-tag')) {
                el.classList.add('adaptive-tag');
                el.style.display = 'inline-flex';
                el.style.alignItems = 'center';
                el.style.transition = 'all 0.2s ease-in-out';
                
                // Size based on device width
                const windowWidth = window.innerWidth;
                if (windowWidth < 576) {
                    el.style.fontSize = 'var(--tag-font-size-xs)';
                    el.style.padding = 'var(--tag-padding-xs)';
                    el.style.margin = '0.1rem';
                    
                    // Style icon inside
                    const icon = el.querySelector('i');
                    if (icon) {
                        icon.style.fontSize = 'calc(var(--tag-font-size-xs) * 1.1)';
                        icon.style.marginRight = '0.15rem';
                    }
                } else if (windowWidth >= 576 && windowWidth < 992) {
                    el.style.fontSize = 'var(--tag-font-size-sm)';
                    el.style.padding = 'var(--tag-padding-sm)';
                    el.style.margin = '0.15rem';
                    
                    // Style icon inside
                    const icon = el.querySelector('i');
                    if (icon) {
                        icon.style.fontSize = 'calc(var(--tag-font-size-sm) * 1.1)';
                        icon.style.marginRight = '0.2rem';
                    }
                } else {
                    el.style.fontSize = 'var(--tag-font-size-md)';
                    el.style.padding = 'var(--tag-padding-md)';
                    el.style.margin = '0.2rem';
                    
                    // Style icon inside
                    const icon = el.querySelector('i');
                    if (icon) {
                        icon.style.fontSize = 'calc(var(--tag-font-size-md) * 1.1)';
                        icon.style.marginRight = '0.25rem';
                    }
                }
            }
        });
        
        // Add adaptive classes to action buttons (comment, share, delete)
        document.querySelectorAll('.btn-sm, .action-btn, .comment-btn, .share-btn, .delete-btn, .reply-btn, a[title="Share"], a[title="Delete"], a[title="Reply"], button[aria-label="Share"], button[aria-label="Delete"], button[aria-label="Reply"], a.btn-outline-primary, a.btn-outline-secondary, a.btn-outline-danger').forEach(el => {
            if (!el.classList.contains('adaptive-action-btn')) {
                el.classList.add('adaptive-action-btn');
                
                // Get device size to adapt button styling
                const windowWidth = window.innerWidth;
                
                if (windowWidth < 576) {
                    // Mobile styling
                    el.style.fontSize = 'var(--font-size-xs)';
                    el.style.padding = 'var(--btn-padding-xs)';
                    el.style.minHeight = '28px';
                    el.style.lineHeight = '1.2';
                    el.style.margin = '0.1rem';
                    
                    // Find icon inside button if exists
                    const icon = el.querySelector('i');
                    if (icon) {
                        icon.style.fontSize = 'calc(var(--font-size-xs) * 1.2)';
                        icon.style.marginRight = '0.2rem';
                    }
                } else if (windowWidth >= 576 && windowWidth < 992) {
                    // Tablet styling
                    el.style.fontSize = 'calc(var(--font-size-sm) * 0.95)';
                    el.style.padding = 'var(--btn-padding-sm)';
                    el.style.minHeight = '32px';
                    el.style.margin = '0.15rem';
                    
                    // Find icon inside button if exists
                    const icon = el.querySelector('i');
                    if (icon) {
                        icon.style.fontSize = 'calc(var(--font-size-sm) * 1.1)';
                        icon.style.marginRight = '0.25rem';
                    }
                } else {
                    // Desktop styling
                    el.style.fontSize = 'var(--font-size-sm)';
                    el.style.padding = 'var(--btn-padding-md)';
                    el.style.minHeight = '36px';
                    el.style.margin = '0.2rem';
                    
                    // Find icon inside button if exists
                    const icon = el.querySelector('i');
                    if (icon) {
                        icon.style.fontSize = 'calc(var(--font-size-sm) * 1.1)';
                        icon.style.marginRight = '0.3rem';
                    }
                }
                
                // Apply common styles for all sizes
                el.style.display = 'inline-flex';
                el.style.alignItems = 'center';
                el.style.justifyContent = 'center';
                el.style.transition = 'all 0.2s ease-in-out';
            }
        });
        
        // Make images responsive
        document.querySelectorAll('img:not(.avatar):not(.nav-avatar):not(.country-flag), .content-image, .post-image').forEach(el => {
            if (!el.classList.contains('adaptive-image')) {
                el.classList.add('adaptive-image');
                el.style.maxWidth = '100%';
                el.style.height = 'auto';
                el.style.transition = 'all 0.2s ease-in-out';
                
                // Size based on device width for max-height
                const windowWidth = window.innerWidth;
                if (windowWidth < 576) {
                    el.style.maxHeight = '200px';
                } else if (windowWidth >= 576 && windowWidth < 992) {
                    el.style.maxHeight = '300px';
                } else {
                    el.style.maxHeight = '400px';
                }
            }
        });
    }
    
    /**
     * Special function to adapt header icons for the navbar
     */
    function adaptHeaderIcons() {
        // Get the navbar and its width
        const navbar = document.querySelector('.navbar');
        if (!navbar) return;
        
        const navbarWidth = navbar.offsetWidth;
        const headerIcons = navbar.querySelectorAll('.adaptive-icon');
        
        // Scale the icons based on navbar width with more precise breakpoints
        let iconSize;
        if (navbarWidth < 320) {
            // Extremely small devices
            iconSize = '0.9rem';
        } else if (navbarWidth < 360) {
            // Extra small mobile devices
            iconSize = '1rem';
        } else if (navbarWidth < 400) {
            // Small mobile devices
            iconSize = '1rem';
        } else if (navbarWidth < 576) {
            // Medium mobile devices
            iconSize = '1rem';
        } else if (navbarWidth < 768) {
            // Large mobile devices
            iconSize = '1rem';
        } else if (navbarWidth < 992) {
            // Tablets
            iconSize = '1.1rem';
        } else if (navbarWidth < 1200) {
            // Small desktops
            iconSize = '1.1rem';
        } else {
            // Large desktops
            iconSize = '1.2rem';
        }
        
        // Apply the calculated size
        headerIcons.forEach(function(icon) {
            icon.style.fontSize = iconSize;
        });
    }
    
    /**
     * Sets the --adaptive-scale CSS variable based on screen size
     * This is used by the universal-adaptive.css file to scale all elements
     */
    function setAdaptiveScale() {
        const windowWidth = window.innerWidth;
        let adaptiveScale = 1; // Default scale
        
        // Set different scales based on breakpoints
        if (windowWidth < 360) {
            // Extra small mobile phones
            adaptiveScale = 0.8;
        } else if (windowWidth < 576) {
            // Mobile phones
            adaptiveScale = 0.85;
        } else if (windowWidth < 768) {
            // Large mobile phones / small tablets
            adaptiveScale = 0.9;
        } else if (windowWidth < 992) {
            // Tablets
            adaptiveScale = 0.92; 
        } else if (windowWidth < 1400) {
            // Desktops
            adaptiveScale = 1;
        } else {
            // Large desktops
            adaptiveScale = 1.1;
        }
        
        // Set the CSS variable
        document.documentElement.style.setProperty('--adaptive-scale', adaptiveScale);
        console.log("Setting adaptive scale to:", adaptiveScale);
    }
    
    // Call setAdaptiveScale on page load
    setAdaptiveScale();
    
    // Update adaptive scale on window resize
    window.addEventListener('resize', function() {
        setAdaptiveScale();
    });
});