/**
 * PhotoSwipe Auto-Integration Script
 * Automatically converts article images to PhotoSwipe galleries
 * Groups adjacent images into the same gallery for better navigation
 */

function initPhotoSwipe() {
    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initPhotoSwipe);
        return;
    }

    // Import PhotoSwipe dynamically
    import('/theme/js/photoswipe-lightbox.esm.js').then(({ default: PhotoSwipeLightbox }) => {
        
        // Find all images in articles
        const articleImages = document.querySelectorAll('article img');
        
        if (articleImages.length === 0) {
            return;
        }

        // Group adjacent images into galleries
        const imageGroups = groupAdjacentImages(articleImages);
        let totalGalleries = 0;

        imageGroups.forEach((group, groupIndex) => {
            // Create a single gallery container for this group
            const galleryDiv = document.createElement('div');
            galleryDiv.className = group.length === 1 ? 'pswp-gallery single-image' : 'pswp-gallery';
            galleryDiv.setAttribute('data-gallery-id', `gallery-${groupIndex}`);
            
            // Process each image in the group
            group.forEach((img, imageIndex) => {
                // Skip if image is already wrapped in a PhotoSwipe link
                if (img.closest('.pswp-gallery')) {
                    return;
                }
                
                // Create link for this image
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
                
                // Replace the original image only for the first image in group
                if (imageIndex === 0) {
                    img.parentNode.replaceChild(galleryDiv, img);
                } else {
                    // Remove subsequent images as they're now part of the gallery
                    img.parentNode.removeChild(img);
                }
            });
            
            totalGalleries++;
        });

        // Initialize PhotoSwipe if we have galleries
        if (totalGalleries > 0) {
            const lightbox = new PhotoSwipeLightbox({
                gallery: '.pswp-gallery',
                children: 'a',
                pswpModule: () => import('/theme/js/photoswipe.esm.js'),
                showHideAnimationType: 'none'
            });
            lightbox.init();

            console.log(`PhotoSwipe initialized with ${totalGalleries} galleries containing ${articleImages.length} total images`);
        }
    }).catch(error => {
        console.warn('PhotoSwipe could not be loaded:', error);
    });
}

function groupAdjacentImages(images) {
    /**
     * Group adjacent images based on their DOM proximity
     * Images are considered adjacent if they are in consecutive paragraphs or have no significant content between them
     */
    const groups = [];
    let currentGroup = [];
    
    Array.from(images).forEach((img, index) => {
        if (currentGroup.length === 0) {
            // Start a new group
            currentGroup.push(img);
        } else {
            const lastImg = currentGroup[currentGroup.length - 1];
            
            // Check if this image is adjacent to the last one
            if (areImagesAdjacent(lastImg, img)) {
                currentGroup.push(img);
            } else {
                // Start a new group
                groups.push(currentGroup);
                currentGroup = [img];
            }
        }
        
        // If this is the last image, close the current group
        if (index === images.length - 1) {
            groups.push(currentGroup);
        }
    });
    
    return groups;
}

function areImagesAdjacent(img1, img2) {
    /**
     * Determine if two images are adjacent (should be in the same gallery)
     * They are adjacent if:
     * 1. They are in consecutive paragraphs with only images
     * 2. There's minimal text content between them
     * 3. They are both direct children of the same container
     */
    
    const parent1 = img1.closest('p') || img1.parentNode;
    const parent2 = img2.closest('p') || img2.parentNode;
    
    // If they have the same parent and it's the article, consider them adjacent
    if (parent1.parentNode === parent2.parentNode && parent1.parentNode.tagName === 'ARTICLE') {
        // Check if there are any non-trivial elements between the parents
        const elements = Array.from(parent1.parentNode.children);
        const index1 = elements.indexOf(parent1);
        const index2 = elements.indexOf(parent2);
        
        if (index1 !== -1 && index2 !== -1 && Math.abs(index1 - index2) <= 2) {
            // Check if there's significant content between them
            const start = Math.min(index1, index2);
            const end = Math.max(index1, index2);
            
            for (let i = start + 1; i < end; i++) {
                const element = elements[i];
                if (element.tagName === 'H1' || element.tagName === 'H2' || element.tagName === 'H3' ||
                    element.tagName === 'H4' || element.tagName === 'H5' || element.tagName === 'H6') {
                    return false; // Heading separates image groups
                }
                if (element.tagName === 'P' && element.textContent.trim().length > 50) {
                    return false; // Significant text separates image groups
                }
            }
            return true;
        }
    }
    
    return false;
}

function updateImageDimensions(link, img) {
    // Update link with actual image dimensions
    link.setAttribute('data-pswp-width', img.naturalWidth.toString());
    link.setAttribute('data-pswp-height', img.naturalHeight.toString());
}

// Initialize when script loads
initPhotoSwipe();