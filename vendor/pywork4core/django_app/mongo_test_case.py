# coding: utf-8

"""
Test case for MongoEngine

Adapted from https://github.com/MongoEngine/mongoengine/blob/master/mongoengine/django/tests.py
MongoEngine's license: https://github.com/MongoEngine/mongoengine/blob/master/LICENSE
"""

from __future__ import unicode_literals

from django.test import TestCase
from django.conf import settings
from mongoengine.connection import connect, disconnect
from mongoengine import Document


# pylint: disable=R0904
class MongoTestCase(TestCase):
    """
    TestCase class that clears the collection between the tests
    """

    def __init__(self, method_name='runtest'):
        disconnect()

        db_name = 'test_%s' % settings.MONGOENGINE['db']
        self.database = connect(db_name, tz_aware=settings.USE_TZ)[db_name]

        super(MongoTestCase, self).__init__(method_name)

    def _post_teardown(self):
        super(MongoTestCase, self)._post_teardown()

        for collection in self.database.collection_names():
            if collection == 'system.indexes':
                continue

            self.database.drop_collection(collection)

        # Mongoengine models need to forget about their collection (to recreate indexes). Hackish, I know.
        # pylint: disable=E1101
        for model in Document.__subclasses__():
            if hasattr(model, '_collection'):
                del model._collection

        disconnect()
