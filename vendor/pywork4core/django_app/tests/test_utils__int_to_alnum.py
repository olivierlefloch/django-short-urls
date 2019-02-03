# coding=utf-8

from __future__ import unicode_literals

from django_app.test import PyW4CTestCase

from utils.int_to_alnum import DEFAULT_ALPHABET, encode, decode


class IntToAlnumTestCase(PyW4CTestCase):
    def test_default_alphabet_length(self):
        self.assertEquals(len(DEFAULT_ALPHABET), 10 + 2 * 26)

    def test(self):
        value = 123456789

        self.assertEquals(decode(encode(value)), value)

        self.assertEquals(encode(0), DEFAULT_ALPHABET[0])
