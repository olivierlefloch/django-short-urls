from datetime import datetime
from hashlib import sha1
from mongoengine import *

import int_to_alnum

class User(Document):
    login = StringField(required=True, unique=True)
    api_key = StringField(required=True)
    email = StringField(required=True)

class ShortPathConflict(Exception):
    def __init__(self, short_path):
        self.short_path = short_path

    def __str__(self):
        return 'Short path "%s" has already been bound.' % self.short_path

class Link(Document):
    # FIXME: Add unit tests - WFU-1527

    short_path = StringField(required=True)
    short_path_to_lower = StringField(required=True, unique=True)
    long_url = StringField(required=True)
    creator = StringField(required=True)
    created_at = DateTimeField(required=True)

    def __init__(self, *args, **kwargs):
        super(Link, self).__init__(*args, **kwargs)

        if self.short_path_to_lower is None:
            self.short_path_to_lower = self.short_path.lower()

    @classmethod
    def shorten(cls, long_url, short_path=None, prefix=None, creator=None):
        if short_path is None:
            if prefix is not None:
                raise NotImplementedError

            # Generate a seed from the long url and the current date
            seed = long_url + str(datetime.utcnow())

            link = None

            while link is None:
                hashed = int(sha1(seed).hexdigest(), 16)
                mod    = 1

                while hashed > mod:
                    mod *= 10
                    short_path = int_to_alnum.encode(hashed % mod)

                    link, created = cls.__get_or_create(short_path, long_url, creator)

                    if created:
                        # Short path didn't exist, we're done
                        break
                    else:
                        # Short path was already used, forget this link
                        link = None

                # Try again with a space appended to seed
                seed += ' '
        else:
            link, created = cls.__get_or_create(short_path, long_url, creator)

            if not created and link.long_url != long_url:
                raise ShortPathConflict(short_path)

        link.save()

        return link

    @classmethod
    def __get_or_create(cls, short_path, long_url, creator):
        return cls.objects.get_or_create(
            short_path=short_path,
            defaults={
                'long_url': long_url,
                'creator': creator,
                'created_at': datetime.utcnow()})

    @classmethod
    def find_by_short_path(cls, short_path):
        """Return Link with matching short path (ignores case)"""

        return cls.objects(short_path_to_lower=short_path.lower()).first()

    def __str__(self):
        return "%s -> %s\n" % (self.short_path, self.long_url)
