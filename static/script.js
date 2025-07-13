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
                    
                    // Remove Bootstrap's dropdown classes
                    const dropdownMenu = toggle.nextElementSibling;
                    if (dropdownMenu && dropdownMenu.classList.contains('dropdown-menu')) {
                        dropdownMenu.classList.remove('show');
                    }
                });
            }
        }
        
        // Function to enable Bootstrap dropdowns
        function enableBootstrapDropdowns() {
            if (!isMobile()) {
                const dropdownToggles = document.querySelectorAll('.dropdown-toggle');
                dropdownToggles.forEach(toggle => {
                    // Restore Bootstrap's data attributes
                    toggle.setAttribute('data-bs-toggle', 'dropdown');
                    toggle.setAttribute('aria-expanded', 'false');
                });
            }
        }
        
        // Initial setup
        disableBootstrapDropdowns();
        
        // Toggle mobile menu
        navToggle.addEventListener('click', function() {
            navbarNav.classList.toggle('active');
            navToggle.classList.toggle('active');
        });
        
        // Handle custom dropdown toggles on mobile
        const dropdownToggles = navbarNav.querySelectorAll('.dropdown-toggle');
        dropdownToggles.forEach(toggle => {
            toggle.addEventListener('click', function(e) {
                if (isMobile()) {
                    e.preventDefault();
                    e.stopPropagation();
                    
                    // Close other dropdowns
                    dropdownToggles.forEach(otherToggle => {
                        if (otherToggle !== toggle) {
                            otherToggle.classList.remove('show');
                            const otherMenu = otherToggle.nextElementSibling;
                            if (otherMenu && otherMenu.classList.contains('dropdown-menu')) {
                                otherMenu.classList.remove('show');
                            }
                        }
                    });
                    
                    // Toggle current dropdown
                    toggle.classList.toggle('show');
                    const dropdownMenu = toggle.nextElementSibling;
                    if (dropdownMenu && dropdownMenu.classList.contains('dropdown-menu')) {
                        dropdownMenu.classList.toggle('show');
                    }
                }
            });
        });
        
        // Close mobile menu when clicking on a regular link (not dropdown toggle)
        const navLinks = navbarNav.querySelectorAll('.nav-link:not(.dropdown-toggle)');
        navLinks.forEach(link => {
            link.addEventListener('click', function() {
                navbarNav.classList.remove('active');
                navToggle.classList.remove('active');
            });
        });
        
        // Close mobile menu when clicking on dropdown items
        const dropdownItems = navbarNav.querySelectorAll('.dropdown-item');
        dropdownItems.forEach(item => {
            item.addEventListener('click', function() {
                navbarNav.classList.remove('active');
                navToggle.classList.remove('active');
                
                // Close all dropdowns
                dropdownToggles.forEach(toggle => {
                    toggle.classList.remove('show');
                    const menu = toggle.nextElementSibling;
                    if (menu && menu.classList.contains('dropdown-menu')) {
                        menu.classList.remove('show');
                    }
                });
            });
        });
        
        // Close mobile menu when clicking outside
        document.addEventListener('click', function(event) {
            if (!event.target.closest('.navbar')) {
                navbarNav.classList.remove('active');
                navToggle.classList.remove('active');
                
                // Close all dropdowns
                dropdownToggles.forEach(toggle => {
                    toggle.classList.remove('show');
                    const menu = toggle.nextElementSibling;
                    if (menu && menu.classList.contains('dropdown-menu')) {
                        menu.classList.remove('show');
                    }
                });
            }
        });
        
        // Handle window resize
        window.addEventListener('resize', function() {
            if (window.innerWidth > 768) {
                navbarNav.classList.remove('active');
                navToggle.classList.remove('active');
                enableBootstrapDropdowns();
                
                // Close all custom dropdowns
                dropdownToggles.forEach(toggle => {
                    toggle.classList.remove('show');
                    const menu = toggle.nextElementSibling;
                    if (menu && menu.classList.contains('dropdown-menu')) {
                        menu.classList.remove('show');
                    }
                });
            } else {
                disableBootstrapDropdowns();
            }
        });
    }
});

// Search Functionality
document.addEventListener('DOMContentLoaded', function() {
    const searchForm = document.querySelector('.search-form');
    const searchInput = document.querySelector('.search-form input');
    
    if (searchForm && searchInput) {
        // Real-time search suggestions
        searchInput.addEventListener('input', function() {
            const query = this.value.trim();
            if (query.length > 2) {
                fetchSearchSuggestions(query);
            }
        });
        
        // Form submission
        searchForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const query = searchInput.value.trim();
            if (query) {
                window.location.href = `/travel?search=${encodeURIComponent(query)}`;
            }
        });
    }
});

