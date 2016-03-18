# coding=utf-8

"""
Default Django settings for all Work4 projects.

Your own app should import all attributes from this file.
"""

from __future__ import unicode_literals

import os


def env_to_bool(val):  # pylint: disable=E0602
    """Use this when parsing environment variables for booleans as it will properly consider 'FALSE' to be False."""
    if isinstance(val, basestring):
        return val.lower() in ("true", "yes", "1")
    else:
        return bool(val)


# pylint: disable=invalid-name, unused-variable
def init_settings(APP_NAME, DEBUG):
    """
    Initializes default settings. Should be called in the projects settings.py, passing any custom parameters that
    might be used.
    """

    globals()['APP_NAME'] = APP_NAME
    globals()['DEBUG'] = DEBUG

    INSTALLED_APPS = ('django_app', 'django_nose', 'django_extensions', APP_NAME)

    # Directories

    # Determine project's root directory based on the path to the module
    # referenced by APP_NAME, in order to handle both standalone and subtree
    # scenarios for pywork4core
    PROJECT_ROOT_DIR = os.path.dirname(__import__(APP_NAME).__path__[0])

    APP_ROOT_DIR = os.path.join(PROJECT_ROOT_DIR, APP_NAME)

    TEMPLATE_DIRS = (os.path.join(APP_ROOT_DIR, 'templates'),)
    TEMP_DIR = os.path.join(PROJECT_ROOT_DIR, 'temp')
    # Do not remove that variable, even if pywork4core doesn't use it itself
    # It might be used in upper projects (that extends pywork4core)
    VENV_DIR = os.path.join(PROJECT_ROOT_DIR, 'venv')

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': TEMP_DIR + '/db.sqlite'
        }
    }

    MONGOENGINE = os.environ.get('MONGOENGINE', {
        'db': APP_NAME,
        'host': 'localhost',
        'port': 27017,
        'username': '',
        'password': ''
    })

    # Timezone management
    # Use operating system's timezone
    TIME_ZONE = None
    USE_TZ = True

    # Language
    LANGUAGE_CODE = 'en-us'
    USE_I18N = False
    USE_L10N = False

    TEMPLATE_DEBUG = DEBUG

    ###########
    # TESTING #
    ###########

    TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
    NOSE_ARGS = ['--logging-clear-handlers']  # Nose capturing logs is all we need during tests

    # The only tangible logging performed by this configuration is to send an email to
    # the site admins on every HTTP 500 error when DEBUG=False.
    # See http://docs.djangoproject.com/en/dev/topics/logging for
    # more details on how to customize your logging configuration.
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'filters': {
            'require_debug_false': {
                '()': 'django.utils.log.RequireDebugFalse'
            },
        },
        'formatters': {
            'verbose': {
                'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
            },
            'simple': {
                'format': '%(levelname)s %(asctime)s %(module)s %(message)s'
            },
        },
        'handlers': {
            'mail_admins': {
                'level': 'CRITICAL',
                'filters': ['require_debug_false'],
                'class': 'django.utils.log.AdminEmailHandler'
            },
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'verbose'
            },
        },
        'loggers': {
            'django.request': {
                'handlers': ['mail_admins'],
                'level': 'ERROR',
                'propagate': True,
            },
            'app': {
                'handlers': ['console'],
                'level': 'DEBUG',
                'propagate': True,
            },
            # 'api' is used for API related activity
            'api': {
                'handlers': ['console'],
                'level': 'WARNING',
                'propagate': True,
            },
        }
    }

    return locals().iteritems()
