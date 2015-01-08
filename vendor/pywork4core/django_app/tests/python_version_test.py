# coding=utf-8

from __future__ import unicode_literals

import sys

from unittest import TestCase


class PythonVersionTest(TestCase):
    def test(self):
        # PyWork4Core only works with Python [2.7, 3[
        self.assertTrue(sys.version_info < (3,))
        self.assertTrue(sys.version_info >= (2, 7))
