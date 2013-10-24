# coding=utf-8

from __future__ import unicode_literals

import os

from unittest import TestCase
from mock import patch

from utils import gui, path, tmp


class UtilsTest(TestCase):
    temp_dir = 'temp'

    @staticmethod
    @patch('subprocess.check_call')
    def test_gui_open_file(subprocess_check_call):
        filename = 'test.png'

        gui.open_file(filename)

        subprocess_check_call.assert_called_with([
            os.path.join(path.get_bin_dir(), 'open'), filename
        ])

    # pylint: disable=W0613
    @patch('utils.tmp.settings', TEMP_DIR=temp_dir)
    def test_get_temp_filename(self, settings):
        nb_temp_files_before = len(os.listdir(self.temp_dir))

        temp_filename = tmp.get_temp_filename()

        self.assertIn(self.temp_dir, temp_filename)

        os.remove(temp_filename)

        extension = '.png'

        temp_filename = tmp.get_temp_filename(extension)

        self.assertIn(extension, temp_filename)

        os.remove(temp_filename)

        self.assertEquals(len(os.listdir(self.temp_dir)), nb_temp_files_before)
