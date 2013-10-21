# coding=utf-8

from __future__ import unicode_literals

import io

from django.core import management
from django.test import TestCase

from django_short_urls.models import Link


class UrlStatsTestCase(TestCase):
    def test_generate_args_output(self):
        prefix = 'work4'

        # Generate a link that won't appear in the results (wrong prefix)
        Link.shorten(long_url='http://www.work4labs.com', creator='olefloch', prefix='work4labs').save()
        # Generate the link that will be used in the output
        link = Link.shorten(long_url='http://www.work4labs.com', creator='olefloch', prefix=prefix).save()

        header_row = 'short_url,long_url,nb_of_clicks,list_of_dates'
        first_row = '%s,%s,0,' % (link.hash, link.long_url)

        with io.BytesIO() as stdout, io.BytesIO() as stderr:
            management.call_command('urlstats', prefix, stdout=stdout, stderr=stderr)

            stdout.seek(0)
            stderr.seek(0)

            self.assertEqual(stderr.read(), '')
            self.assertEqual(stdout.read(), '%s\r\n%s\r\n' % (header_row, first_row))
