# coding=utf-8

from __future__ import unicode_literals

from django.core.handlers.wsgi import WSGIHandler

from django_app.test import PyW4CTestCase

from django_short_urls.wsgi import application


class WsgiTestCase(PyW4CTestCase):
    def test(self):
        self.assertIs(type(application), WSGIHandler)
