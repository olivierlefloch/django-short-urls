# coding=utf-8

"""Django settings for django_short_urls project."""

from __future__ import unicode_literals

import logging

import mongoengine
from pymongo.read_preferences import ReadPreference

from django_app.default_settings import init_web_settings

from django_short_urls.local_settings import *  # pylint: disable=W0614, W0401


APP_NAME = 'django_short_urls'

#########################
# Default configuration #
#########################

globals().update(init_web_settings(
    app_name=APP_NAME, debug=DEBUG, sentry_dsn=SENTRY_DSN,
    late_middleware=('django_short_urls.middleware.ServiceUnavailableMiddleware',)
))

#######
# SSL #
#######

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https, https')

#############
# Databases #
#############

try:
    mongoengine.connect(host=MONGO_URI, read_preference=ReadPreference.PRIMARY_PREFERRED)

    SERVICE_UNAVAILABLE = False
except mongoengine.connection.ConnectionError, err:  # pragma: no cover
    logging.error('MongoEngine ConnectionError: %s', err)
    SERVICE_UNAVAILABLE = True
