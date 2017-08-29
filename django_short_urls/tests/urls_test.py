# coding=utf-8

from __future__ import unicode_literals

from django_app.test import PyW4CTestCase
# pylint 1.7.1 gets confused and thinks `http` is a standard python module. Not in python 2.7.x…
from http.status import HTTP_OK  # pylint: disable=wrong-import-order


class UrlsTestCase(PyW4CTestCase):
    def test_robots(self):
        response = self.client.get('/robots.txt')

        self.assertEqual(response.status_code, HTTP_OK)
        self.assertIn('User-agent: AhrefsBot', response.content)
