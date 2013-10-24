# coding=utf-8

"""Models for the django short urls application"""

from __future__ import unicode_literals

from datetime import datetime
from django.conf import settings
from django.utils.log import getLogger
from hashlib import sha1
from mongoengine import Document, StringField, DateTimeField, IntField, BooleanField, ReferenceField
import re

import django_short_urls.int_to_alnum as int_to_alnum
from django_short_urls.exceptions import ForbiddenKeyword, ShortPathConflict


# pylint: disable=R0904, R0924, E1101
class User(Document):
    """Collection representing a user with access to the API"""

    meta = {
        'auto_create_index': settings.MONGO_AUTO_CREATE_INDEXES,
        'indexes': [('login',)]
    }

    login   = StringField(required=True, unique=True)
    api_key = StringField(required=True)
    email   = StringField(required=True)


class Link(Document):
    """Collection representing a shortened url"""

    meta = {
        'auto_create_index': settings.MONGO_AUTO_CREATE_INDEXES,
        # We can't used a "hashed" index on hash because it needs to be unique
        # Index on long_url is not listed because MongoEngine does not support hashed indexes, see db/schema.js!
        'indexes': [('hash',)]
    }

    hash                 = StringField(required=True, unique=True)
    long_url             = StringField(required=True)
    creator              = StringField(required=True)
    created_at           = DateTimeField(required=True)
    nb_tries_to_generate = IntField()
    act_as_proxy         = BooleanField()

    @classmethod
    def find_for_prefix(cls, prefix):
        """Retrieves all Link objects where the hash starts with a specific prefix"""
        if prefix:
            return cls.objects(hash__startswith=('%s/' % prefix))
        else:
            return cls.objects(hash__not__contains='/')

    @classmethod
    def shorten(cls, long_url, creator, short_path=None, prefix=None):
        """Public API to create a short link"""

        ForbiddenKeyword.raise_if_banned(short_path)
        ForbiddenKeyword.raise_if_banned(prefix)

        if prefix is None:
            prefix = ''

        if short_path is None or not len(short_path):
            link = cls.find_for_prefix(prefix).filter(long_url=long_url).first()

            if link is None:
                link = cls.create_with_random_short_path(long_url, prefix, creator)
        else:
            link, created = cls.__get_or_create(prefix, short_path, long_url, creator)

            if not created and link.long_url != long_url:
                raise ShortPathConflict(link)

        link.save()

        return link

    @classmethod
    def create_with_random_short_path(cls, long_url, prefix, creator):
        """Generate an unused, valid random short path for prefix"""
        nb_tries = 0

        while True:
            # Generate a seed from the long url and the current date (with milliseconds)
            seed   = "%s%s%s" % (long_url, datetime.utcnow(), nb_tries)
            hashed = int(sha1(seed).hexdigest(), 16)
            mod    = 1

            while hashed > mod:
                mod       *= 10
                nb_tries  += 1
                short_path = int_to_alnum.encode(hashed % mod)

                if not cls.is_valid_random_short_path(short_path):
                    continue

                link, created = cls.__get_or_create(prefix, short_path, long_url, creator)

                if created:
                    # Short path didn't exist, store number of tries and we're done
                    link.nb_tries_to_generate = nb_tries
                    return link

    RE_VALID_RANDOM_SHORT_PATHS = re.compile(r'^([a-z]{0,2}\d)+[a-z]{0,2}$')

    @classmethod
    def is_valid_random_short_path(cls, short_path):
        """Checks if the random short path is valid (does not contain words)"""
        # We don't check for ForbiddenKeywords because the constraints make that redundant
        return cls.RE_VALID_RANDOM_SHORT_PATHS.match(short_path) is not None

    @classmethod
    def __get_or_create(cls, prefix, short_path, long_url, creator):
        """Retrieves or Creates a Link object by (prefix, short_path)"""
        # pylint: disable=W0511
        # FIXME: Deprecated in MongoEngine 0.8 - https://work4labs.atlassian.net/browse/OPS-1529
        return cls.objects.get_or_create(
            hash=Link.hash_for_prefix_and_short_path(prefix, short_path),
            defaults={
                'long_url': long_url,
                'creator': creator,
                'created_at': datetime.utcnow()
            }
        )

    @classmethod
    def hash_for_prefix_and_short_path(cls, prefix, short_path):
        """Returns the hash for a combination of prefix and short_path"""
        return ('%s%s' % ('%s/' % prefix if prefix != '' else '', short_path)).lower()

    @classmethod
    def find_by_hash(cls, path):
        """Searches for a Link object by hash"""
        return cls.objects(hash=path.lower()).first()

    def build_relative_path(self):
        """Builds the relative path for the current url (since we only store the hash, we get a lowercase version)"""
        return '/%s' % self.hash

    def build_absolute_uri(self, request):
        """Builds the absolute url for the target link (including full server url)"""
        return request.build_absolute_uri(self.build_relative_path())

    def __str__(self):
        return "%s -> %s\n" % (self.hash, self.long_url)


class Click(Document):
    """Collection to store clicks, including url, time, ip, browser, etc."""

    meta = {
        'auto_create_index': settings.MONGO_AUTO_CREATE_INDEXES,
        'cascade': False,
        'indexes': [('full_path', 'created_at'), ('link', 'created_at')],
        'max_size': 100000000
    }

    server     = StringField(required=True)
    full_path  = StringField(required=True)
    # pylint: disable=W0511
    # TODO: Switch to using ObjectIds instead of DBRefs https://work4labs.atlassian.net/browse/OPS-1521
    link       = ReferenceField('Link', dbref=True)
    created_at = DateTimeField(required=True)
    ip         = StringField(required=True)
    browser    = StringField()
    referer    = StringField()
    lang       = StringField()

    def __unicode__(self):
        return "Click: (%s, %s, %s)" % (self.full_path, self.created_at, self.ip)

    def save(self, **kwargs):
        try:
            super(Click, self).save(**kwargs)
        # pylint: disable=W0703
        except Exception as err:
            getLogger('app').error('Failed to save %s with exception %s' % (self, err))

    @classmethod
    def register(cls, request, link):
        """Registers a click from request on link"""

        click = cls(
            server="%s:%s" % (request.META['SERVER_NAME'], request.META['SERVER_PORT']),
            full_path=request.get_full_path(),
            link=link,
            created_at=datetime.utcnow(),
            ip=request.META['REMOTE_ADDR'],
            browser=(
                ''.join([x if ord(x) < 128 else '?' for x in request.META['HTTP_USER_AGENT']])
                if 'HTTP_USER_AGENT' in request.META else None
            ),
            referer=request.META['HTTP_REFERER'] if 'HTTP_REFERER' in request.META else None,
            lang=request.META['HTTP_ACCEPT_LANGUAGE'] if 'HTTP_ACCEPT_LANGUAGE' in request else None
        )

        click.save()

        return click
