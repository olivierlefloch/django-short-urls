from django.utils import unittest

from django_short_urls.models import Link

class ValidRandomShortPathsTestCase(unittest.TestCase):
    def test(self):
        self.assertEqual(Link.is_valid_random_short_path("ab2cd"), True)
        self.assertEqual(Link.is_valid_random_short_path("ab2"), True)
        self.assertEqual(Link.is_valid_random_short_path("a234r434g43gb32r"), True)
        self.assertEqual(Link.is_valid_random_short_path("4a"), True)

        self.assertEqual(Link.is_valid_random_short_path("abcd"), False)
        self.assertEqual(Link.is_valid_random_short_path("ge"), False)
        self.assertEqual(Link.is_valid_random_short_path("crap"), False)
        self.assertEqual(Link.is_valid_random_short_path("crap42"), False)
        self.assertEqual(Link.is_valid_random_short_path("abe4abe"), False)


from w4l_http import validate_url, url_append_parameters

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
            url_append_parameters('http://workfor.us', dict()),
            'http://workfor.us'
        )
        self.assertEqual(
            url_append_parameters('http://workfor.us', {'toto': 'tata'}),
            'http://workfor.us?toto=tata'
        )
        self.assertEqual(
            url_append_parameters('http://www.theuselessweb.com/', {'foo': 'search'}),
            'http://www.theuselessweb.com/?foo=search'
        )
        self.assertEqual(
            url_append_parameters('http://www.theuselessweb.com?a=1&b=2&z=5', {'foo': 'search'}),
            'http://www.theuselessweb.com?a=1&b=2&z=5&foo=search'
        )
        self.assertEqual(
            url_append_parameters('http://www.theuselessweb.com?foo=4', {'foo': 'search'}),
            'http://www.theuselessweb.com?foo=search'
        )


from suffix_catchall import get_hash_from

class ValidRedirectPathTestCase(unittest.TestCase):
    def test__get_hash_from(self):
        self.assertEqual(get_hash_from('azertyuiop'), ('azertyuiop', None))
        self.assertEqual(get_hash_from('azerty/uiop'), ('azerty/uiop', None))
        self.assertEqual(get_hash_from('a/z/e/r/t/y/u/i/o/p'), ('a/z/e/r/t/y/u/i/o/p', None))

        self.assertEqual(get_hash_from('some/hash/recruiter'), ('some/hash', 'recruiter'))
        self.assertEqual(get_hash_from('some/hash/share'), ('some/hash', 'share'))
        self.assertEqual(get_hash_from('some/hash/search'), ('some/hash', 'search'))

        self.assertEqual(get_hash_from('some/hashrecruiter'), ('some/hashrecruiter', None))
        self.assertEqual(get_hash_from('some/hashshare'), ('some/hashshare', None))
        self.assertEqual(get_hash_from('some/hashsearch'), ('some/hashsearch', None))
