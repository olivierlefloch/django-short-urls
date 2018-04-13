# coding=utf-8

from __future__ import unicode_literals

from django.http import Http404
from django.test.client import RequestFactory
from mock import patch

from django_app.test import PyW4CTestCase
# pylint 1.7.1 gets confused and thinks `http` is a standard python module. Not in python 2.7.x…
from http.status import HTTP_REDIRECT_PERMANENTLY  # pylint: disable=wrong-import-order

from django_short_urls.views import _extract_valid_path, main
from django_short_urls.models import Link


class ViewMainTestCase(PyW4CTestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.path = 'test42'
        self.location = 'http://www.work4.com/jobs'
        self.link = Link.shorten(self.location, short_path=self.path)

    def test_extract_valid_path(self):
        self.assertEqual(_extract_valid_path('work4us'), 'work4us')
        self.assertEqual(_extract_valid_path('foo/&bar'), 'foo')
        self.assertEqual(_extract_valid_path('%5C'), '')

    def call_main(self, query):
        with patch('django_short_urls.views.statsd') as mock_statsd:
            response = main(self.factory.get('/' + query), query)

        self.assertEqual(mock_statsd.increment.call_count, 1)

        return response

    def test_redirect(self):
        response = self.call_main(self.path)

        self.assertEqual(response.status_code, HTTP_REDIRECT_PERMANENTLY)
        self.assertEqual(self.link.reload().clicks, 1)

    def test_suffixes(self):
        response = self.call_main(self.path)

        def expect_same_with_suffix(suffix):
            """Check that appending a certain suffix leaves the response unchanged"""
            response_with_suffix = self.call_main(self.path + suffix)

            self.assertEqual(response_with_suffix.status_code, HTTP_REDIRECT_PERMANENTLY)
            self.assertEqual(response_with_suffix.serialize_headers(), response.serialize_headers())

        expect_same_with_suffix('&foobar')
        expect_same_with_suffix('/%5C')
        expect_same_with_suffix('%C2%A0%E2%80%A6')

    @patch('django_short_urls.views.proxy')
    def test_act_as_proxy(self, mock_proxy):
        self.link.act_as_proxy = True
        self.link.save()

        self.call_main(self.path)

        self.assertEqual(mock_proxy.call_count, 1)

    def test_redirect_suffix(self):
        response = self.call_main(self.path + '/recruiter')

        self.assertEqual(response.status_code, HTTP_REDIRECT_PERMANENTLY)

    def test_redirect_missing_suffix(self):
        response = self.call_main(self.path + '/deleted/suffix')

        self.assertEqual(response.status_code, HTTP_REDIRECT_PERMANENTLY)
        self.assertEqual(response['location'], self.location + '?redirect_suffix=deleted%2Fsuffix&ref=shortener')

    def test_redirect_with_utf8_query_param(self):
        with patch('django_short_urls.views.statsd'):
            response = main(self.factory.get('/' + self.path + '?bla=éàû'), self.path)

        self.assertEqual(response.status_code, HTTP_REDIRECT_PERMANENTLY)
        self.assertEqual(response['location'], self.location + '?bla=%C3%A9%C3%A0%C3%BB&ref=shortener')

    def test_404(self):
        path404 = self.path + 'foobar'

        with self.assertRaises(Http404):
            self.call_main(path404)

        with self.assertRaises(Http404):
            self.call_main(path404 + '/')

    def test_divide_by_zero(self):
        with self.assertRaises(ZeroDivisionError):
            self.client.get('/DivideByZeroPlease')
