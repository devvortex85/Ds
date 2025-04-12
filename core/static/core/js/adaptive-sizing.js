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
        
        // Apply special adaptive sizing for header navigation icons
        adaptHeaderIcons();
    }
    
    // Function to adapt header icons based on available space
    function adaptHeaderIcons() {
        // Get the navbar and its width
        const navbar = document.querySelector('.navbar');
        if (!navbar) return;
        
        const navbarWidth = navbar.offsetWidth;
        const headerIcons = navbar.querySelectorAll('.adaptive-icon');
        
        // Scale the icons based on navbar width
        let iconSize;
        if (navbarWidth < 360) {
            // Extra small mobile devices
            iconSize = '0.8rem';
        } else if (navbarWidth < 576) {
            // Small mobile devices
            iconSize = '0.85rem';
        } else if (navbarWidth < 768) {
            // Medium mobile devices
            iconSize = '0.9rem';
        } else if (navbarWidth < 992) {
            // Tablets
            iconSize = '1rem';
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