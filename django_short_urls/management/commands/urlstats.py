import csv

from django.core.management.base import BaseCommand, CommandError
from django_short_urls.models import Click, Link

class Command(BaseCommand):
    args = '<url_prefix url_prefix ...>'
    help = 'Outputs a CSV with click data for all urls matching a prefix passed as an argument'

    def handle(self, *url_prefixes, **options):
        self.writer = csv.writer(self.stdout)

        self.writer.writerow(['short_url', 'long_url', 'nb_of_clicks', 'list_of_dates'])

        for prefix in url_prefixes:
            for link in Link.objects(prefix=prefix):
                self.write_stats_for_link(link)

    def write_stats_for_link(self, link):
        clicks = Click.objects(link=link)

        self.writer.writerow([
            link.hash, link.long_url, len(clicks),
            ";".join([click.created_at.strftime('%Y-%m-%d %H:%M:%S') for click in clicks])
        ])
