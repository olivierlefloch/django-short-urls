# coding=utf-8

"""Shared exceptions for the Django Short Urls application"""

from __future__ import unicode_literals

import re
from django.db.utils import DatabaseError


# pylint: disable=W0511
# TODO: Move to a dedicated ServiceUnavailable app
class DatabaseWriteDenied(DatabaseError):
    """Exception raised when attempting to write to the database when in readonly mode"""
    pass


class ForbiddenKeyword(Exception):
    """Exception raised when attempting to shorten a link containing an reserved keyword"""

    ban_words = (
        'admin', 'refer', 'share', 'settings', 'jobs', 'careers', 'apply',
        'mobile', 'signup', 'login', 'register', 'install', 'recruiter', 'search',
        'network', 'career', 'register', 'signin', 'password', 'welcome'
    )
    ban_regex = re.compile(r'^(%s)$' % ('|'.join(ban_words)))

    @classmethod
    def is_banned(cls, keyword):
        """Returns true if the keyword is reserved"""

        return keyword is not None and cls.ban_regex.match(keyword.lower())

    @classmethod
    def raise_if_banned(cls, keyword):
        """Raises a ForbiddenKeyword exception if the keyword is reserved"""

        if cls.is_banned(keyword):
            raise cls(keyword)

    def __init__(self, keyword):
        super(ForbiddenKeyword, self).__init__()

        self.keyword = keyword

    def __str__(self):
        return 'Keyword "%s" cannot be used as a short path or a prefix.' % self.keyword


class ShortPathConflict(Exception):
    """Raised when attempting to reuse an existing short link with a different long_url"""

    def __init__(self, link):
        super(ShortPathConflict, self).__init__()

        self.link = link

    def __str__(self):
        return 'Hash "%s" has already been bound.' % self.link.hash
