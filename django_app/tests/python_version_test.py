# coding=utf-8

from __future__ import unicode_literals

import sys

from django_app.test import PyW4CTestCase


class PythonVersionTest(PyW4CTestCase):
    def test(self):
        # PyWork4Core only works with Python [2.7.9, 3[
        self.assertTrue(sys.version_info < (3,))
        self.assertTrue(sys.version_info >= (2, 7, 9))
