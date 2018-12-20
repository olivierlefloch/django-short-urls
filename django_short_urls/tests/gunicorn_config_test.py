# coding=utf-8
# Micro test for coverage, ensure config can be loaded

from django_app.test import PyW4CTestCase

from django_short_urls import gunicorn_config


class GunicornConfigTestCase(PyW4CTestCase):
    def test(self):
        self.assertEqual(gunicorn_config.threads, 0)
