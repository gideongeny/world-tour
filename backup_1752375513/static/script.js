// Mobile Navigation Toggle
document.addEventListener('DOMContentLoaded', function() {
    const navToggle = document.getElementById('nav-toggle');
    const navbarNav = document.getElementById('navbarNav');
    
    if (navToggle && navbarNav) {
        // Disable Bootstrap dropdowns on mobile
        const isMobile = () => window.innerWidth <= 768;
        
        // Function to disable Bootstrap dropdowns
        function disableBootstrapDropdowns() {
            if (isMobile()) {
                const dropdownToggles = document.querySelectorAll('.dropdown-toggle');
                dropdownToggles.forEach(toggle => {
                    // Remove Bootstrap's data attributes
                    toggle.removeAttribute('data-bs-toggle');
                    toggle.removeAttribute('aria-expanded');
                    toggle.removeAttribute('data-bs-auto-close');
                });
            }
        }
        
        // Function to enable Bootstrap dropdowns on desktop
        function enableBootstrapDropdowns() {
            if (!isMobile()) {
                const dropdownToggles = document.querySelectorAll('.dropdown-toggle');
                dropdownToggles.forEach(toggle => {
                    // Restore Bootstrap's data attributes
                    toggle.setAttribute('data-bs-toggle', 'dropdown');
                    toggle.setAttribute('aria-expanded', 'false');
                    toggle.setAttribute('data-bs-auto-close', 'true');
                });
            }
        }
        
        // Custom mobile navigation toggle
        navToggle.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            // Toggle active class
            navToggle.classList.toggle('active');
            navbarNav.classList.toggle('active');
            
            // Prevent body scroll when menu is open
            if (navbarNav.classList.contains('active')) {
                document.body.style.overflow = 'hidden';
            } else {
                document.body.style.overflow = '';
            }
        });
        
        // Handle dropdown toggles on mobile
        const dropdownToggles = document.querySelectorAll('.dropdown-toggle');
        dropdownToggles.forEach(toggle => {
            toggle.addEventListener('click', function(e) {
                if (isMobile()) {
                    e.preventDefault();
                    e.stopPropagation();
                    
                    const dropdownMenu = this.nextElementSibling;
                    if (dropdownMenu && dropdownMenu.classList.contains('dropdown-menu')) {
                        dropdownMenu.classList.toggle('show');
                        this.classList.toggle('show');
                    }
                }
            });
        });
        
        // Close mobile menu when clicking outside
        document.addEventListener('click', function(e) {
            if (isMobile() && navbarNav.classList.contains('active')) {
                if (!navbarNav.contains(e.target) && !navToggle.contains(e.target)) {
                    navToggle.classList.remove('active');
                    navbarNav.classList.remove('active');
                    document.body.style.overflow = '';
                }
            }
        });
        
        // Handle window resize
        window.addEventListener('resize', function() {
            if (!isMobile()) {
                navToggle.classList.remove('active');
                navbarNav.classList.remove('active');
                document.body.style.overflow = '';
                enableBootstrapDropdowns();
            } else {
                disableBootstrapDropdowns();
            }
        });
        
        // Initialize on load
        if (isMobile()) {
            disableBootstrapDropdowns();
        }
    }
    
    // Fix mobile layout issues
    function fixMobileLayout() {
        const isMobile = window.innerWidth <= 768;
        
        if (isMobile) {
            // Prevent horizontal scroll
            document.body.style.overflowX = 'hidden';
            document.documentElement.style.overflowX = 'hidden';
            
            // Fix container widths
            const containers = document.querySelectorAll('.container, .row, .col');
            containers.forEach(container => {
                container.style.maxWidth = '100%';
                container.style.overflowX = 'hidden';
            });
            
            // Fix button overflow
            const buttons = document.querySelectorAll('.btn');
            buttons.forEach(btn => {
                btn.style.maxWidth = '100%';
                btn.style.overflow = 'hidden';
                btn.style.textOverflow = 'ellipsis';
                btn.style.whiteSpace = 'nowrap';
            });
            
            // Fix form elements
            const formElements = document.querySelectorAll('input, select, textarea');
            formElements.forEach(element => {
                element.style.maxWidth = '100%';
                element.style.boxSizing = 'border-box';
            });
            
            // Fix images
            const images = document.querySelectorAll('img');
            images.forEach(img => {
                img.style.maxWidth = '100%';
                img.style.height = 'auto';
            });
        }
    }
    
    // Run on load and resize
    fixMobileLayout();
    window.addEventListener('resize', fixMobileLayout);
    
    // Fix zoom issues on iOS
    function preventZoom() {
        const isMobile = window.innerWidth <= 768;
        if (isMobile) {
            const inputs = document.querySelectorAll('input, select, textarea');
            inputs.forEach(input => {
                if (input.type !== 'file') {
                    input.style.fontSize = '16px';
                }
            });
        }
    }
    
    preventZoom();
    window.addEventListener('resize', preventZoom);
});

