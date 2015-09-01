# coding=utf-8

from __future__ import unicode_literals

from django_app.test import PyW4CTestCase

from django_short_urls.int_to_alnum import ALPHABET, encode, decode


# pylint: disable=E1101
class IntToAlnumTestCase(PyW4CTestCase):
    def test_alphabet(self):
        self.assertEquals(len(ALPHABET), 10 + 2 * 26)

    def test(self):
        value = 123456789

        self.assertEquals(decode(encode(value)), value)

        self.assertEquals(encode(0), ALPHABET[0])
