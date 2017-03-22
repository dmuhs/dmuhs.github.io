#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = 'Dominik Muhs'
SITENAME = '/dev/log'
SITEURL = ''

PATH = 'content'

TIMEZONE = 'Europe/Berlin'

DEFAULT_LANG = 'en'
DEFAULT_DATE_FORMAT = '%d %B %Y'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = 'feeds/all.atom.xml'
FEED_ALL_RSS = 'feeds/all.rss.xml'
CATEGORY_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Blogroll
LINKS = (('Github', 'http://github.com/dmuhs'), )

DEFAULT_PAGINATION = 5
DISPLAY_CATEGORIES_ON_MENU = False
DISPLAY_CATEGORIES_ON_POST = True
DISPLAY_CATEGORY_OVERVIEW_ON_MENU = False
DISPLAY_ARCHIVE_ON_MENU = True
SINGLE_AUTHOR = True
THEME = 'simple'

FOOTER_TEXT = "Made with ♥"

IMAGE_PATH = 'images/'
THUMBNAIL_DIR = 'images/'
THUMBNAIL_SIZES = {
    'thumb': '580x?'
}

STATIC_PATHS = ['images', 'extra/CNAME']
PLUGIN_PATHS = ['plugins']
PLUGINS = ['thumbnailer']
EXTRA_PATH_METADATA = {'extra/CNAME': {'path': 'CNAME'}, }