// Smooth scrolling for anchor links
document.addEventListener('DOMContentLoaded', function() {
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    
    anchorLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            
            if (href !== '#') {
                const target = document.querySelector(href);
                if (target) {
                    e.preventDefault();
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    });
});

// Form validation and enhancement
document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        // Add real-time validation
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                validateField(this);
            });
            
            input.addEventListener('input', function() {
                if (this.classList.contains('error')) {
                    validateField(this);
                }
            });
        });
        
        // Form submission
        form.addEventListener('submit', function(e) {
            let isValid = true;
            const inputs = this.querySelectorAll('input[required], select[required], textarea[required]');
            
            inputs.forEach(input => {
                if (!validateField(input)) {
                    isValid = false;
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                showMessage('Please fill in all required fields correctly.', 'error');
            }
        });
    });
    
    function validateField(field) {
        const value = field.value.trim();
        const type = field.type;
        const required = field.hasAttribute('required');
        
        // Remove existing error styling
        field.classList.remove('error');
        const errorMsg = field.parentNode.querySelector('.error-message');
        if (errorMsg) {
            errorMsg.remove();
        }
        
        // Check if required field is empty
        if (required && !value) {
            showFieldError(field, 'This field is required.');
            return false;
        }
        
        // Email validation
        if (type === 'email' && value) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(value)) {
                showFieldError(field, 'Please enter a valid email address.');
                return false;
            }
        }
        
        // Phone validation
        if (type === 'tel' && value) {
            const phoneRegex = /^[\+]?[1-9][\d]{0,15}$/;
            if (!phoneRegex.test(value.replace(/\s/g, ''))) {
                showFieldError(field, 'Please enter a valid phone number.');
                return false;
            }
        }
        
        // Password validation
        if (type === 'password' && value) {
            if (value.length < 6) {
                showFieldError(field, 'Password must be at least 6 characters long.');
                return false;
            }
        }
        
        return true;
    }
    
    function showFieldError(field, message) {
        field.classList.add('error');
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.textContent = message;
        errorDiv.style.color = '#dc3545';
        errorDiv.style.fontSize = '0.875rem';
        errorDiv.style.marginTop = '0.25rem';
        field.parentNode.appendChild(errorDiv);
    }
});

// Message display system
function showMessage(message, type = 'info') {
    const messageDiv = document.createElement('div');
    messageDiv.className = `alert alert-${type} alert-dismissible fade show`;
    messageDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Insert at the top of the main content
    const mainContent = document.querySelector('main') || document.querySelector('.container');
    if (mainContent) {
        mainContent.insertBefore(messageDiv, mainContent.firstChild);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (messageDiv.parentNode) {
                messageDiv.remove();
            }
        }, 5000);
    }
}

// Lazy loading for images
document.addEventListener('DOMContentLoaded', function() {
    const images = document.querySelectorAll('img[data-src]');
    
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            });
        });
        
        images.forEach(img => imageObserver.observe(img));
    } else {
        // Fallback for older browsers
        images.forEach(img => {
            img.src = img.dataset.src;
            img.classList.remove('lazy');
        });
    }
});

// Search functionality enhancement
document.addEventListener('DOMContentLoaded', function() {
    const searchInputs = document.querySelectorAll('.search-input, input[type="search"]');
    
    searchInputs.forEach(input => {
        let searchTimeout;
        
        input.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            const query = this.value.trim();
            
            if (query.length >= 2) {
                searchTimeout = setTimeout(() => {
                    performSearch(query);
                }, 300);
            }
        });
    });
    
    function performSearch(query) {
        // Add search functionality here
        console.log('Searching for:', query);
    }
});

// Price range slider functionality
document.addEventListener('DOMContentLoaded', function() {
    const priceSliders = document.querySelectorAll('.price-range input[type="range"]');
    
    priceSliders.forEach(slider => {
        const output = slider.nextElementSibling;
        if (output) {
            slider.addEventListener('input', function() {
                output.textContent = this.value;
            });
        }
    });
});

// Booking form enhancement
document.addEventListener('DOMContentLoaded', function() {
    const bookingForms = document.querySelectorAll('.booking-form');
    
    bookingForms.forEach(form => {
        const dateInputs = form.querySelectorAll('input[type="date"]');
        const today = new Date().toISOString().split('T')[0];
        
        dateInputs.forEach(input => {
            // Set minimum date to today
            input.setAttribute('min', today);
            
            // Set default departure date to tomorrow
            if (input.name === 'departure_date') {
                const tomorrow = new Date();
                tomorrow.setDate(tomorrow.getDate() + 1);
                input.value = tomorrow.toISOString().split('T')[0];
            }
        });
        
        // Passenger count validation
        const passengerInputs = form.querySelectorAll('input[name*="passenger"], select[name*="passenger"]');
        passengerInputs.forEach(input => {
            input.addEventListener('change', function() {
                const total = Array.from(passengerInputs).reduce((sum, inp) => {
                    return sum + (parseInt(inp.value) || 0);
                }, 0);
                
                if (total > 10) {
                    showMessage('Maximum 10 passengers allowed per booking.', 'warning');
                }
            });
        });
    });
});

