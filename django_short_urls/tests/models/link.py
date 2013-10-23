# coding=utf-8

from __future__ import unicode_literals

from django.test import TestCase
from freezegun import freeze_time

from django_short_urls.models import Link


class LinkTestCase(TestCase):
    def test_valid_short_path(self):
        self.assertEqual(Link.is_valid_random_short_path("ab2cd"), True)
        self.assertEqual(Link.is_valid_random_short_path("ab2"), True)
        self.assertEqual(Link.is_valid_random_short_path("a234r434g43gb32r"), True)
        self.assertEqual(Link.is_valid_random_short_path("4a"), True)

        self.assertEqual(Link.is_valid_random_short_path("abcd"), False)
        self.assertEqual(Link.is_valid_random_short_path("ge"), False)
        self.assertEqual(Link.is_valid_random_short_path("crap"), False)
        self.assertEqual(Link.is_valid_random_short_path("crap42"), False)
        self.assertEqual(Link.is_valid_random_short_path("abe4abe"), False)

    def test_shorten(self):
        link = Link.shorten("http://www.work4labs.com/", 'olefloch')

        self.assertTrue('work4labs' in str(link))

        self.assertFalse('/' in link.hash)
        self.assertEqual(link.creator, 'olefloch')

    def test_shorten_multiple(self):
        # Generate a couple of links that we should *not* fall on
        Link.shorten("http://www.work4labs.com/", 'olefloch', prefix='foobarblah')
        Link.shorten("http://www.work4labs.com/", 'olefloch', prefix='fooba')

        link1 = Link.shorten("http://www.work4labs.com/", 'olefloch', prefix='foobar')
        self.assertTrue('foobar/' in link1.hash)
        # Check that we get the same link, not one of the false positives
        self.assertTrue(Link.shorten("http://www.work4labs.com/", 'olefloch', prefix='foobar').hash, link1.hash)

    def test_shorten_with_short_path(self):
        link = Link.shorten("http://www.work4labs.com/", 'olefloch', short_path='FooBar')
        self.assertEqual(link.hash, 'foobar')

    # Make this test deterministic
    @freeze_time('2013-05-29')
    def test_create_random(self):
        link1 = Link.create_with_random_short_path('http://work4labs.com/', 'foo', 'olefloch')

        self.assertEqual(link1.creator, 'olefloch')

        # pylint: disable=W0612
        for iteration in xrange(1, 10):
            # We loop 10 times in hopes of encountering an invalid short path
            Link.create_with_random_short_path('http://work4labs.com/', 'foo', 'olefloch')
