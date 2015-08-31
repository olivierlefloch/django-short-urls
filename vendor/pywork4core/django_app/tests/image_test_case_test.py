# coding=utf-8

from __future__ import unicode_literals

import os

from utils.image_test_case import ImageTestCase
from utils import tmp


class ImageTestCaseTestCase(ImageTestCase):
    def test(self):
        def _path_from_name(name):
            return os.path.join(os.path.dirname(__file__), 'results/' + name)

        def _compare(file1, file2, **kwargs):
            self.assertImageAlmostEqual(_path_from_name(file1), _path_from_name(file2), **kwargs)

        # Compare identical images
        _compare('white.png', 'white.png')
        _compare('red.jpg', 'red.jpg')
        # Compare close images
        _compare('gradient.png', 'gradient-broken.png', threshold=7, outfile=tmp.get_temp_filename('.png'))

        with self.assertRaises(AssertionError):
            _compare('red.jpg', 'white.png')
