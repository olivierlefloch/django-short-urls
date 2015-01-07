# coding=utf-8

"""Shared exceptions for the Django Short Urls application"""

from __future__ import unicode_literals

import re

from .w4l_http import URL_SAFE_FOR_PATH


class InvalidHashException(Exception):
    """An exception that can store the invalid hash"""

    def __init__(self, hash_):
        super(InvalidHashException, self).__init__()

        self.hash = hash_

    def __str__(self):
        return self.MESSAGE_TEMPLATE % self.hash


class PathIsNotUrlSafe(InvalidHashException):
    """Exception raised when attempting to use a hash that is not url safe"""

    IS_URL_SAFE_RE = re.compile(r'^[%s]*$' % URL_SAFE_FOR_PATH)

    MESSAGE_TEMPLATE = '"%s" contains unsafe characters'

    @classmethod
    def raise_if_unsafe(cls, short_url):
        """Raises a PathIsNotUrlSafe exception if the hash is not valid"""

        if cls.IS_URL_SAFE_RE.match(short_url) is None:
            raise cls(short_url)


class ForbiddenKeyword(InvalidHashException):
    """Exception raised when attempting to shorten a link containing an reserved keyword"""

    BAN_REGEX = re.compile(r'^(%s)$' % ('|'.join((
        'admin', 'refer', 'share', 'settings', 'jobs', 'careers', 'apply',
        'mobile', 'signup', 'login', 'register', 'install', 'recruiter', 'search',
        'network', 'career', 'register', 'signin', 'password', 'welcome'
    ))))

    MESSAGE_TEMPLATE = 'Keyword "%s" cannot be used as a short path or a prefix.'

    @classmethod
    def raise_if_banned(cls, keyword):
        """Raises a ForbiddenKeyword exception if the keyword is reserved"""

        if keyword is not None and cls.BAN_REGEX.match(keyword.lower()):
            raise cls(keyword)


class ShortPathConflict(InvalidHashException):
    """Raised when attempting to reuse an existing short link with a different long_url"""

    MESSAGE_TEMPLATE = 'Hash "%s" has already been bound.'

    def __init__(self, link):
        super(ShortPathConflict, self).__init__(link.hash)

        self.link = link
