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
        document.querySelectorAll('.post-title, h1.article-title, .community-title, .profile-name').forEach(el => {
            if (isMobile) {
                el.style.fontSize = 'var(--font-size-lg)';
                el.style.lineHeight = '1.3';
            } else if (isTablet) {
                el.style.fontSize = 'calc(var(--font-size-lg) * 1.1)';
                el.style.lineHeight = '1.4';
            } else if (isDesktop) {
                el.style.fontSize = 'calc(var(--font-size-lg) * 1.2)';
                el.style.lineHeight = '1.5';
            } else {
                el.style.fontSize = 'calc(var(--font-size-lg) * 1.3)';
                el.style.lineHeight = '1.5';
            }
        });
        
        // Secondary titles
        document.querySelectorAll('h2, .section-title, .post-subtitle').forEach(el => {
            if (isMobile) {
                el.style.fontSize = 'var(--font-size-md)';
            } else if (isTablet) {
                el.style.fontSize = 'calc(var(--font-size-md) * 1.1)';
            } else {
                el.style.fontSize = 'calc(var(--font-size-md) * 1.2)';
            }
        });
        
        // Meta information and small text
        document.querySelectorAll('.meta-info, .post-meta, .card-subtitle, .text-muted, small').forEach(el => {
            if (isMobile) {
                el.style.fontSize = 'var(--font-size-xs)';
            } else if (isTablet) {
                el.style.fontSize = 'var(--font-size-sm)';
            } else {
                el.style.fontSize = 'calc(var(--font-size-sm) * 1.05)';
            }
        });
        
        // Body text and general content
        document.querySelectorAll('.post-content, .comment-content, .card-text, p:not(.meta-info):not(.card-subtitle)').forEach(el => {
            if (isMobile) {
                el.style.fontSize = 'var(--font-size-sm)';
                el.style.lineHeight = '1.4';
            } else if (isTablet) {
                el.style.fontSize = 'var(--font-size-md)';
                el.style.lineHeight = '1.5';
            } else {
                el.style.fontSize = 'calc(var(--font-size-md) * 1.05)';
                el.style.lineHeight = '1.6';
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
        
        // Buttons scaling
        document.querySelectorAll('.btn:not(.btn-sm):not(.btn-lg)').forEach(el => {
            if (isMobile) {
                el.style.padding = '0.2rem 0.5rem';
                el.style.fontSize = 'var(--font-size-sm)';
            } else if (isTablet) {
                el.style.padding = '0.3rem 0.6rem';
                el.style.fontSize = 'var(--font-size-sm)';
            } else {
                el.style.padding = '0.375rem 0.75rem';
                el.style.fontSize = 'var(--font-size-md)';
            }
        });
        
        // Small buttons
        document.querySelectorAll('.btn-sm').forEach(el => {
            if (isMobile) {
                el.style.padding = '0.1rem 0.3rem';
                el.style.fontSize = 'var(--font-size-xs)';
            } else {
                el.style.padding = '0.2rem 0.4rem';
                el.style.fontSize = 'var(--font-size-sm)';
            }
        });
        
        // Adjust form controls
        document.querySelectorAll('.form-control, .form-select').forEach(el => {
            if (isMobile) {
                el.style.padding = '0.2rem 0.4rem';
                el.style.fontSize = 'var(--font-size-sm)';
                el.style.minHeight = '32px';
            } else if (isTablet) {
                el.style.padding = '0.25rem 0.5rem';
                el.style.fontSize = 'var(--font-size-md)';
                el.style.minHeight = '36px';
            } else {
                el.style.padding = '0.3rem 0.6rem';
                el.style.fontSize = 'var(--font-size-md)';
                el.style.minHeight = '38px';
            }
        });
        
        // Image sizing
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
        
        // Lists and content spacing
        document.querySelectorAll('.list-group, .post-item, .comment-item').forEach(el => {
            if (isMobile) {
                el.style.marginBottom = 'var(--spacing-xs)';
            } else if (isTablet) {
                el.style.marginBottom = 'var(--spacing-sm)';
            } else {
                el.style.marginBottom = 'var(--spacing-md)';
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
            } else {
                profileHeader.style.flexDirection = 'row';
                profileHeader.style.alignItems = 'flex-start';
            }
        }
        
        // Check if we're on community page
        if (document.querySelector('.community-header')) {
            const communityHeader = document.querySelector('.community-header');
            if (windowWidth < 576) {
                communityHeader.style.padding = 'var(--spacing-sm)';
            } else {
                communityHeader.style.padding = 'var(--spacing-lg)';
            }
        }
        
        // Post detail layout
        if (document.querySelector('.post-detail')) {
            if (windowWidth < 576) {
                // Simplify layout on mobile
                document.querySelectorAll('.post-sidebar').forEach(el => {
                    el.style.display = 'none';
                });
            } else {
                document.querySelectorAll('.post-sidebar').forEach(el => {
                    el.style.display = 'block';
                });
            }
        }
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
        
        // Identify containers that should have adaptive spacing
        document.querySelectorAll('.card, .list-group-item, .nav-item, .dropdown-item').forEach(el => {
            if (!el.classList.contains('adaptive-spacing')) {
                el.classList.add('adaptive-spacing');
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
});