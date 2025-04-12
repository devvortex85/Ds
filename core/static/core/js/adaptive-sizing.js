/**
 * Adaptive Sizing Script
 * This script provides dynamic adaptation of UI elements based on screen size
 * It complements the CSS media queries with JavaScript-based adaptations
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initial call
    applyResponsiveLayout();
    
    // Listen for window resize events
    window.addEventListener('resize', function() {
        applyResponsiveLayout();
    });
    
    // Apply layout changes based on screen width
    function applyResponsiveLayout() {
        const windowWidth = window.innerWidth;
        const isMobile = windowWidth < 576;
        const isTablet = windowWidth >= 576 && windowWidth < 992;
        
        console.log("Applying responsive layout: Mobile: " + isMobile + ", Tablet: " + isTablet);
        
        // Apply additional dynamic styling that can't be done with CSS alone
        if (isMobile) {
            // On mobile devices, make specific adjustments
            document.querySelectorAll('.post-title').forEach(function(element) {
                element.style.fontSize = '1rem';
            });
            
            // Simplify UI on mobile
            document.querySelectorAll('.meta-info').forEach(function(element) {
                element.style.fontSize = '0.75rem';
            });
            
            // Reduce image sizes
            document.querySelectorAll('img:not(.avatar):not(.nav-avatar)').forEach(function(element) {
                element.style.maxHeight = '200px';
            });
        } else if (isTablet) {
            // On tablet devices
            document.querySelectorAll('.post-title').forEach(function(element) {
                element.style.fontSize = '1.1rem';
            });
            
            document.querySelectorAll('.meta-info').forEach(function(element) {
                element.style.fontSize = '0.8rem';
            });
            
            // Moderate image sizes
            document.querySelectorAll('img:not(.avatar):not(.nav-avatar)').forEach(function(element) {
                element.style.maxHeight = '300px';
            });
        } else {
            // On desktop devices
            document.querySelectorAll('.post-title').forEach(function(element) {
                element.style.fontSize = '1.25rem';
            });
            
            document.querySelectorAll('.meta-info').forEach(function(element) {
                element.style.fontSize = '0.85rem';
            });
            
            // Larger image sizes
            document.querySelectorAll('img:not(.avatar):not(.nav-avatar)').forEach(function(element) {
                element.style.maxHeight = '400px';
            });
        }
        
        // Apply adaptive icon sizing based on parent container width
        document.querySelectorAll('.adaptive-icon').forEach(function(icon) {
            const containerWidth = icon.parentElement.offsetWidth;
            
            if (containerWidth < 50) {
                icon.style.fontSize = '0.7rem';
            } else if (containerWidth < 100) {
                icon.style.fontSize = '0.8rem';
            } else if (containerWidth < 200) {
                icon.style.fontSize = '0.9rem';
            } else {
                icon.style.fontSize = '1rem';
            }
        });
    }
});