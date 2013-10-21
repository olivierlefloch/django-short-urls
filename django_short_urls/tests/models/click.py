# coding=utf-8

from __future__ import unicode_literals

from django.test.client import RequestFactory
from django_app.mongo_test_case import MongoTestCase
from mock import patch

from django_short_urls.models import Click, Link


class ClickTestCase(MongoTestCase):
    def setUp(self):
        self.path = 'test42'
        self.link = Link.shorten('http://www.work4.com/jobs', 'olefloch', short_path=self.path)

        self.request = RequestFactory().get('/%s' % self.path)

    def test_click(self):
        self.assertTrue('Click: (%s' % (self.request.get_full_path()) in str(Click.register(self.request, self.link)))

    def test_save_exception(self):
        # Mocking mongoengine.Document.save to have it raise an Exception when called
        # (such as because the DB is read only)
        with patch('django_short_urls.models.Document.save', side_effect=Exception()) as mongoengine_save:
            Click.register(self.request, self.link)

        mongoengine_save.assert_called_once_with()

        self.assertEqual(Click.objects.count(), 0)
