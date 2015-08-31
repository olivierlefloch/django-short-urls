# coding=utf-8

"""Common test class to ensure Mongo and network requests are properly handled"""

from __future__ import unicode_literals

from django_app.mongo_test_case import MongoTestCase
from django_app.no_network_test_case import NoNetworkTestCase


class PyW4CTestCase(MongoTestCase, NoNetworkTestCase):  # pylint: disable=too-many-public-methods
    """
    Test case that handles both Mongo and prevents network requests, should be
    used as a base test case in all your projects.
    """

    NETWORKING_ALLOWED_PREFIXES = ('pymongo.',)
