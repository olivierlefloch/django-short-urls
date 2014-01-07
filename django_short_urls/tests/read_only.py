# coding=utf-8

from __future__ import unicode_literals

from django.conf import settings
from django.test.client import RequestFactory
from django_app.mongo_test_case import MongoTestCase

from django_short_urls.exceptions import DatabaseWriteDenied
from django_short_urls.middleware import ServiceUnavailableMiddleware
from django_short_urls.models import Link
from django_short_urls.views import main
from django_short_urls.w4l_http import HTTP_SERVICE_UNAVAILABLE


# pylint: disable=E1101
class ReadOnlyTestCase(MongoTestCase):
    def setUp(self):
        self.setting_backup = settings.SITE_READ_ONLY

        settings.SITE_READ_ONLY = True

        self.factory = RequestFactory()

        self.path = 'test42'
        self.link = Link.shorten('http://www.work4.com/jobs', 'olefloch', short_path=self.path)

    def tearDown(self):
        settings.SITE_READ_ONLY = self.setting_backup

    def test_views(self):
        response = main(self.factory.get('/%s' % self.path), self.path)

        # Make sure we're still redirecting
        self.assertEqual(response.status_code, 302)
        # But not logging clicks
        self.assertEqual(self.link.clicks, 0)

    def test_middleware_process_request(self):
        self.assertEqual(
            ServiceUnavailableMiddleware().process_request(self.factory.post('/')).status_code,
            HTTP_SERVICE_UNAVAILABLE
        )

        self.assertTrue(ServiceUnavailableMiddleware().process_request(self.factory.get('/')) is None)

    def test_middleware_process_view(self):
        self.assertTrue(
            ServiceUnavailableMiddleware().process_view(None, lambda x: True, [], {})
        )

        # pylint: disable=W0613
        def raise_write_denied(self):
            raise DatabaseWriteDenied()

        self.assertEqual(
            ServiceUnavailableMiddleware().process_view(None, raise_write_denied, [], {}).status_code,
            HTTP_SERVICE_UNAVAILABLE
        )
