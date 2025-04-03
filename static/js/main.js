document.addEventListener('DOMContentLoaded', function() {
    // Mobile menu toggle
    const mobileMenuButton = document.getElementById('mobile-menu-button');
    const mobileMenu = document.getElementById('mobile-menu');
    
    if (mobileMenuButton && mobileMenu) {
        mobileMenuButton.addEventListener('click', function() {
            mobileMenu.classList.toggle('active');
            // Toggle between menu and close icons
            const menuIcon = mobileMenuButton.querySelector('.menu-icon');
            const closeIcon = mobileMenuButton.querySelector('.close-icon');
            
            if (menuIcon && closeIcon) {
                menuIcon.classList.toggle('hidden');
                closeIcon.classList.toggle('hidden');
            }
        });
    }
    
    // Close mobile menu when clicking outside
    document.addEventListener('click', function(event) {
        if (mobileMenu && mobileMenu.classList.contains('active') && 
            !mobileMenu.contains(event.target) && 
            !mobileMenuButton.contains(event.target)) {
            mobileMenu.classList.remove('active');
            
            const menuIcon = mobileMenuButton.querySelector('.menu-icon');
            const closeIcon = mobileMenuButton.querySelector('.close-icon');
            
            if (menuIcon && closeIcon) {
                menuIcon.classList.remove('hidden');
                closeIcon.classList.add('hidden');
            }
        }
    });
    
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                window.scrollTo({
                    top: targetElement.offsetTop - 80, // Adjust for header height
                    behavior: 'smooth'
                });
                
                // Close mobile menu after clicking a link
                if (mobileMenu && mobileMenu.classList.contains('active')) {
                    mobileMenu.classList.remove('active');
                    
                    const menuIcon = mobileMenuButton.querySelector('.menu-icon');
                    const closeIcon = mobileMenuButton.querySelector('.close-icon');
                    
                    if (menuIcon && closeIcon) {
                        menuIcon.classList.remove('hidden');
                        closeIcon.classList.add('hidden');
                    }
                }
            }
        });
    });
    
    // Initialize animation for elements that should animate when they enter the viewport
    const animatedElements = document.querySelectorAll('.animate-on-scroll');
    
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.1
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-fadeIn');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    animatedElements.forEach(el => {
        observer.observe(el);
    });
    
    // Contact form validation
    const contactForm = document.getElementById('contact-form');
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            const nameField = document.getElementById('name');
            const emailField = document.getElementById('email');
            const messageField = document.getElementById('message');
            
            let isValid = true;
            
            // Simple validation
            if (nameField && nameField.value.trim() === '') {
                nameField.classList.add('border-red-500');
                isValid = false;
            } else if (nameField) {
                nameField.classList.remove('border-red-500');
            }
            
            if (emailField) {
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (!emailRegex.test(emailField.value.trim())) {
                    emailField.classList.add('border-red-500');
                    isValid = false;
                } else {
                    emailField.classList.remove('border-red-500');
                }
            }
            
            if (messageField && messageField.value.trim() === '') {
                messageField.classList.add('border-red-500');
                isValid = false;
            } else if (messageField) {
                messageField.classList.remove('border-red-500');
            }
            
            if (!isValid) {
                e.preventDefault();
                // Display error message
                const errorMsg = document.getElementById('form-error');
                if (errorMsg) {
                    errorMsg.classList.remove('hidden');
                }
            }
        });
    }
});
