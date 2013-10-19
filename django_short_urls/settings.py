# coding=utf-8

"""Django settings for django_short_urls project."""

from __future__ import unicode_literals

import logging


from pywork4core.django_app.default_settings import init_settings

# pylint: disable=W0614, W0401
from django_short_urls.local_settings import *

APP_NAME = 'django_short_urls'

MANAGERS = ADMINS

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django_short_urls.middleware.ServiceUnavailableMiddleware',
)

ROOT_URLCONF = 'django_short_urls.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'django_short_urls.wsgi.application'

AUTHENTICATION_BACKENDS = (
    'mongoengine.django.auth.MongoEngineBackend',
)

#########################
# Default configuration #
#########################

for (key, value) in init_settings(APP_NAME=APP_NAME, DEBUG=DEBUG):
    if key not in globals():
        globals()[key] = value


# Databases

import mongoengine

try:
    # pylint: disable=W0142
    mongoengine.connect(**MONGOENGINE)

    SERVICE_UNAVAILABLE = False
except mongoengine.connection.ConnectionError, err:
    logging.error('MongoEngine ConnectionError: %s', err)
    SERVICE_UNAVAILABLE = True
