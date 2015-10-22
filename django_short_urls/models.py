# coding=utf-8

"""Models for the django short urls application"""

from __future__ import unicode_literals

from datetime import datetime
from django.conf import settings
from hashlib import sha1
from mongoengine import Document, StringField, IntField, BooleanField
import re
from statsd import statsd

import django_short_urls.int_to_alnum as int_to_alnum
from django_short_urls.exceptions import PathIsNotUrlSafe, ForbiddenKeyword, ShortPathConflict


# pylint: disable=R0904, E1101
class User(Document):
    """Collection representing a user with access to the API"""

    meta = {
        'auto_create_index': settings.MONGO_AUTO_CREATE_INDEXES,
        'indexes': [('login',)]
    }

    login = StringField(required=True, unique=True)
    api_key = StringField(required=True)
    email = StringField(required=True)


class Link(Document):
    """Collection representing a shortened url"""

    long_url_index_spec = [('long_url', 'hashed')]

    meta = {
        'auto_create_index': settings.MONGO_AUTO_CREATE_INDEXES,
        # We can't used a "hashed" index on hash because it needs to be unique
        'indexes': [('hash',), long_url_index_spec]
    }

    hash = StringField(required=True, unique=True)
    long_url = StringField(required=True)
    act_as_proxy = BooleanField()
    clicks = IntField(default=0)

    @classmethod
    def find_for_prefix(cls, prefix):
        """Retrieves all Link objects where the hash starts with a specific prefix
           If you do not give a prefix (or prefix='') this is not going to be indexed,
           so make sure you filter on another field that is actually indexed.
        """
        if prefix:
            return cls.objects(hash__startswith=('%s/' % prefix.lower()))
        else:
            return cls.objects(hash__not__contains='/')

    @classmethod
    def find_for_prefix_and_long_url(cls, prefix, long_url):
        """Retrieves Link objects for a specific long_url that also match a specific prefix"""
        # For some reason, we need to hint explictly at the index to use
        return cls.find_for_prefix(prefix).filter(long_url=long_url).hint(cls.long_url_index_spec)

    @classmethod
    def shorten(cls, long_url, short_path=None, prefix=None):
        """Public API to create a short link"""

        if prefix is None:
            prefix = ''
        else:
            ForbiddenKeyword.raise_if_banned(prefix)
            PathIsNotUrlSafe.raise_if_unsafe(prefix)

        if short_path is None or not len(short_path):
            link = cls.find_for_prefix_and_long_url(prefix, long_url).first()

            if link is None:
                link = cls.create_with_random_short_path(long_url, prefix)
        else:
            PathIsNotUrlSafe.raise_if_unsafe(short_path)
            ForbiddenKeyword.raise_if_banned(short_path)

            link, created = cls.__get_or_create(prefix, short_path, long_url)

            if not created and link.long_url != long_url:
                raise ShortPathConflict(link)

        link.save()

        return link

    @classmethod
    def create_with_random_short_path(cls, long_url, prefix):
        """Generate an unused, valid random short path for prefix"""
        nb_tries = 0

        while True:
            # Generate a seed from the long url and the current date (with milliseconds)
            seed = "%s%s%s" % (long_url, datetime.utcnow(), nb_tries)
            hashed = int(sha1(seed).hexdigest(), 16)
            mod = 1

            while hashed > mod:
                mod *= 10
                nb_tries += 1
                short_path = int_to_alnum.encode(hashed % mod)

                if not cls.is_valid_random_short_path(short_path):
                    continue

                link, created = cls.__get_or_create(prefix, short_path, long_url)

                if created:
                    # Short path didn't exist, store number of tries and we're done
                    statsd.histogram('workforus.nb_tries_to_generate', nb_tries, tags=['prefix:' + prefix])
                    return link

    RE_VALID_RANDOM_SHORT_PATHS = re.compile(r'^([a-z]{0,2}\d)+[a-z]{0,2}$')

    @classmethod
    def is_valid_random_short_path(cls, short_path):
        """Checks if the random short path is valid (does not contain words)"""
        # We don't check for ForbiddenKeywords because the constraints make that redundant
        return cls.RE_VALID_RANDOM_SHORT_PATHS.match(short_path) is not None

    @classmethod
    def __get_or_create(cls, prefix, short_path, long_url):
        """Retrieves or Creates a Link object by (prefix, short_path)"""
        # pylint: disable=W0511
        # FIXME: Deprecated in MongoEngine 0.8 - https://work4labs.atlassian.net/browse/OPS-1529
        return cls.objects.get_or_create(
            hash=Link.hash_for_prefix_and_short_path(prefix, short_path),
            defaults={'long_url': long_url}
        )

    @classmethod
    def hash_for_prefix_and_short_path(cls, prefix, short_path):
        """Returns the hash for a combination of prefix and short_path"""
        return ('%s%s' % ('%s/' % prefix if prefix != '' else '', short_path)).lower()

    @classmethod
    def find_by_hash(cls, path):
        """Searches for a Link object by hash"""
        return cls.objects(hash=path.lower()).first()

    @property
    def prefix(self):
        """If present, return the prefix"""
        if '/' not in self.hash:
            return ''

        return self.hash.split('/')[0]

    def click(self):
        """Register a click on this link"""
        self.__class__.objects(hash=self.hash).update_one(inc__clicks=1)

    def build_relative_path(self):
        """Builds the relative path for the current url (since we only store the hash, we get a lowercase version)"""
        return '/%s' % self.hash

    def build_absolute_uri(self, request):
        """Builds the absolute url HTTPs for the target link (including full server url)"""
        url = request.build_absolute_uri(self.build_relative_path())
        _, url = url.split('://')  # Strip protocol
        return "https://" + url

    def __str__(self):
        return "%s -> %s\n" % (self.hash, self.long_url)
