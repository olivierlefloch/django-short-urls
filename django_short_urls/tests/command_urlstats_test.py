# coding=utf-8

from __future__ import unicode_literals

import io

from django.core import management
from mock import patch

from django_app.test import PyW4CTestCase

from django_short_urls.models import Link


class UrlStatsTestCase(PyW4CTestCase):
    @patch('django_short_urls.models.statsd')
    def test_generate_args_output(self, mock_statsd):  # pylint: disable=unused-argument
        prefix = 'work4'

        # Generate a link that won't appear in the results (wrong prefix)
        Link.shorten(long_url='http://www.work4labs.com', prefix='work4labs').save()
        # Generate the link that will be used in the output
        link = Link.shorten(long_url='http://www.work4labs.com', prefix=prefix).save()

        header_row = 'hash,long_url,nb_of_clicks'
        first_row = '%s,%s,0' % (link.hash, link.long_url)

        with io.BytesIO() as stdout, io.BytesIO() as stderr:
            management.call_command('urlstats', prefix, stdout=stdout, stderr=stderr)

            stdout.seek(0)
            stderr.seek(0)

            self.assertEqual(stderr.read(), '')
            self.assertEqual(stdout.read(), '%s\r\n%s\r\n' % (header_row, first_row))
