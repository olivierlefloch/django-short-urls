# coding=utf-8

"""Django settings for django_short_urls project."""

from __future__ import unicode_literals

import logging
from pymongo.read_preferences import ReadPreference

from django_app.default_settings import init_settings

from django_short_urls.local_settings import *  # pylint: disable=W0614, W0401


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

######################
# ERRORS AND LOGGING #
######################

if SENTRY_DSN is not None:  # pragma: no cover
    globals()['INSTALLED_APPS'] += ('raven.contrib.django.raven_compat',)

if not DEBUG:  # pragma: no cover
    LOGGING = {
        'version': 1,
        'formatters': {
            'standard': {
                'format': "%(levelname)s [%(module)s] %(message)s"
            },
        },
        'handlers': {
            'console': {
                'level': 'WARNING',
                'class': 'logging.StreamHandler',
                'formatter': 'standard'
            },
            'sentry': {
                'level': 'ERROR',
                'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
            }
        },
        'root': {
            'handlers': ['console', 'sentry'],
            'level': 'WARNING'
        }
    }

#############
# Databases #
#############

import mongoengine

try:
    # pylint: disable=W0142
    mongoengine.connect(read_preference=ReadPreference.PRIMARY_PREFERRED, **MONGOENGINE)

    SERVICE_UNAVAILABLE = False
except mongoengine.connection.ConnectionError, err:  # pragma: no cover
    logging.error('MongoEngine ConnectionError: %s', err)
    SERVICE_UNAVAILABLE = True
