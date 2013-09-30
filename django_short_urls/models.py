from datetime import datetime
from django.conf import settings
from hashlib import sha1
from mongoengine import *
import re

import int_to_alnum
import suffix_catchall
from exceptions import ForbiddenKeyword, ShortPathConflict

class User(Document):
    meta = {
        'allow_inheritance': False,
        'auto_create_index': settings.MONGO_AUTO_CREATE_INDEXES,
        'indexes': [('login',)]
    }

    login   = StringField(required=True, unique=True)
    api_key = StringField(required=True)
    email   = StringField(required=True)

class Link(Document):
    # FIXME: Add unit tests - WFU-1527

    meta = {
        'allow_inheritance': False,
        'auto_create_index': settings.MONGO_AUTO_CREATE_INDEXES,
        'indexes': [('prefix', 'long_url'), ('hash',)]
    }

    hash       = StringField(required=True, unique=True)
    prefix     = StringField(required=True)
    short_path = StringField(required=True)
    long_url   = StringField(required=True)
    creator    = StringField(required=True)
    created_at = DateTimeField(required=True)
    nb_tries_to_generate = IntField()
    act_as_proxy = BooleanField()

    @classmethod
    def shorten(cls, long_url, creator, short_path=None, prefix=None):
        # This intermediate public method hides the private _ignore_bans parameter
        return cls.__shorten(long_url=long_url, creator=creator, short_path=short_path, prefix=prefix)

    @classmethod
    def __shorten(cls, long_url, creator, _ignore_bans=False, short_path=None, prefix=None):
        if not _ignore_bans:
            ForbiddenKeyword.raise_if_banned(short_path)
            ForbiddenKeyword.raise_if_banned(prefix)

        if prefix is None:
            prefix = ''

        if short_path is None or not len(short_path):
            link = cls.objects(long_url=long_url, prefix=prefix).first()

            if link is None:
                link = cls.__create_with_random_short_path(long_url, prefix, creator)
        else:
            link, created = cls.__get_or_create(prefix, short_path, long_url, creator)

            if not created and link.long_url != long_url:
                raise ShortPathConflict(link)

        link.save()

        return link

    @classmethod
    def __create_with_random_short_path(cls, long_url, prefix, creator):
        while True:
            # Generate a seed from the long url and the current date (with milliseconds)
            seed     = long_url + str(datetime.utcnow())
            hashed   = int(sha1(seed).hexdigest(), 16)
            mod      = 1
            nb_tries = 0

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
        # We don't check for ForbiddenKeywords because the constraints make that redundant
        return cls.RE_VALID_RANDOM_SHORT_PATHS.match(short_path) is not None

    @classmethod
    def __get_or_create(cls, prefix, short_path, long_url, creator):
        return cls.objects.get_or_create(
            hash=Link.hash_for_prefix_and_short_path(prefix, short_path),
            defaults={
                'short_path': short_path,
                'prefix': prefix,
                'long_url': long_url,
                'creator': creator,
                'created_at': datetime.utcnow()})

    @classmethod
    def hash_for_prefix_and_short_path(cls, prefix, short_path):
        return ('%s%s' % ('%s/' % prefix if prefix != '' else '', short_path)).lower()

    @classmethod
    def find_by_hash(cls, path):
        return cls.objects(hash=path.lower()).first()

    def build_relative_path(self):
        return ('/%s/%%s' % self.prefix if self.prefix else '/%s') % self.short_path

    def build_absolute_uri(self, request):
        return request.build_absolute_uri(self.build_relative_path())

    def __str__(self):
        return "%s -> %s\n" % (self.hash, self.long_url)

class Click(Document):
    meta = {
        'allow_inheritance': False,
        'auto_create_index': settings.MONGO_AUTO_CREATE_INDEXES,
        'cascade': False,
        'indexes': [('full_path', 'created_at'), ('link', 'created_at')],
        'max_size': '97557560'
    }

    server     = StringField(required=True)
    full_path  = StringField(required=True)
    # FIXME: Switch to using strings as dbrefs http://mongoengine-odm.readthedocs.org/en/latest/upgrade.html#referencefields
    link       = ReferenceField('Link', dbref=True)
    created_at = DateTimeField(required=True)
    ip         = StringField(required=True)
    browser    = StringField()
    referer    = StringField()
    lang       = StringField()
