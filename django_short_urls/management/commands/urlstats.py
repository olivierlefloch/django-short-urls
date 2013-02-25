from django.core.management.base import BaseCommand, CommandError
from django_short_urls.models import Click, Link

class Command(BaseCommand):
    args = '<url_prefix url_prefix ...>'
    help = 'Outputs a CSV with click data for all urls matching a prefix passed as an argument'

    def handle(self, *url_prefixes, **options):
        self.stdout.write(repr(url_prefixes) + "\n")
