from django.utils import unittest

from django_short_urls.suffix_catchall import get_hash_from


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
