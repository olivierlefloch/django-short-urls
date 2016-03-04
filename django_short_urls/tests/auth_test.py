# coding=utf-8

from __future__ import unicode_literals

from mock import Mock

from django_app.test import PyW4CTestCase
from http.status import HTTP_UNAUTHORIZED

from django_short_urls.auth import _safe_base64_decode, login_with_basic_auth_required
from django_short_urls.models import User


@login_with_basic_auth_required
def _test_view(request):  # pylint: disable=unused-argument
    """Test view that does nothing"""
    raise NotImplementedError("You can't be here")


class AuthTestCase(PyW4CTestCase):
    def test__safe_base64_decode(self):
        # Basic test
        self.assertEqual(_safe_base64_decode('bG9naW46cGFzc3dvcmQ='), 'login:password')
        # Add some unicode in there
        self.assertEqual(_safe_base64_decode('w6lsw6lwaGFudA=='), 'éléphant')
        # Insufficient padding, recover gracefully
        self.assertEqual(_safe_base64_decode('w6lsw6lwaGFudA'), 'éléphant')
        # Try decoding something that's not base64 encoded, return an empty string
        self.assertEqual(_safe_base64_decode('login:password'), '')
        # Invalid utf8, raise an error
        with self.assertRaises(UnicodeDecodeError):
            print _safe_base64_decode('77+97+9')

    def test_bad_auth(self):
        self.assertEqual(
            _test_view(Mock(META={"HTTP_AUTHORIZATION": "Basic "})).status_code,
            HTTP_UNAUTHORIZED)

        self.assertEqual(
            _test_view(Mock(META={"HTTP_AUTHORIZATION": "Basic login:password"})).status_code,
            HTTP_UNAUTHORIZED)

        self.assertEqual(
            _test_view(Mock(META={"HTTP_AUTHORIZATION": "Basic bG9naW46cGFzc3dvcmQ="})).status_code,
            HTTP_UNAUTHORIZED)

    def test_good_auth(self):
        User(login="login", api_key="password", email='toto@work4labs.com').save()

        with self.assertRaises(NotImplementedError):
            _test_view(Mock(META={"HTTP_AUTHORIZATION": "Basic bG9naW46cGFzc3dvcmQ="}))
