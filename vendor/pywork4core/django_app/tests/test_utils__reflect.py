# coding=utf-8

from __future__ import unicode_literals

from django_app.test import PyW4CTestCase
from utils.reflect import caller_qualname


class UtilsReflectTest(PyW4CTestCase):
    def test_caller_qualname(self):
        self.assertEqual(caller_qualname(skip=42), "")

        self.assertEqual(
            caller_qualname(skip=1),
            "pywork4core.django_app.tests.test_utils__reflect.UtilsReflectTest.test_caller_qualname")

        self.assertEqual(
            caller_qualname(),
            "unittest.case.UtilsReflectTest.run")

        self.assertEqual(
            caller_qualname(skip=-1),
            "")

        self.assertEqual(
            caller_qualname(skip=-2),
            "coverage.cmdline.main")
