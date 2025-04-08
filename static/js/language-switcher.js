// Language Switcher JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Get all elements with the language-switcher class
    const languageSwitchers = document.querySelectorAll('.language-switcher');
    
    // Add click event listeners to each switcher
    languageSwitchers.forEach(switcher => {
        switcher.addEventListener('click', function(event) {
            // We don't need to preventDefault as we're now using proper URLs
            // that will be handled by the backend
            console.log('Language switcher clicked:', this.getAttribute('href'));
        });
    });
});