// Weather widget functionality
document.addEventListener('DOMContentLoaded', function() {
    const weatherCards = document.querySelectorAll('.weather-card');
    
    weatherCards.forEach(card => {
        const location = card.dataset.location;
        if (location) {
            // Add weather API integration here
            updateWeather(card, location);
        }
    });
    
    function updateWeather(card, location) {
        // Placeholder for weather API integration
        console.log('Updating weather for:', location);
    }
});

// Review system enhancement
document.addEventListener('DOMContentLoaded', function() {
    const starRatings = document.querySelectorAll('.star-rating');
    
    starRatings.forEach(rating => {
        const stars = rating.querySelectorAll('input');
        const labels = rating.querySelectorAll('label');
        
        stars.forEach((star, index) => {
            star.addEventListener('change', function() {
                const value = this.value;
                
                // Update visual stars
                labels.forEach((label, labelIndex) => {
                    if (labelIndex < value) {
                        label.style.color = '#ffd700';
                    } else {
                        label.style.color = '#ddd';
                    }
                });
            });
        });
    });
});

// Social sharing functionality
document.addEventListener('DOMContentLoaded', function() {
    const shareButtons = document.querySelectorAll('.social-share .social-btn');
    
    shareButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const platform = this.classList[1]; // facebook, twitter, etc.
            const url = encodeURIComponent(window.location.href);
            const title = encodeURIComponent(document.title);
            
            let shareUrl;
            
            switch (platform) {
                case 'facebook':
                    shareUrl = `https://www.facebook.com/sharer/sharer.php?u=${url}`;
                    break;
                case 'twitter':
                    shareUrl = `https://twitter.com/intent/tweet?url=${url}&text=${title}`;
                    break;
                case 'linkedin':
                    shareUrl = `https://www.linkedin.com/sharing/share-offsite/?url=${url}`;
                    break;
                case 'email':
                    shareUrl = `mailto:?subject=${title}&body=Check out this page: ${url}`;
                    break;
            }
            
            if (shareUrl) {
                window.open(shareUrl, '_blank', 'width=600,height=400');
            }
        });
    });
});

// Newsletter subscription
document.addEventListener('DOMContentLoaded', function() {
    const newsletterForm = document.querySelector('.newsletter-form');
    
    if (newsletterForm) {
        newsletterForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const email = this.querySelector('input[type="email"]').value;
            
            if (email) {
                // Add newsletter subscription logic here
                showMessage('Thank you for subscribing to our newsletter!', 'success');
                this.reset();
            }
        });
    }
});

// Accessibility improvements
document.addEventListener('DOMContentLoaded', function() {
    // Add skip to main content link
    const skipLink = document.createElement('a');
    skipLink.href = '#main-content';
    skipLink.textContent = 'Skip to main content';
    skipLink.className = 'skip-link';
    skipLink.style.cssText = `
        position: absolute;
        top: -40px;
        left: 6px;
        background: #667eea;
        color: white;
        padding: 8px;
        text-decoration: none;
        border-radius: 4px;
        z-index: 1001;
    `;
    
    document.body.insertBefore(skipLink, document.body.firstChild);
    
    // Focus management for mobile menu
    const navToggle = document.getElementById('nav-toggle');
    const navbarNav = document.getElementById('navbarNav');
    
    if (navToggle && navbarNav) {
        navToggle.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                this.click();
            }
        });
        
        // Trap focus in mobile menu
        navbarNav.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                navToggle.click();
                navToggle.focus();
            }
        });
    }
});

// Performance optimizations
document.addEventListener('DOMContentLoaded', function() {
    // Preload critical resources
    const criticalImages = [
        '/static/modern.jpg',
        '/static/luxury.jpg',
        '/static/minimalist.jpg'
    ];
    
    criticalImages.forEach(src => {
        const link = document.createElement('link');
        link.rel = 'preload';
        link.as = 'image';
        link.href = src;
        document.head.appendChild(link);
    });
    
    // Defer non-critical JavaScript
    const deferredScripts = document.querySelectorAll('script[data-defer]');
    deferredScripts.forEach(script => {
        setTimeout(() => {
            const newScript = document.createElement('script');
            newScript.src = script.src;
            document.head.appendChild(newScript);
        }, 2000);
    });
});