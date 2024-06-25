# AUTHOR = 'Dominik Muhs'
SITENAME = "plaintext"
SITEURL = ""

THEME = "hebe"

TIMEZONE = "Europe/Berlin"

# Feed generation is usually not desired when developing
# FEED_ALL_ATOM = "feeds/all.atom.xml"
# CATEGORY_FEED_ATOM = "feeds/{slug}.atom.xml"
# FEED_ALL_RSS = "feeds/all.rss.xml"
# CATEGORY_FEED_RSS = "feeds/{slug}.rss.xml"

USE_FOLDER_AS_CATEGORY = False

# Blogroll
LINKS = (
    ("GitHub", "https://github.com/dmuhs"),
    # ("Bluesky", "https://bsky.app/profile/lethalspoons.bsky.social"),
)

DEFAULT_PAGINATION = 25

# Uncomment following line if you want document-relative URLs when developing
# RELATIVE_URLS = True

PATH = "content"
ARTICLE_PATHS = ["blog"]
ARTICLE_URL = ARTICLE_SAVE_AS = "{date:%Y}/{date:%m}/{date:%d}/{slug}.html"
AUTHORS_SAVE_AS = ""
TAGS_SAVE_AS = ""
ARCHIVES_SAVE_AS = ""
CATEGORIES_SAVE_AS = ""
# DISPLAY_CATEGORIES_ON_MENU = False

STATIC_PATHS = [
    "images",
    "extra",
]

EXTRA_PATH_METADATA = {
    # 'extra/custom.css': {'path': 'custom.css'},
    "extra/robots.txt": {"path": "robots.txt"},
    # 'extra/favicon.ico': {'path': 'favicon.ico'},
    "extra/CNAME": {"path": "CNAME"},
}
LIQUID_TAGS = ["img", "literal", "video", "youtube", "vimeo", "include_code"]

IMAGE_PROCESS_FORCE = False
IMAGE_PROCESS = {
    "article-image": {
        "type": "responsive-image",
        "srcset": [
            ("1x", ["scale_in 800 600 True"]),
            ("2x", ["scale_in 1600 1200 True"]),
            ("4x", ["scale_in 3200 2400 True"]),
        ],
        "default": "1x",
    },
}
