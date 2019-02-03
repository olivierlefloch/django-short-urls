# coding=utf-8

from __future__ import unicode_literals

from django.test import RequestFactory
from freezegun import freeze_time
from mock import call, Mock, patch

from django_app.test import PyW4CTestCase

from django_short_urls.models import Link


def _shorten(*args, **kwargs):
    with patch('django_short_urls.models.statsd') as mock_statsd:
        return Link.shorten(*args, **kwargs), mock_statsd


class LinkTestCase(PyW4CTestCase):
    URL = "http://www.work4labs.com/"

    def test_valid_short_path(self):
        self.assertTrue(Link._is_valid_random_short_path("ab2cd"))
        self.assertTrue(Link._is_valid_random_short_path("ab2"))
        self.assertTrue(Link._is_valid_random_short_path("a234r434g43gb32r"))
        self.assertTrue(Link._is_valid_random_short_path("4a"))
        self.assertTrue(Link._is_valid_random_short_path("ge"))
        self.assertTrue(Link._is_valid_random_short_path("42"))
        self.assertTrue(Link._is_valid_random_short_path("j"))

        self.assertFalse(Link._is_valid_random_short_path("42abcd"), 'More than 2 consecutive letters')
        self.assertFalse(Link._is_valid_random_short_path("crap"), 'More than 2 consecutive letters')
        self.assertFalse(Link._is_valid_random_short_path("crap42"), 'More than 2 consecutive letters')
        self.assertFalse(Link._is_valid_random_short_path("abe4abe"), 'More than 2 consecutive letters')
        self.assertFalse(Link._is_valid_random_short_path("Jo42"), 'Uppercase used')

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
            self.assertEqual(
                explanation['cursor'],
                u'BtreeCursor long_url_hashed')
        else:  # pragma: no cover
            self.assertEqual(explanation['queryPlanner']['winningPlan']['inputStage']['indexName'], 'long_url_hashed')

    # Freeze time to make this test deterministic
    @freeze_time('2013-05-29')
    @patch('django_short_urls.models.statsd.histogram')
    def test_create_random(self, mock_histogram):
        self.assertEqual(
            Link.create_with_random_short_path(self.URL, 'foo').long_url,
            self.URL)
        mock_histogram.assert_called_once_with('workforus.nb_tries_to_generate', 1, tags=['prefix:foo'])

    @freeze_time('2013-05-07')
    @patch('django_short_urls.models.statsd.histogram')
    @patch('django_short_urls.models.Link._is_valid_random_short_path', side_effect=[False, True])
    def test_create_random_is_invalid(self, mock_is_valid, mock_histogram):
        """Check that we try a second time if we randomly generate an invalid hash, and that we count tries properly"""
        self.assertEqual(Link.create_with_random_short_path(self.URL, 'foo').long_url, self.URL)
        self.assertEqual(mock_is_valid.call_count, 2)
        mock_histogram.assert_called_once_with('workforus.nb_tries_to_generate', 2, tags=['prefix:foo'])

    @freeze_time('2013-05-07')
    @patch('django_short_urls.models.statsd.histogram')
    @patch('django_short_urls.models.sha1', return_value=Mock(hexdigest=Mock(side_effect=['0', '123245'])))
    def test_create_random_hash_overflow(self, mock_sha1, mock_histogram):
        """Check that we generate a new hash if we exceed the length of the current hash"""
        self.assertEqual(Link.create_with_random_short_path(self.URL, 'foo').long_url, self.URL)

        self.assertEqual(mock_sha1.call_count, 2)
        mock_histogram.assert_has_calls([call('workforus.nb_tries_to_generate', 1, tags=['prefix:foo'])])

    @freeze_time('2013-05-07')
    @patch('django_short_urls.models.statsd.histogram')
    @patch('django_short_urls.models.sha1', return_value=Mock(hexdigest=Mock(return_value='123456789')))
    def test_create_random_hash_conflict(self, mock_sha1, mock_histogram):
        """Check that we try again if we encounter hash conflicts"""
        link1 = Link.create_with_random_short_path(self.URL, 'foo')
        url2 = self.URL + '?foo'
        link2 = Link.create_with_random_short_path(url2, 'foo')

        self.assertEqual(link1.long_url, self.URL)
        self.assertEqual(link1.hash, 'foo/5')
        self.assertEqual(link2.long_url, url2)
        self.assertEqual(link2.hash, 'foo/19')

        self.assertEqual(mock_sha1.call_count, 2)
        mock_histogram.assert_has_calls([
            # First link gets generated in 1 try
            call('workforus.nb_tries_to_generate', 1, tags=['prefix:foo']),
            # Second one needs 2 tries
            call('workforus.nb_tries_to_generate', 2, tags=['prefix:foo'])
        ])

    def test_prefix(self):
        link, _ = _shorten(self.URL)
        self.assertEqual(link.prefix, '')

        prefix = 'foo'
        link, _ = _shorten(self.URL, prefix=prefix)
        self.assertEqual(link.prefix, prefix)

    def test_build_absolute_uri(self):
        link, _ = _shorten("http://www.work4labs.com/", short_path='foo')

        self.assertEqual(
            link.build_absolute_uri(RequestFactory().get('/test')),
            "https://testserver/foo"
        )
