# coding=utf-8

from __future__ import unicode_literals

import os

from unittest import TestCase
from mock import patch

from utils import gui, path, tmp


class UtilsTest(TestCase):
    @staticmethod
    def test_gui_open_file():
        filename = 'test.png'

        with patch('subprocess.check_call') as subprocess_check_call:
            gui.open_file(filename)

        subprocess_check_call.assert_called_with([
            os.path.join(path.get_bin_dir(), 'open'), filename
        ])

    def test_get_temp_filename(self):
        temp_dir = 'temp'

        # pylint: disable=W0612
        with patch('utils.tmp.settings', TEMP_DIR=temp_dir) as settings:
            nb_temp_files_before = len(os.listdir(temp_dir))

            temp_filename = tmp.get_temp_filename()

            self.assertIn(temp_dir, temp_filename)

            os.remove(temp_filename)

            extension = '.png'

            temp_filename = tmp.get_temp_filename(extension)

            self.assertIn(extension, temp_filename)

            os.remove(temp_filename)

            self.assertEquals(len(os.listdir(temp_dir)), nb_temp_files_before)
