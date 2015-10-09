# coding=utf-8

from __future__ import unicode_literals

from django.test.client import RequestFactory
from django.utils.http import urlencode
from django_app.test import PyW4CTestCase
from mock import patch
from requests.auth import _basic_auth_str

from django_short_urls.views import new
from django_short_urls.models import User
from http.status import HTTP_OK, HTTP_BAD_REQUEST, HTTP_UNAUTHORIZED, HTTP_FORBIDDEN, HTTP_CONFLICT


class ViewNewTestCase(PyW4CTestCase):
    def setUp(self):
        self._factory = RequestFactory()

        self.user = User(login="olefloch", api_key="wfdre!4$%", email='olefloch@work4labs.com').save()

        self.long_url = 'http://work4.com'

    def _post(self, url, data=None, with_auth=True, **extra):
        post_extra = {
            'QUERY_STRING': urlencode(data, doseq=True) if data else ''
        }
        post_extra.update(extra)

        if with_auth:
            post_extra['HTTP_AUTHORIZATION'] = _basic_auth_str(self.user.login, self.user.api_key)

        return self._factory.post(url, **post_extra)

    @patch('django_short_urls.views.statsd')
    def test_unauthorized(self, mock_statsd):
        # No auth sent
        self.assertEqual(new(self._post('/new', with_auth=False)).status_code, HTTP_UNAUTHORIZED)

        # Digest auth
        request = self._post(
            '/new', with_auth=False,
            HTTP_AUTHORIZATION='Digest username="Mufasa", ...invalid'
        )
        self.assertEqual(new(request).status_code, HTTP_UNAUTHORIZED)
        self.assertEqual(mock_statsd.increment.call_count, 0)

    def test_bad_requests(self):
        # Test missing long_url
        self.assertEqual(new(self._post('/new')).status_code, HTTP_BAD_REQUEST)

        # Test for slashes in the short_path
        data = {
            'long_url': self.long_url,
            'short_path': 'inva/lid'
        }
        self.assertEqual(new(self._post('/new', data)).status_code, HTTP_BAD_REQUEST)

        data['allow_slashes_in_prefix'] = True
        self.assertEqual(new(self._post('/new', data)).status_code, HTTP_BAD_REQUEST)

        # Test for slashes in the prefix
        data = {
            'long_url': self.long_url,
            'short_path': 'valid',
            'prefix': 'inva/lid'
        }
        self.assertEqual(new(self._post('/new', data)).status_code, HTTP_BAD_REQUEST)

        # Test for other invalid chars in the url ('%', '?', etc.)
        data = {
            'long_url': self.long_url,
            'short_path': 'inva&lid',
        }
        self.assertEqual(new(self._post('/new', data)).status_code, HTTP_BAD_REQUEST)

    @patch('django_short_urls.views.statsd')
    def test_short_path_conflict(self, mock_statsd):
        # Create the base conflicting link
        data = {
            'long_url': self.long_url,
            'short_path': 'conflict'
        }
        new(self._post('/new', data))

        # Conflict when trying to replace an existing short_path with a different long_url target
        data['long_url'] = 'http://some.thi.ng/different'
        self.assertEqual(new(self._post('/new', data)).status_code, HTTP_CONFLICT)

        # Now check the same thing with urls that include a prefix - first create
        data['prefix'] = 'foobar'
        self.assertEqual(new(self._post('/new', data)).status_code, HTTP_OK)

        # Now trigger the conflict
        data['long_url'] = 'http://yet.aga.in/something/else'
        self.assertEqual(new(self._post('/new', data)).status_code, HTTP_CONFLICT)

        self.assertEqual(mock_statsd.increment.call_count, 4)

    @patch('django_short_urls.views.statsd')
    def test_forbidden_keyword(self, mock_statsd):
        data = {
            'long_url': self.long_url,
            'short_path': 'jobs'
        }
        self.assertEqual(new(self._post('/new', data)).status_code, HTTP_FORBIDDEN)
        self.assertEqual(mock_statsd.increment.call_count, 1)

    @patch('django_short_urls.models.statsd')
    @patch('django_short_urls.views.statsd')
    def test_new(self, mock_views_statsd, mock_models_statsd):  # pylint: disable=unused-argument
        data = {
            'long_url': self.long_url
        }
        self.assertEqual(new(self._post('/new', data)).status_code, HTTP_OK)

        data['short_path'] = 'bar'
        data['prefix'] = 'foo'
        self.assertEqual(new(self._post('/new', data)).status_code, HTTP_OK)

        data['prefix'] = 'inva/lid'
        data['allow_slashes_in_prefix'] = True
        self.assertEqual(new(self._post('/new', data)).status_code, HTTP_OK)

        self.assertEqual(mock_views_statsd.increment.call_count, 3)
