# coding=utf-8

from __future__ import unicode_literals

from django_app.test import PyW4CTestCase
from http.status import HTTP_OK


class UrlsTestCase(PyW4CTestCase):
    def test_robots(self):
        response = self.client.get('/robots.txt')

        self.assertEqual(response.status_code, HTTP_OK)
        self.assertIn('User-agent: AhrefsBot', response.content)
