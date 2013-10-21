# coding=utf-8

from __future__ import unicode_literals

from django.test.client import RequestFactory
from django_app.mongo_test_case import MongoTestCase

from django_short_urls.models import Click, Link


class ClickTestCase(MongoTestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.path = 'test42'
        self.link = Link.shorten('http://www.work4.com/jobs', 'olefloch', short_path=self.path)

    def test_click(self):
        request = self.factory.get('/%s' % self.path)

        self.assertTrue('Click: (%s' % (request.get_full_path()) in str(Click.register(request, self.link)))
