# coding=utf-8

from __future__ import unicode_literals

from django.http import HttpResponse
from django.utils import unittest
from mock import Mock, patch

from django_short_urls.w4l_http import (
    validate_url, url_append_parameters, proxy, response_service_unavailable, get_browser, get_client_ip,
    HTTP_SERVICE_UNAVAILABLE
)


class W4lHttpTestCase(unittest.TestCase):
    def test(self):
        self.assertEqual(validate_url('http://workfor.us'), (True, None))
        self.assertEqual(validate_url('http://app.work4labs.com/jobs?job_id=42'), (True, None))

        self.assertEqual(validate_url('foobar')[0], False)
        self.assertEqual(validate_url('jobs?job_id=42')[0], False)
        self.assertEqual(validate_url('ftp://work4labs.com')[0], False)
        self.assertEqual(validate_url('http://app:bar@work4labs.com')[0], False)

    def test__url_append_parameters(self):
        self.assertEqual(
            url_append_parameters('http://workfor.us', dict(), dict()),
            'http://workfor.us'
        )
        self.assertEqual(
            url_append_parameters('http://workfor.us', {'toto': 'tata'}, dict()),
            'http://workfor.us?toto=tata'
        )
        self.assertEqual(
            url_append_parameters('http://www.theuselessweb.com/', {'foo': 'search'}, {'foo': 'bar'}),
            'http://www.theuselessweb.com/?foo=search'
        )
        self.assertEqual(
            url_append_parameters('http://www.theuselessweb.com?a=1&b=2&z=5', {'foo': 'séarch'}, {'b': '3'}),
            'http://www.theuselessweb.com?a=1&b=2&z=5&foo=s%C3%A9arch'
        )
        self.assertEqual(
            url_append_parameters('http://www.theuselessweb.com?foo=4', {'foo': 'search'}, {'c': '42'}),
            'http://www.theuselessweb.com?c=42&foo=search'
        )

    @patch('django_short_urls.w4l_http.requests.get')
    def test_proxy(self, requests_get):
        url = 'http://www.work4labs.com'

        self.assertEqual(type(proxy(url)), HttpResponse)

        requests_get.assert_called_once_with(url)

    def test_unavailable(self):
        self.assertEquals(response_service_unavailable().status_code, HTTP_SERVICE_UNAVAILABLE)

    def test_get_browser(self):
        def _mock_browser(ua_str):
            return Mock(META={'HTTP_USER_AGENT': ua_str})

        self.assertEqual(get_browser(_mock_browser(
            'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)'
        )), 'ie')
        self.assertEqual(get_browser(_mock_browser(
            'Mozilla/5.0 (iPod; U; CPU iPhone OS 4_3_3 like Mac OS X; ja-jp) AppleWebKit/533.17.9 (KHTML, like Gecko) \
                Version/5.0.2 Mobile/8J2 Safari/6533.18.5'
        )), 'iphone')
        self.assertEqual(get_browser(_mock_browser(
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/537.13+ (KHTML, like Gecko) Version/5.1.7 \
                Safari/534.57.2'
        )), 'safari')
        self.assertEqual(get_browser(_mock_browser(
            'curl/7.9.8 (i686-pc-linux-gnu) libcurl 7.9.8 (OpenSSL 0.9.6b) (ipv6 enabled)'
        )), 'unknown')

    def test_get_client_ip(self):
        wrong_ip = '127.0.0.1'
        right_ip = '42.42.42.42'

        self.assertEqual(get_client_ip(
            Mock(META={'REMOTE_ADDR': right_ip})
        ), right_ip)

        self.assertEqual(get_client_ip(
            Mock(META={'REMOTE_ADDR': wrong_ip, 'HTTP_X_FORWARDED_FOR': right_ip})
        ), right_ip)

        self.assertEqual(get_client_ip(
            Mock(META={'REMOTE_ADDR': wrong_ip, 'HTTP_X_FORWARDED_FOR': '%s,%s' % (wrong_ip, right_ip)})
        ), right_ip)
