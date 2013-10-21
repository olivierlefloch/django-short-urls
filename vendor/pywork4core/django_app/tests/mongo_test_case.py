# coding=utf-8

from __future__ import unicode_literals

from django_app import mongo_test_case


class MongoTestCaseTestCase(mongo_test_case.MongoTestCase):
    def test(self):
        self.database.test_collection.insert({'foo': 'bar'})

        self.assertEqual(1, 1)