// Fetch search suggestions
async function fetchSearchSuggestions(query) {
    try {
        const response = await fetch(`/search?query=${encodeURIComponent(query)}`);
        const data = await response.json();
        displaySearchSuggestions(data);
    } catch (error) {
        console.error('Error fetching search suggestions:', error);
    }
}

// Display search suggestions
function displaySearchSuggestions(suggestions) {
    // Remove existing suggestions
    const existingSuggestions = document.querySelector('.search-suggestions');
    if (existingSuggestions) {
        existingSuggestions.remove();
    }
    
    if (suggestions.length === 0) return;
    
    const searchForm = document.querySelector('.search-form');
    const suggestionsContainer = document.createElement('div');
    suggestionsContainer.className = 'search-suggestions';
    
    suggestions.forEach(suggestion => {
        const suggestionItem = document.createElement('div');
        suggestionItem.className = 'suggestion-item';
        suggestionItem.textContent = suggestion.title;
        suggestionItem.addEventListener('click', function() {
            window.location.href = `/travel?search=${encodeURIComponent(suggestion.title)}`;
        });
        suggestionsContainer.appendChild(suggestionItem);
    });
    
    searchForm.appendChild(suggestionsContainer);
}

// Star Rating System
document.addEventListener('DOMContentLoaded', function() {
    const starRatings = document.querySelectorAll('.star-rating');
    
    starRatings.forEach(rating => {
        const stars = rating.querySelectorAll('label');
        
        stars.forEach((star, index) => {
            star.addEventListener('mouseenter', function() {
                highlightStars(stars, index);
            });
            
            star.addEventListener('mouseleave', function() {
                resetStars(stars);
            });
        });
    });
});

function highlightStars(stars, index) {
    stars.forEach((star, i) => {
        if (i <= index) {
            star.style.color = '#ffc107';
        } else {
            star.style.color = '#ddd';
        }
    });
}

function resetStars(stars) {
    const checkedInput = document.querySelector('.star-rating input:checked');
    if (checkedInput) {
        const checkedIndex = Array.from(stars).findIndex(star => 
            star.getAttribute('for') === checkedInput.id
        );
        highlightStars(stars, checkedIndex);
    } else {
        stars.forEach(star => {
            star.style.color = '#ddd';
        });
    }
}

// Smooth Scrolling for Anchor Links
document.addEventListener('DOMContentLoaded', function() {
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    
    anchorLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
});

// Flash Message Auto-hide
document.addEventListener('DOMContentLoaded', function() {
    const flashMessages = document.querySelectorAll('.flash-message');
    
    flashMessages.forEach(message => {
        setTimeout(() => {
            message.style.opacity = '0';
            setTimeout(() => {
                message.remove();
            }, 300);
        }, 5000);
    });
});

// Form Validation
document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    field.style.borderColor = '#dc3545';
                } else {
                    field.style.borderColor = '#ddd';
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                showError('Please fill in all required fields.');
            }
        });
    });
});

