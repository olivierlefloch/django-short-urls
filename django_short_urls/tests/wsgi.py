from __future__ import unicode_literals

from django.core.handlers.wsgi import WSGIHandler
from django.utils import unittest

from django_short_urls.wsgi import application


class WsgiTestCase(unittest.TestCase):
    def test(self):
        self.assertIs(type(application), WSGIHandler)
