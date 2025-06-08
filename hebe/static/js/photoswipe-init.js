/**
 * PhotoSwipe Auto-Integration Script
 * Automatically converts article images to PhotoSwipe galleries
 */

function initPhotoSwipe() {
    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initPhotoSwipe);
        return;
    }

    // Import PhotoSwipe dynamically
    import('/theme/js/photoswipe-lightbox.esm.js').then(({ default: PhotoSwipeLightbox }) => {
        
        // Find all images in articles and wrap them for PhotoSwipe
        const articleImages = document.querySelectorAll('article img');
        let galleryItems = [];
        
        articleImages.forEach((img, index) => {
            // Skip if image is already wrapped in a PhotoSwipe link
            if (img.closest('.pswp-gallery')) {
                return;
            }
            
            // Create wrapper div
            const galleryDiv = document.createElement('div');
            galleryDiv.className = 'pswp-gallery pswp-gallery--single-column';
            
            // Create link
            const link = document.createElement('a');
            link.href = img.src;
            link.target = '_blank';
            
            // Set default dimensions - we'll update these when image loads
            link.setAttribute('data-pswp-width', '1200');
            link.setAttribute('data-pswp-height', '800');
            
            // Get actual image dimensions
            if (img.complete && img.naturalWidth !== 0) {
                updateImageDimensions(link, img);
            } else {
                img.addEventListener('load', () => updateImageDimensions(link, img));
            }
            
            // Clone the image to preserve all attributes
            const newImg = img.cloneNode(true);
            
            // Build the structure
            link.appendChild(newImg);
            galleryDiv.appendChild(link);
            
            // Replace the original image with the gallery wrapper
            img.parentNode.replaceChild(galleryDiv, img);
            
            galleryItems.push(galleryDiv);
        });
        
        // Initialize PhotoSwipe if we have gallery items
        if (galleryItems.length > 0) {
            const lightbox = new PhotoSwipeLightbox({
                gallery: '.pswp-gallery',
                children: 'a',
                pswpModule: () => import('/theme/js/photoswipe.esm.js')
            });
            lightbox.init();
            
            console.log(`PhotoSwipe initialized with ${galleryItems.length} images`);
        }
    }).catch(error => {
        console.warn('PhotoSwipe could not be loaded:', error);
    });
}

function updateImageDimensions(link, img) {
    // Update link with actual image dimensions
    link.setAttribute('data-pswp-width', img.naturalWidth.toString());
    link.setAttribute('data-pswp-height', img.naturalHeight.toString());
}

// Initialize when script loads
initPhotoSwipe(); 