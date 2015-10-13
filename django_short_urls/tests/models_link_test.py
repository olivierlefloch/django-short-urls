# coding=utf-8

from __future__ import unicode_literals

from django_app.test import PyW4CTestCase
from freezegun import freeze_time
from mock import patch

from django_short_urls.models import Link


def _shorten(*args, **kwargs):
    with patch('django_short_urls.models.statsd') as mock_statsd:
        return Link.shorten(*args, **kwargs), mock_statsd


class LinkTestCase(PyW4CTestCase):
    URL = "http://www.work4labs.com/"

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
        link, _ = _shorten("http://www.work4labs.com/")

        self.assertIn('work4labs', str(link))

        self.assertNotIn('/', link.hash)

    def test_shorten_multiple(self):
        # Generate a couple of links that we should *not* fall on
        _shorten("http://www.work4labs.com/", prefix='foobarblah')
        _shorten("http://www.work4labs.com/", prefix='fooba')

        link1, _ = _shorten("http://www.work4labs.com/", prefix='foobar')
        self.assertIn('foobar/', link1.hash)

    def test_shorten_with_short_path(self):
        link, _ = _shorten("http://www.work4labs.com/", short_path='FooBar')
        self.assertEqual(link.hash, 'foobar')

    def _shorten_twice(self, expected_statsd_call_count=1, **kwargs):
        kwargs['long_url'] = "http://www.work4labs.com/"

        link1, mock_statsd = _shorten(**kwargs)
        self.assertEqual(len(mock_statsd.mock_calls), expected_statsd_call_count)

        link2, mock_statsd = _shorten(**kwargs)
        # statsd.histogram should only be called once, at creation
        self.assertEqual(len(mock_statsd.mock_calls), 0)

        self.assertEqual(link1.hash, link2.hash)

    def test_shorten_twice_no_prefix(self):
        self._shorten_twice()

    def test_shorten_twice_with_prefix(self):
        self._shorten_twice(prefix="olefloch")
        self._shorten_twice(prefix="FooBar")

    def test_shorten2_with_short_path(self):
        # We expect statsd.histogram to not be called since we don't need to
        # generate a random short path
        self._shorten_twice(short_path="youpitralala", expected_statsd_call_count=0)

    def find_for_prefix(self, prefix):
        # First check that there are no links for this prefix
        self.assertEqual(len(Link.find_for_prefix(prefix)), 0)

        # Create a link with this prefix and another with another prefix
        true_link, _ = _shorten("http://www.work4labs.com/", prefix=prefix)

        # other link
        _shorten("http://www.work4labs.com/", prefix='other_%s' % prefix)

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

        _shorten(long_url, prefix=prefix)

        explanation = Link.find_for_prefix_and_long_url(prefix, long_url).explain(False)

        if 'cursor' in explanation:  # pragma: no cover
            # Mongo 2.x
            explanation_item = explanation['cursor']
            match = u'BtreeCursor long_url_hashed'
        else:  # pragma: no cover
            explanation_item = explanation['queryPlanner']['winningPlan']['inputStage']['inputStage']['keyPattern']
            match = {'long_url': 'hashed'}

        self.assertEqual(explanation_item, match)

    # Freeze time to make this test deterministic
    @freeze_time('2013-05-29')
    @patch('django_short_urls.models.statsd')
    def test_create_random(self, mock_statsd):  # pylint: disable=unused-argument
        link1 = Link.create_with_random_short_path(self.URL, 'foo')

        self.assertEqual(link1.long_url, self.URL)

        # pylint: disable=W0612
        for _ in xrange(1, 10):
            # We loop 10 times in hopes of encountering an invalid short path
            Link.create_with_random_short_path(self.URL, 'foo')

    def test_prefix(self):
        link, _ = _shorten(self.URL)
        self.assertEqual(link.prefix, '')

        prefix = 'foo'
        link, _ = _shorten(self.URL, prefix=prefix)
        self.assertEqual(link.prefix, prefix)
