// ===== WORLD TOUR - MAIN JAVASCRIPT =====
// Modern, responsive, and feature-rich travel website functionality

document.addEventListener('DOMContentLoaded', function() {
    // ===== MOBILE NAVIGATION =====
    const navToggle = document.getElementById('navToggle');
    const navMenu = document.getElementById('navMenu');
    
    if (navToggle && navMenu) {
        navToggle.addEventListener('click', function() {
            navMenu.classList.toggle('active');
            navToggle.classList.toggle('active');
            
            // Update toggle icon
            const icon = navToggle.querySelector('i');
            if (icon) {
                icon.classList.toggle('fa-bars');
                icon.classList.toggle('fa-times');
            }
        });
        
        // Close mobile menu when clicking on a link
        const navLinks = navMenu.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', function() {
                navMenu.classList.remove('active');
                navToggle.classList.remove('active');
                
                const icon = navToggle.querySelector('i');
                if (icon) {
                    icon.classList.remove('fa-times');
                    icon.classList.add('fa-bars');
                }
            });
        });
        
        // Close mobile menu when clicking outside
        document.addEventListener('click', function(event) {
            if (!navToggle.contains(event.target) && !navMenu.contains(event.target)) {
                navMenu.classList.remove('active');
                navToggle.classList.remove('active');
                
                const icon = navToggle.querySelector('i');
                if (icon) {
                    icon.classList.remove('fa-times');
                    icon.classList.add('fa-bars');
                }
            }
        });
    }

    // ===== SCROLL EFFECTS =====
    const header = document.querySelector('.header');
    
    window.addEventListener('scroll', function() {
        if (window.scrollY > 100) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }
    });

    // ===== SEARCH FUNCTIONALITY =====
    const searchForm = document.querySelector('.search-form');
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            const searchInput = searchForm.querySelector('input[name="search"]');
            if (searchInput && searchInput.value.trim() === '') {
                e.preventDefault();
                searchInput.focus();
                showNotification('Please enter a destination to search', 'warning');
            }
        });
    }

    // ===== DESTINATION CARDS =====
    const destinationCards = document.querySelectorAll('.destination-card');
    destinationCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-10px)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });

    // ===== LAZY LOADING =====
    const images = document.querySelectorAll('img[data-src]');
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

    // ===== SMOOTH SCROLLING =====
    const smoothScrollLinks = document.querySelectorAll('a[href^="#"]');
    smoothScrollLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);
            
            if (targetElement) {
                const headerHeight = document.querySelector('.header').offsetHeight;
                const targetPosition = targetElement.offsetTop - headerHeight;
                
                window.scrollTo({
                    top: targetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });

    // ===== FORM VALIDATION =====
    const forms = document.querySelectorAll('form[data-validate]');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateForm(this)) {
                e.preventDefault();
            }
        });
    });

    // ===== NOTIFICATION SYSTEM =====
    window.showNotification = function(message, type = 'info', duration = 5000) {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas fa-${getNotificationIcon(type)}"></i>
                <span>${message}</span>
                <button class="notification-close" onclick="this.parentElement.parentElement.remove()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Auto remove after duration
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, duration);
    };

    // ===== LOADING STATES =====
    window.showLoading = function(element) {
        if (element) {
            element.classList.add('loading');
            element.disabled = true;
        }
    };

    window.hideLoading = function(element) {
        if (element) {
            element.classList.remove('loading');
            element.disabled = false;
        }
    };

    // ===== PRICE FORMATTING =====
    window.formatPrice = function(amount, currency = 'USD') {
        const formatter = new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: currency
        });
        return formatter.format(amount);
    };

    // ===== DATE FORMATTING =====
    window.formatDate = function(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    };

    // ===== AJAX REQUESTS =====
    window.makeRequest = async function(url, options = {}) {
        const defaultOptions = {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
        };

        const finalOptions = { ...defaultOptions, ...options };
        
        try {
            const response = await fetch(url, finalOptions);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                return await response.json();
            } else {
                return await response.text();
            }
        } catch (error) {
            console.error('Request failed:', error);
            throw error;
        }
    };

    // ===== WISHLIST FUNCTIONALITY =====
    const wishlistButtons = document.querySelectorAll('.wishlist-btn');
    wishlistButtons.forEach(button => {
        button.addEventListener('click', async function(e) {
            e.preventDefault();
            
            const destinationId = this.dataset.destinationId;
            const isInWishlist = this.classList.contains('in-wishlist');
            
            try {
                showLoading(this);
                
                const response = await makeRequest(`/wishlist/${isInWishlist ? 'remove' : 'add'}/${destinationId}`, {
                    method: 'POST'
                });
                
                if (response.success) {
                    this.classList.toggle('in-wishlist');
                    const icon = this.querySelector('i');
                    if (icon) {
                        icon.classList.toggle('fas');
                        icon.classList.toggle('far');
                    }
                    
                    showNotification(
                        isInWishlist ? 'Removed from wishlist' : 'Added to wishlist',
                        'success'
                    );
                }
            } catch (error) {
                showNotification('Failed to update wishlist', 'error');
            } finally {
                hideLoading(this);
            }
        });
    });

    // ===== REVIEW SYSTEM =====
    const reviewForms = document.querySelectorAll('.review-form');
    reviewForms.forEach(form => {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const submitBtn = this.querySelector('button[type="submit"]');
            const formData = new FormData(this);
            
            try {
                showLoading(submitBtn);
                
                const response = await makeRequest(this.action, {
                    method: 'POST',
                    body: formData
                });
                
                if (response.success) {
                    showNotification('Review submitted successfully', 'success');
                    this.reset();
                    // Optionally reload the page or update the reviews section
                    location.reload();
                }
            } catch (error) {
                showNotification('Failed to submit review', 'error');
            } finally {
                hideLoading(submitBtn);
            }
        });
    });

    // ===== NEWSLETTER SUBSCRIPTION =====
    const newsletterForm = document.querySelector('.newsletter-form');
    if (newsletterForm) {
        newsletterForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const email = this.querySelector('input[name="email"]').value;
            const submitBtn = this.querySelector('button[type="submit"]');
            
            if (!isValidEmail(email)) {
                showNotification('Please enter a valid email address', 'warning');
                return;
            }
            
            try {
                showLoading(submitBtn);
                
                const response = await makeRequest('/newsletter/subscribe', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ email: email })
                });
                
                if (response.success) {
                    showNotification('Successfully subscribed to newsletter', 'success');
                    this.reset();
                }
            } catch (error) {
                showNotification('Failed to subscribe to newsletter', 'error');
            } finally {
                hideLoading(submitBtn);
            }
        });
    }

    // ===== VOICE SEARCH =====
    const voiceSearchBtn = document.querySelector('.voice-search-btn');
    if (voiceSearchBtn && 'webkitSpeechRecognition' in window) {
        voiceSearchBtn.addEventListener('click', function() {
            const recognition = new webkitSpeechRecognition();
            recognition.continuous = false;
            recognition.interimResults = false;
            recognition.lang = 'en-US';
            
            recognition.onstart = function() {
                voiceSearchBtn.classList.add('listening');
                showNotification('Listening... Speak now', 'info');
            };
            
            recognition.onresult = function(event) {
                const transcript = event.results[0][0].transcript;
                const searchInput = document.querySelector('input[name="search"]');
                if (searchInput) {
                    searchInput.value = transcript;
                    searchInput.focus();
                }
            };
            
            recognition.onend = function() {
                voiceSearchBtn.classList.remove('listening');
            };
            
            recognition.start();
        });
    }

    // ===== ANIMATIONS ON SCROLL =====
    const animatedElements = document.querySelectorAll('.animate-on-scroll');
    const animationObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animated');
            }
        });
    });

    animatedElements.forEach(element => animationObserver.observe(element));

    // ===== UTILITY FUNCTIONS =====
    function getNotificationIcon(type) {
        const icons = {
            success: 'check-circle',
            error: 'exclamation-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        return icons[type] || 'info-circle';
    }

    function validateForm(form) {
        const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
        let isValid = true;
        
        inputs.forEach(input => {
            if (!input.value.trim()) {
                input.classList.add('error');
                isValid = false;
            } else {
                input.classList.remove('error');
            }
        });
        
        return isValid;
    }

    function isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    // ===== PERFORMANCE OPTIMIZATION =====
    // Debounce function for search inputs
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    // Debounced search
    const searchInputs = document.querySelectorAll('input[data-search]');
    searchInputs.forEach(input => {
        const debouncedSearch = debounce(async function(searchTerm) {
            if (searchTerm.length < 2) return;
            
            try {
                const response = await makeRequest(`/api/search?q=${encodeURIComponent(searchTerm)}`);
                // Handle search results
                updateSearchResults(response.results);
            } catch (error) {
                console.error('Search failed:', error);
            }
        }, 300);
        
        input.addEventListener('input', function() {
            debouncedSearch(this.value);
        });
    });

    function updateSearchResults(results) {
        const resultsContainer = document.querySelector('.search-results');
        if (!resultsContainer) return;
        
        resultsContainer.innerHTML = results.map(result => `
            <div class="search-result-item">
                <img src="${result.image_url}" alt="${result.name}">
                <div class="search-result-content">
                    <h4>${result.name}</h4>
                    <p>${result.description}</p>
                    <span class="price">${formatPrice(result.price)}</span>
                </div>
            </div>
        `).join('');
    }

    // ===== ACCESSIBILITY =====
    // Keyboard navigation for dropdowns
    const dropdowns = document.querySelectorAll('.dropdown');
    dropdowns.forEach(dropdown => {
        const toggle = dropdown.querySelector('.dropdown-toggle');
        const menu = dropdown.querySelector('.dropdown-menu');
        
        if (toggle && menu) {
            toggle.addEventListener('keydown', function(e) {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    menu.classList.toggle('show');
                }
            });
            
            // Close dropdown when clicking outside
            document.addEventListener('click', function(e) {
                if (!dropdown.contains(e.target)) {
                    menu.classList.remove('show');
                }
            });
        }
    });

    // ===== PROGRESSIVE WEB APP =====
    // Install prompt
    let deferredPrompt;
    window.addEventListener('beforeinstallprompt', (e) => {
        e.preventDefault();
        deferredPrompt = e;
        
        // Show install button if available
        const installBtn = document.querySelector('.install-app-btn');
        if (installBtn) {
            installBtn.style.display = 'block';
            installBtn.addEventListener('click', async () => {
                if (deferredPrompt) {
                    deferredPrompt.prompt();
                    const { outcome } = await deferredPrompt.userChoice;
                    if (outcome === 'accepted') {
                        installBtn.style.display = 'none';
                    }
                    deferredPrompt = null;
                }
            });
        }
    });

    // ===== ANALYTICS =====
    // Track page views
    function trackPageView() {
        if (typeof gtag !== 'undefined') {
            gtag('config', 'GA_MEASUREMENT_ID', {
                page_title: document.title,
                page_location: window.location.href
            });
        }
    }

    // Track events
    window.trackEvent = function(action, category, label, value) {
        if (typeof gtag !== 'undefined') {
            gtag('event', action, {
                event_category: category,
                event_label: label,
                value: value
            });
        }
    };

    // Track page view on load
    trackPageView();

    // ===== ERROR HANDLING =====
    window.addEventListener('error', function(e) {
        console.error('JavaScript error:', e.error);
        // Send error to analytics
        trackEvent('error', 'javascript', e.message, 1);
    });

    // ===== INITIALIZATION COMPLETE =====
    console.log('World Tour JavaScript initialized successfully');
});

// ===== GLOBAL FUNCTIONS =====
// These functions are available globally

// Currency conversion
window.convertCurrency = async function(amount, fromCurrency, toCurrency) {
    try {
        const response = await fetch(`/api/convert-currency?from=${fromCurrency}&to=${toCurrency}&amount=${amount}`);
        const data = await response.json();
        return data.converted_amount;
    } catch (error) {
        console.error('Currency conversion failed:', error);
        return amount; // Return original amount if conversion fails
    }
};

// Weather information
window.getWeather = async function(city) {
    try {
        const response = await fetch(`/api/weather/${encodeURIComponent(city)}`);
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Weather fetch failed:', error);
        return null;
    }
};

// Share functionality
window.shareContent = function(title, text, url) {
    if (navigator.share) {
        navigator.share({
            title: title,
            text: text,
            url: url
        });
    } else {
        // Fallback: copy to clipboard
        navigator.clipboard.writeText(url).then(() => {
            showNotification('Link copied to clipboard', 'success');
        });
    }
};

// Print functionality
window.printPage = function() {
    window.print();
};

// Fullscreen functionality
window.toggleFullscreen = function(element) {
    if (!document.fullscreenElement) {
        element.requestFullscreen();
    } else {
        document.exitFullscreen();
    }
};