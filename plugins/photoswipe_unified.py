"""
PhotoSwipe Unified Plugin for Pelican
Combines thumbnail generation and PhotoSwipe gallery creation in a single plugin.
"""
import logging
import re
import shutil
from pathlib import Path
from pelican import signals

logger = logging.getLogger(__name__)

# Configuration
THUMBNAIL_SIZE = (800, 600)
THUMBNAIL_QUALITY = 85
SIZE_THRESHOLD = 300 * 1024  # 300KB


class ImageProcessor:
    """Handles image path resolution, thumbnail generation, and file operations."""

    def __init__(self, settings):
        self.settings = settings
        self.content_path = Path(settings.get('PATH', 'content'))
        self.output_path = Path(settings.get('OUTPUT_PATH', 'output'))

    def resolve_image_path(self, src, content_file_path):
        """Resolve image URL to actual file path and output URL."""
        if src.startswith(('http://', 'https://')):
            return None  # Skip external images

        # Handle {attach} URLs
        if '{attach}' in src:
            relative_path = src.replace('{attach}', '').lstrip('/')
            content_dir = Path(content_file_path).parent if content_file_path else Path()

            # Try to find the actual file
            for base_path in [content_dir, self.content_path]:
                file_path = base_path / relative_path
                if file_path.exists():
                    # Generate output URL
                    if content_dir != Path() and self.content_path in content_dir.parents:
                        rel_from_content = content_dir.relative_to(self.content_path)
                        output_url = f"/{rel_from_content}/{relative_path}" if rel_from_content != Path('.') else f"/{relative_path}"
                    else:
                        output_url = f"/{relative_path}"

                    return {'file_path': file_path, 'output_url': output_url}
        else:
            # Regular local image - try multiple paths
            src_path = Path(src.lstrip('/'))
            for base_path in [Path(), self.output_path, self.content_path]:
                file_path = base_path / src_path
                if file_path.exists():
                    return {'file_path': file_path, 'output_url': src}

        return None

    def should_generate_thumbnail(self, file_path):
        """Check if image is large enough to warrant thumbnail generation."""
        try:
            return file_path.stat().st_size > SIZE_THRESHOLD
        except OSError:
            return False

    def get_thumbnail_path(self, file_path):
        """Get the thumbnail path for a given image file."""
        return file_path.with_name(f"{file_path.stem}_thumb.jpg")

    def get_thumbnail_url(self, output_url):
        """Get the thumbnail URL for a given output URL."""
        url_path = Path(output_url)
        return str(url_path.with_name(f"{url_path.stem}_thumb.jpg"))

    def generate_thumbnail(self, file_path, thumbnail_path):
        """Generate a thumbnail for the given image."""
        try:
            from PIL import Image

            # Skip if thumbnail already exists and is newer than original
            if (thumbnail_path.exists() and
                thumbnail_path.stat().st_mtime > file_path.stat().st_mtime):
                return True

            with Image.open(file_path) as img:
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')

                # Generate thumbnail maintaining aspect ratio
                img.thumbnail(THUMBNAIL_SIZE, Image.Resampling.LANCZOS)

                # Save thumbnail
                thumbnail_path.parent.mkdir(parents=True, exist_ok=True)
                img.save(thumbnail_path, 'JPEG', quality=THUMBNAIL_QUALITY, optimize=True)

                logger.info(f"Generated thumbnail: {thumbnail_path}")
                return True

        except Exception as e:
            logger.error(f"Error generating thumbnail for {file_path}: {e}")
            return False

    def get_image_dimensions(self, file_path):
        """Get image dimensions."""
        try:
            from PIL import Image
            with Image.open(file_path) as img:
                return img.width, img.height
        except Exception as e:
            logger.error(f"Error getting dimensions for {file_path}: {e}")
            return 1200, 800  # Fallback dimensions


class ThumbnailManager:
    """Manages thumbnail tracking and copying to output directory."""

    def __init__(self, output_path):
        self.output_path = Path(output_path)
        self.thumbnails_to_copy = []

    def track_thumbnail(self, thumbnail_path, thumbnail_url):
        """Track a thumbnail for copying to output."""
        self.thumbnails_to_copy.append({
            'path': Path(thumbnail_path),
            'url': thumbnail_url
        })

    def copy_thumbnails(self):
        """Copy all tracked thumbnails to the output directory."""
        if not self.thumbnails_to_copy:
            return

        logger.info(f"Copying {len(self.thumbnails_to_copy)} thumbnails to output")

        for thumbnail_info in self.thumbnails_to_copy:
            thumbnail_path = thumbnail_info['path']
            thumbnail_url = thumbnail_info['url']

            if not thumbnail_path.exists():
                continue

            # Calculate output path for thumbnail
            output_thumbnail_path = self.output_path / thumbnail_url.lstrip('/')

            # Create directory and copy thumbnail
            output_thumbnail_path.parent.mkdir(parents=True, exist_ok=True)
            try:
                shutil.copy2(thumbnail_path, output_thumbnail_path)
                logger.info(f"Copied thumbnail: {output_thumbnail_path}")
            except Exception as e:
                logger.error(f"Error copying thumbnail {thumbnail_path} to {output_thumbnail_path}: {e}")


