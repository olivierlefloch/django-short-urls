# coding=utf-8

from __future__ import unicode_literals

import os

from mock import patch

from django_app.test import PyW4CTestCase
from utils import gui, path, tmp, patterns


class UtilsTest(PyW4CTestCase):
    temp_dir = 'temp'

    @staticmethod
    @patch('subprocess.check_call')
    def test_gui_open_file(subprocess_check_call):
        filename = 'test.png'

        gui.open_file(filename)

        subprocess_check_call.assert_called_with([
            os.path.join(path.get_bin_dir(), 'open'), filename
        ])

    @patch('utils.tmp.settings', TEMP_DIR=temp_dir)
    def test_get_temp_filename(self, settings):  # pylint: disable=W0613
        nb_temp_files_before = len(os.listdir(self.temp_dir))

        temp_filename = tmp.get_temp_filename()

        self.assertIn(self.temp_dir, temp_filename)

        os.remove(temp_filename)

        extension = '.png'

        temp_filename = tmp.get_temp_filename(extension)

        self.assertIn(extension, temp_filename)

        os.remove(temp_filename)

        self.assertEquals(len(os.listdir(self.temp_dir)), nb_temp_files_before)

    def test_patterns_singleton(self):
        val = 42

        class _TestSingleton(object):
            __metaclass__ = patterns.Singleton

            var = val

            def get_val(self):
                return self.var

            def set_var(self, new_val):
                self.var = new_val

        self.assertTrue(_TestSingleton() is _TestSingleton())
        self.assertEqual(id(_TestSingleton()), id(_TestSingleton()))

        self.assertEqual(_TestSingleton().get_val(), val)
        self.assertEqual(_TestSingleton().var, val)

        new_val = 21
        _TestSingleton().var = new_val

        self.assertEqual(_TestSingleton().var, new_val)

        _TestSingleton().set_var(val)
        self.assertEqual(_TestSingleton().get_val(), val)
