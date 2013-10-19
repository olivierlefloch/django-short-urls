from __future__ import unicode_literals

from django.utils import unittest

from django_short_urls.w4l_http import validate_url, url_append_parameters


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
            url_append_parameters('http://www.theuselessweb.com?a=1&b=2&z=5', {'foo': 'search'}, {'b': '3'}),
            'http://www.theuselessweb.com?a=1&b=2&z=5&foo=search'
        )
        self.assertEqual(
            url_append_parameters('http://www.theuselessweb.com?foo=4', {'foo': 'search'}, {'c': '42'}),
            'http://www.theuselessweb.com?c=42&foo=search'
        )
