# coding=utf-8

"""Django settings for pywork4core project (used for texts)."""

from __future__ import unicode_literals

import logging

import mongoengine

from django_app.default_settings import init_web_settings


APP_NAME = 'django_app'

DEBUG = True

SECRET_KEY = 'Foobar'

#########################
# Default configuration #
#########################

globals().update(init_web_settings(app_name=APP_NAME, debug=DEBUG, sentry_dsn=None))


# Databases

try:
    mongoengine.connect(tz_aware=USE_TZ, **MONGOENGINE)  # pylint: disable=undefined-variable
except mongoengine.connection.ConnectionError, err:  # pragma: no cover
    logging.error('MongoEngine ConnectionError: %s', err)

INSTALLED_APPS = (APP_NAME,)
