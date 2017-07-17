# coding=utf-8

from __future__ import unicode_literals

from django.test.client import RequestFactory
from mock import Mock, patch
import mongoengine

from django_app.test import PyW4CTestCase
# pylint 1.7.1 gets confused and thinks `http` is a standard python module. Not in python 2.7.x…
from http.status import HTTP_REDIRECT_PERMANENTLY, HTTP_SERVICE_UNAVAILABLE  # pylint: disable=wrong-import-order

from django_short_urls.middleware import ServiceUnavailableMiddleware
from django_short_urls.models import Link
from django_short_urls.views import main


# pylint: disable=W0613,E1101
class ReadOnlyTestCase(PyW4CTestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.path = 'test42'
        self.link = Link.shorten('http://www.work4.com/jobs', short_path=self.path)

    @patch('django_short_urls.views.statsd')
    @patch('django_short_urls.views.mongoengine_is_primary', return_value=False)
    def test_views(self, mock_mongoengine_is_primary, mock_statsd):
        response = main(self.factory.get('/%s' % self.path), self.path)

        # Make sure we're still redirecting
        self.assertEqual(response.status_code, HTTP_REDIRECT_PERMANENTLY)
        # But not logging clicks
        self.assertEqual(self.link.clicks, 0)

    @patch('django_short_urls.middleware.mongoengine_is_primary', return_value=False)
    def test_middleware_process_request(self, mock_mongoengine_is_primary):
        self.assertEqual(
            ServiceUnavailableMiddleware(get_response=Mock())(self.factory.post('/')).status_code,
            HTTP_SERVICE_UNAVAILABLE
        )

        mock_request = Mock(method='GET')
        # Yes, get_response is `lambda x: x`, so the response will be mock_request – but that's fine,
        # that's not what we're testing here anyway
        self.assertEqual(ServiceUnavailableMiddleware(get_response=lambda x: x)(mock_request), mock_request)

    @patch('django_short_urls.middleware.mongoengine_is_primary', return_value=False)
    def test_middleware_process_view(self, mock_mongoengine_is_primary):
        self.assertTrue(
            ServiceUnavailableMiddleware(get_response=lambda x: x).process_view(None, lambda x: True, [], {})
        )

        def raise_write_denied(request):  # pylint: disable=W0613
            raise mongoengine.connection.MongoEngineConnectionError()

        status_code = ServiceUnavailableMiddleware(
            get_response=Mock()).process_view(None, raise_write_denied, [], {}).status_code
        self.assertEqual(status_code, HTTP_SERVICE_UNAVAILABLE)
