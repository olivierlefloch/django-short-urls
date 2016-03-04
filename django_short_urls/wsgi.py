# coding=utf-8

"""
WSGI config for django_short_urls project.

This module contains the WSGI application used by Django's development server
and any production WSGI deployments. It should expose a module-level variable
named ``application``. Django's ``runserver`` and ``runfcgi`` commands discover
this application via the ``WSGI_APPLICATION`` setting.

Usually you will have the standard Django WSGI application here, but it also
might make sense to replace the whole Django WSGI application with a custom one
that later delegates to the Django one. For example, you could introduce WSGI
middleware here, or combine a Django application with an application of another
framework.

"""
from __future__ import unicode_literals

import os
import sys


ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.append(ROOT_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_short_urls.settings")

# The following imports cannot be placed at the top of the file since they Django to be initialized properly
# pylint: disable=wrong-import-position
from raven.contrib.django.raven_compat.middleware.wsgi import Sentry  # noqa
from django.core.wsgi import get_wsgi_application  # noqa


application = Sentry(get_wsgi_application())  # pylint: disable=C0103