// Show Error Message
function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    errorDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #dc3545;
        color: white;
        padding: 1rem;
        border-radius: 5px;
        z-index: 1000;
        animation: slideIn 0.3s ease;
    `;
    
    document.body.appendChild(errorDiv);
    
    setTimeout(() => {
        errorDiv.remove();
    }, 3000);
}

// Lazy Loading for Images
document.addEventListener('DOMContentLoaded', function() {
    const images = document.querySelectorAll('img[data-src]');
    
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.removeAttribute('data-src');
                observer.unobserve(img);
            }
        });
    });
    
    images.forEach(img => imageObserver.observe(img));
});

// Booking Form Price Calculator
document.addEventListener('DOMContentLoaded', function() {
    const bookingForm = document.querySelector('.booking-form');
    
    if (bookingForm) {
        const startDate = document.getElementById('start_date');
        const endDate = document.getElementById('end_date');
        const guests = document.getElementById('guests');
        const daysCount = document.getElementById('days-count');
        const guestsCount = document.getElementById('guests-count');
        const totalPrice = document.getElementById('total-price');
        
        if (startDate && endDate && guests && daysCount && guestsCount && totalPrice) {
            const basePrice = parseFloat(totalPrice.textContent.replace('$', ''));
            
            function updatePrice() {
                if (startDate.value && endDate.value) {
                    const start = new Date(startDate.value);
                    const end = new Date(endDate.value);
                    const days = Math.ceil((end - start) / (1000 * 60 * 60 * 24));
                    const guestCount = parseInt(guests.value);
                    
                    if (days > 0) {
                        daysCount.textContent = days;
                        guestsCount.textContent = guestCount;
                        const total = basePrice * days * guestCount;
                        totalPrice.textContent = '$' + total.toFixed(0);
                    }
                }
            }
            
            startDate.addEventListener('change', updatePrice);
            endDate.addEventListener('change', updatePrice);
            guests.addEventListener('change', updatePrice);
            
            // Set minimum end date based on start date
            startDate.addEventListener('change', function() {
                if (this.value) {
                    const minEndDate = new Date(this.value);
                    minEndDate.setDate(minEndDate.getDate() + 1);
                    endDate.min = minEndDate.toISOString().split('T')[0];
                }
            });
        }
    }
});

// Add to Wishlist Functionality
document.addEventListener('DOMContentLoaded', function() {
    const wishlistButtons = document.querySelectorAll('.wishlist-btn');
    
    wishlistButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const destinationId = this.dataset.destinationId;
            
            // Toggle wishlist state
            this.classList.toggle('active');
            
            if (this.classList.contains('active')) {
                this.innerHTML = '<i class="fas fa-heart"></i> Added';
                showSuccess('Added to wishlist!');
            } else {
                this.innerHTML = '<i class="far fa-heart"></i> Add to Wishlist';
                showSuccess('Removed from wishlist!');
            }
            
            // Here you would typically make an API call to update the wishlist
            updateWishlist(destinationId, this.classList.contains('active'));
        });
    });
});

// Update Wishlist (placeholder function)
async function updateWishlist(destinationId, isAdded) {
    try {
        // This would be a real API call in a production app
        console.log(`${isAdded ? 'Added' : 'Removed'} destination ${destinationId} from wishlist`);
    } catch (error) {
        console.error('Error updating wishlist:', error);
    }
}

// Show Success Message
function showSuccess(message) {
    const successDiv = document.createElement('div');
    successDiv.className = 'success-message';
    successDiv.textContent = message;
    successDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #28a745;
        color: white;
        padding: 1rem;
        border-radius: 5px;
        z-index: 1000;
        animation: slideIn 0.3s ease;
    `;
    
    document.body.appendChild(successDiv);
    
    setTimeout(() => {
        successDiv.remove();
    }, 3000);
}

// Filter Functionality
document.addEventListener('DOMContentLoaded', function() {
    const filterForm = document.querySelector('.filter-form');
    
    if (filterForm) {
        const filterInputs = filterForm.querySelectorAll('input, select');
        
        filterInputs.forEach(input => {
            input.addEventListener('change', function() {
                // Auto-submit form when filters change
                filterForm.submit();
            });
        });
    }
});

// Review Form Enhancement
document.addEventListener('DOMContentLoaded', function() {
    const reviewForm = document.querySelector('.review-form');
    
    if (reviewForm) {
        const ratingInputs = reviewForm.querySelectorAll('input[name="rating"]');
        const commentTextarea = reviewForm.querySelector('textarea[name="comment"]');
        
        ratingInputs.forEach(input => {
            input.addEventListener('change', function() {
                // Enable comment field when rating is selected
                if (commentTextarea) {
                    commentTextarea.disabled = false;
                    commentTextarea.placeholder = 'Share your experience...';
                }
            });
        });
    }
});

// Add CSS for search suggestions
const style = document.createElement('style');
style.textContent = `
    .search-suggestions {
        position: absolute;
        top: 100%;
        left: 0;
        right: 0;
        background: white;
        border: 1px solid #ddd;
        border-top: none;
        border-radius: 0 0 5px 5px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        z-index: 1000;
        max-height: 200px;
        overflow-y: auto;
    }
    
    .suggestion-item {
        padding: 0.75rem 1rem;
        cursor: pointer;
        border-bottom: 1px solid #eee;
        transition: background-color 0.2s ease;
    }
    
    .suggestion-item:hover {
        background-color: #f8f9fa;
    }
    
    .suggestion-item:last-child {
        border-bottom: none;
    }
    
    .search-form {
        position: relative;
    }
    
    .wishlist-btn {
        transition: all 0.3s ease;
    }
    
    .wishlist-btn.active {
        color: #dc3545;
    }
    
    .wishlist-btn.active i {
        color: #dc3545;
    }
    
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
`;
document.head.appendChild(style);