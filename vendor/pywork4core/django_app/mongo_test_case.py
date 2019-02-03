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


class MongoTestCase(TestCase):
    """
    TestCase class that clears the collection between the tests.

    Extends internal methods of django.test.TestCase, so beware when upgrading Django!
    """

    def _pre_setup(self):
        super(MongoTestCase, self)._pre_setup()

        disconnect()

        db_name = 'test_%s' % settings.MONGOENGINE['db']
        self._database = connect(  # pylint: disable=attribute-defined-outside-init
            db_name, tz_aware=settings.USE_TZ
        )[db_name]

    def _post_teardown(self):
        for collection in self._database.collection_names():
            if collection == 'system.indexes':  # pragma: no cover
                continue

            self._database.drop_collection(collection)

        # Mongoengine models need to forget about their collection (to recreate indexes). Hackish, I know.
        # FIXME: __subclasses__ may only take direct descendants into account!
        for model in Document.__subclasses__():
            if hasattr(model, '_collection'):
                del model._collection

        disconnect()

        super(MongoTestCase, self)._post_teardown()
