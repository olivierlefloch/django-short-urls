# coding=utf-8

"""
Default Django settings for all Work4 projects.

Your own app should import all attributes from this file.
"""

from __future__ import unicode_literals

import os
import sys


def env_to_bool(val):
    """Use this when parsing environment variables for booleans as it will properly consider 'FALSE' to be False."""
    if isinstance(val, basestring):
        return val.lower() in ("true", "yes", "1")
    else:
        return bool(val)


def init_settings(app_name, debug):
    """
    Initializes default settings. Should be called in the projects settings.py, passing any custom parameters that
    might be used.
    """

    # Determine project's root directory based on the path to the module
    # referenced by app_name, in order to handle both standalone and subtree
    # scenarios for pywork4core
    project_root_dir = os.path.dirname(__import__(app_name).__path__[0])
    app_root_dir = os.path.join(project_root_dir, app_name)
    temp_dir = os.path.join(project_root_dir, 'temp')

    # Needs its own line to avoid pragma no cover bleeding into other statements
    log_level = 'DEBUG' if debug else 'INFO'  # pragma: no cover

    return {
        'APP_NAME': app_name,
        'DEBUG': debug,

        'INSTALLED_APPS': ('django.contrib.contenttypes', 'django_app', 'django_nose', 'django_extensions', app_name),

        # Directories

        'PROJECT_ROOT_DIR': project_root_dir,
        'APP_ROOT_DIR': app_root_dir,
        'TEMPLATE_DIRS': (os.path.join(app_root_dir, 'templates'),),
        'TEMP_DIR': temp_dir,
        'VENV_DIR': os.path.join(project_root_dir, 'venv'),

        # Timezone management: Use operating system's timezone
        'TIME_ZONE': None,
        'USE_TZ': True,

        # Language
        'LANGUAGE_CODE': 'en-us',
        'USE_I18N': False,
        'USE_L10N': False,

        # Templating
        'TEMPLATE_DEBUG': debug,

        # Databases
        'DATABASES': {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': temp_dir + '/db.sqlite'
            }
        },
        'MONGOENGINE': os.environ.get('MONGOENGINE', {
            'db': app_name,
            'host': 'localhost',
            'port': 27017,
            'username': '',
            'password': ''
        }),

        ###########
        # TESTING #
        ###########
        'TESTING': len(sys.argv) > 1 and sys.argv[1] == 'test',
        'TEST_RUNNER': 'django_nose.NoseTestSuiteRunner',
        # During tests, Nose captures all logs during tests
        'NOSE_ARGS': ['--logging-clear-handlers'],

        ###########
        # LOGGING #
        ###########
        'LOG_LEVEL': log_level,
        'LOGGING': {
            'version': 1,
            'formatters': {
                'standard': {
                    'format': "%(levelname)s [%(module)s] %(message)s"
                },
            },
            'handlers': {
                'console': {
                    'level': log_level,
                    'class': 'logging.StreamHandler',
                    'formatter': 'standard',
                    'stream': sys.stdout
                }
            },
            'loggers': {
                'django': {
                    'level': 'INFO',   # We don't want Django's debug, even in development mode.
                    'handlers': [],    # Don't handle logs at this level,
                    'propagate': True  # But bubble up to the `root` logger.
                },
            },
            'root': {
                'handlers': ['console'],
                'level': log_level
            }
        }
    }


# pylint: disable=used-before-assignment
def init_web_settings(app_name, debug, sentry_dsn, early_middleware=(), late_middleware=()):
    """
    Appends extra Django settings useful specifically for web apps, such as static files handling, etc.

    :param sentry_dsn: a string containing the DSN to configure the raven client. Projects defining
                       this parameter MUST add `raven` to their pip requirements.

    settings: dict
    return: dict
    """

    # Load settings dict into local scope for concision and coherence

    settings = init_settings(app_name, debug)

    staticfiles_dirs = (os.path.join(settings['APP_ROOT_DIR'], 'static'),)

    # Needs its own line to avoid pragma no cover bleeding into other statements
    staticfiles_storage = 'whitenoise.storage.CompressedManifestStaticFilesStorage'\
        if not settings['TESTING'] \
        else 'django.contrib.staticfiles.storage.StaticFilesStorage'  # pragma: no cover

    template_context_processors = (settings.get('TEMPLATE_CONTEXT_PROCESSORS', ()) + (
        ("django.core.context_processors.debug",) if debug else ()))  # pragma: no cover

    settings.update({
        # Installed apps
        'INSTALLED_APPS': ('whitenoise.runserver_nostatic', 'django.contrib.staticfiles') + settings['INSTALLED_APPS'],

        # Routing
        'ROOT_URLCONF': app_name + '.urls',

        # Static files, templates
        'STATIC_ROOT': 'staticfiles',
        'STATIC_URL': '/static/',
        'STATICFILES_DIRS': staticfiles_dirs,

        # Don't use Whitenoise's static files storage in testing as it requires running collectstatic
        'STATICFILES_STORAGE': staticfiles_storage,

        'WHITENOISE_ROOT': staticfiles_dirs[0] + '/files',
        'WHITENOISE_ALLOW_ALL_ORIGINS': False,

        'TEMPLATE_CONTEXT_PROCESSORS': template_context_processors
    })

    ##########
    # SENTRY #
    ##########

    if sentry_dsn:  # pragma: no cover
        settings['INSTALLED_APPS'] = ('raven.contrib.django.raven_compat',) + settings['INSTALLED_APPS']

        settings['LOGGING']['handlers']['sentry'] = {
            'level': 'ERROR',
            'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
        }
        settings['LOGGING']['root']['handlers'].append('sentry')

        # import-error disabled: Raven shall only be a dependency of projects that define sentry_dsn
        import raven  # pylint: disable=wrong-import-position, wrong-import-order, import-error

        settings['RAVEN_CONFIG'] = {'dsn': sentry_dsn}

        try:
            settings['RAVEN_CONFIG']['release'] = raven.fetch_git_sha(settings['PROJECT_ROOT_DIR'])
        except raven.exceptions.InvalidGitRepository:
            # Probably not a git repo (on heroku?)
            pass

    settings['MIDDLEWARE_CLASSES'] = _compute_middleware_settings(
        early_middleware, late_middleware, use_sentry=bool(sentry_dsn))

    return settings


def _compute_middleware_settings(early=(), late=(), use_sentry=False):
    """This method takes care of inserting the app's middlewares without conflicting with Sentry's positioning"""
    return ((
        'raven.contrib.django.raven_compat.middleware.SentryResponseErrorIdMiddleware',
        'raven.contrib.django.raven_compat.middleware.Sentry404CatchMiddleware') if use_sentry else ()) \
        + early + ('django.middleware.common.CommonMiddleware',) + late
