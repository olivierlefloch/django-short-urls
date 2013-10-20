# coding=utf-8

from __future__ import unicode_literals

from django.conf import settings
from django.test.client import RequestFactory
from django_app.mongo_test_case import MongoTestCase

from django_short_urls.views import main
from django_short_urls.models import Link, Click


# pylint: disable=E1101
class ReadOnlyTestCase(MongoTestCase):
    def setUp(self):
        self.setting_backup = settings.SITE_READ_ONLY

        settings.SITE_READ_ONLY = True

        self.factory = RequestFactory()

        self.path = 'test42'
        self.link = Link.shorten('http://www.work4.com/jobs', 'olefloch', short_path=self.path)

    def test_views(self):
        response = main(self.factory.get('/%s' % self.path), self.path)

        # Make sure we're still redirecting
        self.assertEqual(response.status_code, 302)
        # But not logging clicks
        self.assertEqual(Click.objects.count(), 0)

    def tearDown(self):
        settings.SITE_READ_ONLY = self.setting_backup
