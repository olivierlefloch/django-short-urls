# coding=utf-8

"""
This command extracts click data about urls
"""

from __future__ import unicode_literals

import csv

from django.core.management.base import BaseCommand
from django_short_urls.models import Link


# pylint: disable=E1101, W0201
class Command(BaseCommand):
    """Outputs a CSV with click data for all urls matching a prefix passed as an argument"""

    args = '<url_prefix url_prefix ...>'
    help = 'Outputs a CSV with click data for all urls matching a prefix passed as an argument'

    def handle(self, *url_prefixes, **options):
        self.writer = csv.writer(self.stdout)

        self.writer.writerow(['hash', 'long_url', 'nb_of_clicks'])

        for prefix in url_prefixes:
            for link in Link.find_for_prefix(prefix):
                self.writer.writerow([link.hash, link.long_url, link.clicks])
