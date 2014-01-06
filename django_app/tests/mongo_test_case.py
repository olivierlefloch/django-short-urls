# coding=utf-8

from __future__ import unicode_literals

from mongoengine import Document

from django_app import mongo_test_case


class MongoTestCaseTestCase(mongo_test_case.MongoTestCase):
    # pylint: disable=R0924
    class MongoDoc(Document):
        pass

    def test(self):
        self.database.test_collection.insert({'foo': 'bar'})

        self.MongoDoc().save()

        self.assertEqual(1, 1)
