# coding=utf-8

from __future__ import unicode_literals

from django.http import Http404
from django.test.client import RequestFactory
from django_app.mongo_test_case import MongoTestCase

from django_short_urls.views import main
from django_short_urls.models import Link


class ViewsTestCase(MongoTestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.path = 'test42'

    def test404(self):

        with self.assertRaises(Http404):
            print main(self.factory.get('/%s' % self.path), self.path)

        with self.assertRaises(Http404):
            main(self.factory.get('/%s/' % self.path), self.path + '/')

    def test_redirect(self):
        Link.shorten('http://www.work4.com/jobs', 'olefloch', short_path=self.path)

        response = main(self.factory.get('/%s' % self.path), self.path)

        self.assertEqual(response.status_code, 302)