class GalleryBuilder:
    """Builds PhotoSwipe gallery HTML from processed images."""

    @staticmethod
    def is_minimal_content(content):
        """Check if content between images is minimal."""
        clean = re.sub(r'\s+|<p>\s*</p>|<br\s*/?>', ' ', content.strip())
        return (not re.search(r'<h[1-6]', clean, re.I) and
                len(re.sub(r'<[^>]*>', '', clean).strip()) <= 50)

    @staticmethod
    def group_adjacent_images(images, html_content):
        """Group adjacent images based on content between them."""
        if not images:
            return []

        groups = []
        current_group = [images[0]]

        for img in images[1:]:
            gap = html_content[current_group[-1]['end']:img['start']]
            if GalleryBuilder.is_minimal_content(gap):
                current_group.append(img)
            else:
                groups.append(current_group)
                current_group = [img]
        groups.append(current_group)

        return groups

    @staticmethod
    def create_gallery_html(images, gallery_id):
        """Create PhotoSwipe gallery HTML."""
        css_class = "pswp-gallery single-image" if len(images) == 1 else "pswp-gallery"

        gallery_html = f'<div class="{css_class}" data-gallery-id="gallery-{gallery_id}">\n'
        for img in images:
            # Use original image for lightbox, thumbnail for display
            lightbox_src = img.get('original_url', img['display_url'])
            gallery_html += f'''    <a href="{lightbox_src}" data-pswp-width="{img['width']}" data-pswp-height="{img['height']}" target="_blank">
        <img src="{img['display_url']}" alt="{img['alt']}" class="{img['class']}" />
    </a>
'''
        gallery_html += '</div>'
        return gallery_html


class PhotoSwipeUnified:
    """Main plugin class that orchestrates thumbnail generation and gallery creation."""

    def __init__(self, settings):
        self.settings = settings
        self.image_processor = ImageProcessor(settings)
        self.thumbnail_manager = ThumbnailManager(settings.get('OUTPUT_PATH', 'output'))
        self.gallery_builder = GalleryBuilder()

    def process_html_content(self, html_content, content_file_path=None):
        """Process HTML content to generate thumbnails and create PhotoSwipe galleries."""
        # Extract and process all images
        processed_images = self._extract_and_process_images(html_content, content_file_path)

        if not processed_images:
            return html_content

        # Group images into galleries and replace in HTML
        return self._create_galleries(html_content, processed_images)

    def _extract_and_process_images(self, html_content, content_file_path):
        """Extract images from HTML and process them for thumbnails."""
        img_pattern = r'<p>\s*(<img[^>]*>)\s*</p>|(<img[^>]*>)'
        processed_images = []

        for match in re.finditer(img_pattern, html_content):
            img_tag = match.group(1) or match.group(2)

            # Extract image attributes
            src_match = re.search(r'src="([^"]*)"', img_tag)
            if not src_match:
                continue

            src = src_match.group(1)
            alt = (re.search(r'alt="([^"]*)"', img_tag) or ['', ''])[1]
            css_class = (re.search(r'class="([^"]*)"', img_tag) or ['', ''])[1]

            # Process the image
            processed_img = self._process_single_image(src, content_file_path)
            if processed_img:
                processed_img.update({
                    'alt': alt,
                    'class': css_class,
                    'start': match.start(),
                    'end': match.end(),
                })
                processed_images.append(processed_img)

        return processed_images

    def _create_galleries(self, html_content, processed_images):
        """Group images into galleries and replace them in HTML."""
        image_groups = self.gallery_builder.group_adjacent_images(processed_images, html_content)

        # Replace images with galleries
        new_content = html_content
        offset = 0

        for i, group in enumerate(image_groups):
            gallery_html = self.gallery_builder.create_gallery_html(group, i)
            start = group[0]['start'] + offset
            end = group[-1]['end'] + offset

            new_content = new_content[:start] + gallery_html + new_content[end:]
            offset += len(gallery_html) - (end - start)

        return new_content

    def _process_single_image(self, src, content_file_path):
        """Process a single image: resolve paths, generate thumbnail if needed."""
        # Resolve image path
        image_info = self.image_processor.resolve_image_path(src, content_file_path)
        if not image_info:
            return None  # Skip external or not found images

        file_path = image_info['file_path']
        original_url = image_info['output_url']

        # Get image dimensions
        width, height = self.image_processor.get_image_dimensions(file_path)

        # Check if we need a thumbnail
        if self.image_processor.should_generate_thumbnail(file_path):
            thumbnail_path = self.image_processor.get_thumbnail_path(file_path)
            if self.image_processor.generate_thumbnail(file_path, thumbnail_path):
                thumbnail_url = self.image_processor.get_thumbnail_url(original_url)

                # Track thumbnail for copying
                self.thumbnail_manager.track_thumbnail(thumbnail_path, thumbnail_url)

                return {
                    'display_url': thumbnail_url,
                    'original_url': original_url,
                    'width': width,
                    'height': height
                }
        else:
            # No thumbnail needed, use original
            return {
                'display_url': original_url,
                'width': width,
                'height': height
            }

    def finalize(self):
        """Copy thumbnails to output directory."""
        self.thumbnail_manager.copy_thumbnails()


# Global plugin instance
plugin_instance = None


def get_plugin_instance(settings):
    """Get or create the global plugin instance."""
    global plugin_instance
    if plugin_instance is None:
        plugin_instance = PhotoSwipeUnified(settings)
    return plugin_instance


def process_content(generator):
    """Process articles and pages."""
    instance = get_plugin_instance(generator.settings)

    items = getattr(generator, 'articles', []) + getattr(generator, 'pages', [])

    for item in items:
        if hasattr(item, '_content'):
            item._content = instance.process_html_content(
                item._content,
                getattr(item, 'source_path', None)
            )


def finalize_processing(generator):
    """Finalize processing by copying thumbnails."""
    instance = get_plugin_instance(generator.settings)
    instance.finalize()


def register():
    """Register the plugin with Pelican."""
    signals.article_generator_finalized.connect(process_content)
    signals.page_generator_finalized.connect(process_content)
    signals.finalized.connect(finalize_processing)