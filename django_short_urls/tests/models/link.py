# coding=utf-8

from __future__ import unicode_literals

from django_app.mongo_test_case import MongoTestCase
from freezegun import freeze_time

from django_short_urls.models import Link


class LinkTestCase(MongoTestCase):
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

        self.assertIn('work4labs', str(link))

        self.assertNotIn('/', link.hash)
        self.assertEqual(link.creator, 'olefloch')

    def test_shorten_multiple(self):
        # Generate a couple of links that we should *not* fall on
        Link.shorten("http://www.work4labs.com/", 'olefloch', prefix='foobarblah')
        Link.shorten("http://www.work4labs.com/", 'olefloch', prefix='fooba')

        link1 = Link.shorten("http://www.work4labs.com/", 'olefloch', prefix='foobar')
        self.assertIn('foobar/', link1.hash)

    def test_shorten_with_short_path(self):
        link = Link.shorten("http://www.work4labs.com/", 'olefloch', short_path='FooBar')
        self.assertEqual(link.hash, 'foobar')

    def shorten_twice(self, **kwargs):
        link1 = Link.shorten("http://www.work4labs.com/", 'olefloch', **kwargs)
        link2 = Link.shorten("http://www.work4labs.com/", 'olefloch', **kwargs)
        self.assertEqual(link1.hash, link2.hash)

    def test_shorten_twice_no_prefix(self):
        self.shorten_twice()

    def test_shorten_twice_with_prefix(self):
        self.shorten_twice(prefix="olefloch")

    def test_shorten2_with_short_path(self):
        self.shorten_twice(short_path="youpitralala")

    def find_for_prefix(self, prefix):
        # First check that there are no links for this prefix
        self.assertEqual(len(Link.find_for_prefix(prefix)), 0)

        # Create a link with this prefix and another with another prefix
        true_link = Link.shorten("http://www.work4labs.com/", 'olefloch', prefix=prefix)

        # other link
        Link.shorten("http://www.work4labs.com/", 'olefloch', prefix='other_%s' % prefix)

        # We should only find the true link
        links = Link.find_for_prefix(prefix)

        self.assertEqual(len(links), 1)
        self.assertEqual(links.first().hash, true_link.hash)

    def test_find_for_prefix_no_prefix(self):
        # Not sure we actually want to allow this to be possible
        # Probably raising an error in this case would be best
        # or it could return cls.objects (but it is not correct though)
        self.find_for_prefix('')

    def test_prefix_with_prefix(self):
        self.find_for_prefix('toto')

    def test_find_for_p_and_l_u(self):
        prefix = 'ole'
        long_url = "http://www.work4labs.com/"

        Link.shorten(long_url, 'olefloch', prefix=prefix)

        self.assertEqual(
            Link.find_for_prefix_and_long_url(prefix, long_url).explain()['cursor'],
            u'BtreeCursor long_url_hashed'
        )

    # Freeze time to make this test deterministic
    @freeze_time('2013-05-29')
    def test_create_random(self):
        link1 = Link.create_with_random_short_path('http://work4labs.com/', 'foo', 'olefloch')

        self.assertEqual(link1.creator, 'olefloch')

        # pylint: disable=W0612
        for iteration in xrange(1, 10):
            # We loop 10 times in hopes of encountering an invalid short path
            Link.create_with_random_short_path('http://work4labs.com/', 'foo', 'olefloch')
