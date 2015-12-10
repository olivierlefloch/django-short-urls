# coding=utf-8

from __future__ import unicode_literals

from raven.contrib.django.middleware.wsgi import Sentry

from django_app.test import PyW4CTestCase

from django_short_urls.wsgi import application


class WsgiTestCase(PyW4CTestCase):
    def test(self):
        self.assertIs(type(application), Sentry)
