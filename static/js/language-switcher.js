document.addEventListener('DOMContentLoaded', function() {
    // Language switcher functionality
    const languageSwitcher = document.getElementById('language-switcher');
    const languageOptions = document.getElementById('language-options');
    
    if (languageSwitcher && languageOptions) {
        // Toggle language options visibility on click
        languageSwitcher.addEventListener('click', function(e) {
            e.stopPropagation();
            languageOptions.classList.toggle('hidden');
        });
        
        // Hide language options when clicking outside
        document.addEventListener('click', function() {
            if (!languageOptions.classList.contains('hidden')) {
                languageOptions.classList.add('hidden');
            }
        });
        
        // Prevent hiding when clicking on the options themselves
        languageOptions.addEventListener('click', function(e) {
            e.stopPropagation();
        });
    }
    
    // Handle language selection
    const languageLinks = document.querySelectorAll('.language-option');
    languageLinks.forEach(link => {
        link.addEventListener('click', function() {
            // The actual redirect is handled by the href attribute
            if (languageOptions) {
                languageOptions.classList.add('hidden');
            }
        });
    });
});
