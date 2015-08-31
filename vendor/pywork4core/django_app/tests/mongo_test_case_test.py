# coding=utf-8

from __future__ import unicode_literals

from mongoengine import Document

from django_app.mongo_test_case import MongoTestCase


class MongoTestCaseTestCase(MongoTestCase):
    class MongoDoc(Document):
        pass

    def test(self):
        self._database.test_collection.insert({'foo': 'bar'})

        self.MongoDoc().save()
