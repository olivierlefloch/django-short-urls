# coding=utf-8

from __future__ import unicode_literals

from django.http import Http404
from mock import Mock
from mongoengine import Document, StringField

from django_app.test import PyW4CTestCase
from utils.mongo import mongoengine_is_primary, LocalURLField, get_document_or_404


class MongoTestCase(PyW4CTestCase):
    def test_mongoengine_is_primary(self):
        self.assertTrue(mongoengine_is_primary())

    def test_localurlfield(self):
        local_url_field = LocalURLField()
        local_url_field.error = Mock()

        local_url_field.validate('blub://foobar')
        local_url_field.error.assert_called_once_with('Invalid scheme blub in URL: blub://foobar')
        local_url_field.error.reset_mock()

        local_url_field.validate('http://www')
        local_url_field.error.assert_called_with('Invalid URL: http://www')
        local_url_field.error.reset_mock()

        local_url_field.validate('http://www.work4labs.com')
        self.assertEqual(local_url_field.error.call_count, 0)

    def test_get_document_or_404(self):
        class TestDoc(Document):
            name = StringField()

        TestDoc(name="foobar").save()

        with self.assertRaises(Http404):
            get_document_or_404(TestDoc, name="bar")

        self.assertEqual(get_document_or_404(TestDoc, name="foobar").name, "foobar")
