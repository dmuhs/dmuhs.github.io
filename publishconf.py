# This file is only used if you use `make publish` or
# explicitly specify it as your config file.

import os
import sys

sys.path.append(os.curdir)
from pelicanconf import *

# If your site is available via HTTPS, make sure SITEURL begins with https://
SITEURL = "https://spoons.fyi"
RELATIVE_URLS = False

FEED_ALL_RSS = "feeds/all.rss.xml"
CATEGORY_FEED_RSS = "feeds/{slug}.rss.xml"

OPTIMIZE_IMAGES_DEV_MODE = False
DELETE_OUTPUT_DIRECTORY = True
