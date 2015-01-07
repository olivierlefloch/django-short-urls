# coding=utf-8

"""Django settings for pywork4core project (used for texts)."""

from __future__ import unicode_literals

import logging


from django_app.default_settings import init_settings

APP_NAME = 'django_app'

DEBUG = True

MONGOENGINE = {
    'db': 'pywork4core',
    'host': 'localhost',
    'port': 27017,
    'username': '',
    'password': ''
}

SECRET_KEY = 'Foobar'

#########################
# Default configuration #
#########################

for (key, value) in init_settings(APP_NAME=APP_NAME, DEBUG=DEBUG):
    if key not in globals():
        globals()[key] = value


# Databases

import mongoengine

try:
    # pylint: disable=W0142,E0602
    mongoengine.connect(tz_aware=USE_TZ, **MONGOENGINE)
except mongoengine.connection.ConnectionError, err:  # pragma: no cover
    logging.error('MongoEngine ConnectionError: %s', err)

INSTALLED_APPS = (APP_NAME,)
