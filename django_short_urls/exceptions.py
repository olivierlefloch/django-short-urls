import re
from django.db.utils import DatabaseError


# FIXME: Move to a dedicated ServiceUnavailable app
class DatabaseWriteDenied(DatabaseError):
    pass


class ForbiddenKeyword(Exception):
    ban_words = (
        'admin', 'refer', 'share', 'settings', 'jobs', 'careers', 'apply',
        'mobile', 'signup', 'login', 'register', 'install', 'recruiter', 'search',
        'network', 'career', 'register', 'signin', 'password', 'welcome'
    )
    ban_regex = re.compile(r'^(%s)$' % ('|'.join(ban_words)))

    @classmethod
    def is_banned(cls, keyword):
        return keyword is not None and cls.ban_regex.match(keyword.lower())

    @classmethod
    def raise_if_banned(cls, keyword):
        if cls.is_banned(keyword):
            raise cls(keyword)

    def __init__(self, keyword):
        self.keyword = keyword

    def __str__(self):
        return 'Keyword "%s" cannot be used as a short path or a prefix.' % self.keyword


class ShortPathConflict(Exception):
    def __init__(self, link):
        self.link = link

    def __str__(self):
        return 'Hash "%s" has already been bound.' % self.link.hash
