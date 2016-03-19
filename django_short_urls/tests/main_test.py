# coding=utf-8

from __future__ import unicode_literals

from django.http import Http404
from django.test.client import RequestFactory
from mock import patch

from django_app.test import PyW4CTestCase
from http.status import HTTP_REDIRECT_PERMANENTLY

from django_short_urls.views import _extract_valid_path, main
from django_short_urls.models import Link


class ViewMainTestCase(PyW4CTestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.path = 'test42'
        self.link = Link.shorten('http://www.work4.com/jobs', short_path=self.path)

    def test_extract_valid_path(self):
        self.assertEqual(_extract_valid_path('work4us'), 'work4us')
        self.assertEqual(_extract_valid_path('foo/&bar'), 'foo')
        self.assertEqual(_extract_valid_path('%5C'), '')

    @patch('django_short_urls.views.statsd')
    def test_redirect(self, mock_statsd):
        response = main(self.factory.get('/%s' % self.path), self.path)
        self.assertEqual(response.status_code, HTTP_REDIRECT_PERMANENTLY)
        self.assertEqual(self.link.reload().clicks, 1)
        self.assertEqual(mock_statsd.increment.call_count, 1)

        def expect_same_with_suffix(suffix):
            """Check that appending a certain suffix leaves the response unchanged"""
            path_with_suffix = self.path + suffix

            response_with_suffix = main(self.factory.get('/%s' % path_with_suffix), path_with_suffix)

            self.assertEqual(response_with_suffix.status_code, response.status_code)
            self.assertEqual(response_with_suffix.serialize_headers(), response.serialize_headers())

        expect_same_with_suffix('&foobar')
        expect_same_with_suffix('/%5C')
        expect_same_with_suffix('%C2%A0%E2%80%A6')

    @patch('django_short_urls.views.proxy')
    @patch('django_short_urls.views.statsd')
    def test_act_as_proxy(self, mock_statsd, mock_proxy):  # pylint: disable=W0613
        self.link.act_as_proxy = True
        self.link.save()

        main(self.factory.get('/%s' % self.path), self.path)
        self.assertEqual(mock_proxy.call_count, 1)

    @patch('django_short_urls.views.statsd')
    def test_redirect_suffix(self, mock_statsd):  # pylint: disable=unused-argument
        response = main(self.factory.get('/%s/recruiter' % self.path), self.path + '/recruiter')

        self.assertEqual(response.status_code, HTTP_REDIRECT_PERMANENTLY)

    def test_redirect_with_utf8_query_param(self):
        with patch('django_short_urls.views.statsd'):
            response = main(self.factory.get('/' + self.path + '?bla=éàû'), self.path)

        self.assertEqual(response.status_code, HTTP_REDIRECT_PERMANENTLY)
        self.assertEqual(
            response['location'],
            'http://www.work4.com/jobs?bla=%C3%A9%C3%A0%C3%BB&ref=shortener')

    @patch('django_short_urls.views.statsd')
    def test_404(self, mock_statsd):  # pylint: disable=unused-argument
        path404 = self.path + 'foobar'

        with self.assertRaises(Http404):
            main(self.factory.get('/%s' % path404), path404)

        with self.assertRaises(Http404):
            main(self.factory.get('/%s/' % path404), path404 + '/')

    def test_divide_by_zero(self):
        with self.assertRaises(ZeroDivisionError):
            self.client.get('/DivideByZeroPlease')  # pylint: disable=E1103
