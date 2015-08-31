# coding=utf-8

from __future__ import unicode_literals

from django_app.test import PyW4CTestCase

from django_short_urls.suffix_catchall import get_hash_from


class ValidRedirectPathTestCase(PyW4CTestCase):
    def test__get_hash_from(self):
        self.assertEqual(get_hash_from('azertyuiop'), ('azertyuiop', None))
        self.assertEqual(get_hash_from('azerty/uiop'), ('azerty/uiop', None))
        self.assertEqual(get_hash_from('a/z/e/r/t/y/u/i/o/p'), ('a/z/e/r/t/y/u/i/o/p', None))

        self.assertEqual(get_hash_from('some/hash/referrals'), ('some/hash', 'referrals'))
        self.assertEqual(get_hash_from('some/hash/recruiter'), ('some/hash', 'recruiter'))
        self.assertEqual(get_hash_from('some/hash/share'), ('some/hash', 'share'))
        self.assertEqual(get_hash_from('some/hash/search'), ('some/hash', 'search'))

        self.assertEqual(get_hash_from('some/hashreferrals'), ('some/hashreferrals', None))
        self.assertEqual(get_hash_from('some/hashrecruiter'), ('some/hashrecruiter', None))
        self.assertEqual(get_hash_from('some/hashshare'), ('some/hashshare', None))
        self.assertEqual(get_hash_from('some/hashsearch'), ('some/hashsearch', None))
