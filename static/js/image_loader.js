// This script will load placeholder images from Unsplash

document.addEventListener('DOMContentLoaded', function() {
    // Product images
    const productImages = {
        'bt_cloud': 'https://images.unsplash.com/photo-1489389944381-3471b5b30f04?w=500&auto=format&fit=crop&q=60',
        'ai': 'https://images.unsplash.com/photo-1677442135137-12b5faf8c1f6?w=500&auto=format&fit=crop&q=60',
        'wms': 'https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?w=500&auto=format&fit=crop&q=60',
        'iot': 'https://images.unsplash.com/photo-1580584126903-c17d41830450?w=500&auto=format&fit=crop&q=60',
        'cybouz': 'https://images.unsplash.com/photo-1600880292203-757bb62b4baf?w=500&auto=format&fit=crop&q=60',
        'custom': 'https://images.unsplash.com/photo-1577760258779-e787a1733016?w=500&auto=format&fit=crop&q=60',
    };

    // Case study images
    const caseStudyImages = {
        'case_kintone': 'https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=500&auto=format&fit=crop&q=60',
        'case_ai_inspection': 'https://images.unsplash.com/photo-1563770660941-10958e003f16?w=500&auto=format&fit=crop&q=60',
        'case_foreign_labor': 'https://images.unsplash.com/photo-1521791136064-7986c2920216?w=500&auto=format&fit=crop&q=60',
        'case_ai_ocr': 'https://images.unsplash.com/photo-1618044619888-009e412ff12a?w=500&auto=format&fit=crop&q=60',
        'case_temperature': 'https://images.unsplash.com/photo-1620466302161-76ae61171989?w=500&auto=format&fit=crop&q=60',
        'case_more': 'https://images.unsplash.com/photo-1553877522-43269d4ea984?w=500&auto=format&fit=crop&q=60',
    };

    // Replace all product image placeholders
    document.querySelectorAll('.product-image-placeholder').forEach(img => {
        const productKey = img.getAttribute('data-product');
        if (productKey && productImages[productKey]) {
            img.src = productImages[productKey];
            img.alt = productKey.replace('_', ' ').toUpperCase();
        }
    });

    // Replace all case study image placeholders
    document.querySelectorAll('.case-study-image-placeholder').forEach(img => {
        const caseKey = img.getAttribute('data-case');
        if (caseKey && caseStudyImages[caseKey]) {
            img.src = caseStudyImages[caseKey];
            img.alt = caseKey.replace('_', ' ').toUpperCase();
        }
    });
});