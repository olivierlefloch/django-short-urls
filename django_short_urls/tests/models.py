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

        self.assertEqual(link.prefix, '')
        self.assertEqual(link.creator, 'olefloch')

        self.assertEqual(Link.shorten("http://www.work4labs.com/", 'olefloch', prefix='foobar').prefix, 'foobar')
        # Check that we get the same link
        self.assertEqual(Link.shorten("http://www.work4labs.com/", 'olefloch', prefix='foobar').prefix, 'foobar')

        link = Link.shorten("http://www.work4labs.com/", 'olefloch', short_path='FooBar')
        self.assertEqual(link.short_path, 'FooBar')
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
