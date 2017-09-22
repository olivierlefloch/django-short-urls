# coding: utf-8

"""
Django test case that doesn't allow networking
"""

from __future__ import unicode_literals

import re
import socket
from unittest import TestCase

from utils.reflect import caller_qualname


class NetworkError(Exception):
    """Exception thrown when you try to use the network (that's bad!)"""
    pass


class NoNetworkTestCase(TestCase):
    """
    TestCase class that prevents networking requests from non whitelisted modules

    Subclasses should set NETWORKING_ALLOWED_PREFIXES to a tuple of allowed
    qualified prefixes (module.class.function) that should be allowed to perform
    networking requests, for example

        NETWORKING_ALLOWED_PREFIXES = ("pyredis", "pymongo.pool.Pool.create_connection")
    """

    NETWORKING_ALLOWED_PREFIXES = None

    @classmethod
    def __guard(cls, *args, **kwargs):
        """
        Checks whether the current caller (previous method in stack) should
        be allowed to call socket.socket.
        """
        caller = caller_qualname()

        if not cls.whitelist_re or not cls.whitelist_re.match(caller):
            raise NetworkError("I told you not to use the Internet! (called from %s)" % caller)

        return cls.__socket_backup(*args, **kwargs)

    @classmethod
    def setUpClass(cls):
        super(NoNetworkTestCase, cls).setUpClass()

        # Cache the regular expression so we only build it once
        if cls.NETWORKING_ALLOWED_PREFIXES:
            cls.whitelist_re = re.compile(r'^%s' % '|'.join(cls.NETWORKING_ALLOWED_PREFIXES).replace('.', r'\.'))
        else:
            cls.whitelist_re = None

        cls.__socket_backup, socket.socket = socket.socket, cls.__guard

    @classmethod
    def tearDownClass(cls):
        socket.socket = cls.__socket_backup

        super(NoNetworkTestCase, cls).tearDownClass()
