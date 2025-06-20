/**
 * PhotoSwipe Initialization Script
 * Simply initializes PhotoSwipe on existing gallery structures generated by the Pelican plugin.
 * No DOM manipulation needed - the galleries are already properly structured.
 */

function initPhotoSwipe() {
    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initPhotoSwipe);
        return;
    }

    // Check if we have any PhotoSwipe galleries on the page
    const galleries = document.querySelectorAll('.pswp-gallery');

    if (galleries.length === 0) {
        return;
    }

    // Import PhotoSwipe dynamically and initialize
    import('/theme/js/photoswipe-lightbox.esm.js')
        .then(({ default: PhotoSwipeLightbox }) => {
            const lightbox = new PhotoSwipeLightbox({
                gallery: '.pswp-gallery',
                children: 'a',
                pswpModule: () => import('/theme/js/photoswipe.esm.js'),
                // showHideAnimationType: 'none'
            });

            lightbox.init();

            console.log(`PhotoSwipe initialized with ${galleries.length} galleries`);
        })
        .catch(error => {
            console.warn('PhotoSwipe could not be loaded:', error);
        });
}

// Initialize when script loads
initPhotoSwipe();
