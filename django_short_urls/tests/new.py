# coding=utf-8

from __future__ import unicode_literals

from django.test.client import RequestFactory
from django_app.mongo_test_case import MongoTestCase

from django_short_urls.views import new
from django_short_urls.models import User
from http.status import HTTP_OK, HTTP_BAD_REQUEST, HTTP_UNAUTHORIZED, HTTP_FORBIDDEN, HTTP_CONFLICT


class ViewNewTestCase(MongoTestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.user = User(login="olefloch", api_key="foobar", email='olefloch@work4labs.com').save()

        self.data = {
            'login': self.user.login,
            'api_key': self.user.api_key
        }

    def test_unauthorized(self):
        self.assertEqual(new(self.factory.post('/new')).status_code, HTTP_UNAUTHORIZED)

    def test_bad_requests(self):
        # Test missing long_url
        self.assertEqual(new(self.factory.post('/new', self.data)).status_code, HTTP_BAD_REQUEST)

        self.data['long_url'] = 'http://work4.com'
        self.data['short_path'] = 'inva/lid'

        self.assertEqual(new(self.factory.post('/new', self.data)).status_code, HTTP_BAD_REQUEST)

        self.data['allow_slashes_in_prefix'] = True

        self.assertEqual(new(self.factory.post('/new', self.data)).status_code, HTTP_BAD_REQUEST)

        self.data['short_path'] = 'valid'
        self.data['prefix'] = 'inva/lid'
        del self.data['allow_slashes_in_prefix']

        self.assertEqual(new(self.factory.post('/new', self.data)).status_code, HTTP_BAD_REQUEST)

    def test_short_path_conflict(self):
        self.data['long_url'] = 'http://work4.com'
        self.data['short_path'] = 'conflict'

        new(self.factory.post('/new', self.data))

        self.data['long_url'] = 'http://some.thi.ng/different'

        self.assertEqual(new(self.factory.post('/new', self.data)).status_code, HTTP_CONFLICT)

        self.data['prefix'] = 'foobar'

        new(self.factory.post('/new', self.data))

        self.data['long_url'] = 'http://yet.aga.in/something/else'

        self.assertEqual(new(self.factory.post('/new', self.data)).status_code, HTTP_CONFLICT)

    def test_forbidden_keyword(self):
        self.data['long_url'] = 'http://work4.com'
        self.data['short_path'] = 'jobs'

        self.assertEqual(new(self.factory.post('/new', self.data)).status_code, HTTP_FORBIDDEN)

    def test_new(self):
        self.data['long_url'] = 'http://www.work4labs.com/'

        self.assertEqual(new(self.factory.post('/new', self.data)).status_code, HTTP_OK)

        self.data['short_path'] = 'bar'
        self.data['prefix'] = 'foo'

        self.assertEqual(new(self.factory.post('/new', self.data)).status_code, HTTP_OK)

        self.data['prefix'] = 'inva/lid'
        self.data['allow_slashes_in_prefix'] = True

        self.assertEqual(new(self.factory.post('/new', self.data)).status_code, HTTP_OK)
