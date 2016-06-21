#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = 'Dominik Muhs'
SITENAME = '/dev/log'
# SITESUBTITLE = ''
SITEURL = ''

PATH = 'content'

TIMEZONE = 'Europe/Berlin'

DEFAULT_LANG = 'en'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = 'feeds/all.atom.xml'
FEED_ALL_RSS = 'feeds/all.rss.xml'
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Blogroll
LINKS = (('Github', 'http://github.com/dmuhs'),)

# Social widget
# SOCIAL = (('You can add links in your config file', '#'),
#          ('Another social link', '#'),)

DEFAULT_PAGINATION = 5
DISPLAY_CATEGORIES_ON_MENU = False
DISPLAY_CATEGORIES_ON_POST = True
SINGLE_AUTHOR = True
THEME = 'chunk'

IMAGE_PATH = 'images/'
THUMBNAIL_DIR = 'images/'
THUMBNAIL_SIZES = {
    'thumb': '580x?'
}

STATIC_PATHS = ['images', 'extra/CNAME']
PLUGIN_PATHS = ['plugins']
PLUGINS = ['thumbnailer']
EXTRA_PATH_METADATA = {'extra/CNAME': {'path': 'CNAME'}, }

# Uncomment following line if you want document-relative URLs when developing
# RELATIVE_URLS = True
