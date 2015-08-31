# coding=utf-8
'''
TestCase extension that knows how to compare image files for equality.

Use as such (compatible with other TestCase classes):

    class MyTestCase(ImageTestCase):
        self.assertImageAlmostEqual(path_to_generated, path_to_expected)
'''

# Force floating point division
from __future__ import division, unicode_literals

from django.test import TestCase
from PIL import Image, ImageChops


class ImageTestCase(TestCase):
    """
    TestCase class that implements `ImageTestCase.assertImageAlmostEqual` to
    compare image files for similarity.
    """

    def assertImageAlmostEqual(self, img_path1, img_path2, threshold=1, outfile=None):  # pylint: disable=invalid-name
        """
        Threshold is the percentage of pixels that may differ between the two images.
        Tweak it for your test based on how different the rendered images end up
        being on your various build platforms.
        """
        diff = ImageChops.difference(Image.open(img_path1), Image.open(img_path2))

        if outfile is not None:
            diff.save(outfile)

        for count, color in diff.getcolors():
            # getcolors() returns [(nbpixels, (r, g, b)), ...]
            # http://pillow.readthedocs.org/en/latest/reference/Image.html?#PIL.Image.Image.getcolors
            if color == (0, 0, 0):
                count_black = count
                break
        else:
            count_black = 0

        # Compare some highlevel stats on the diff to the arbitrary delta threshold
        percentage_difference = (1 - count_black / (diff.width * diff.height)) * 100
        print ""
        print count_black, diff.width, diff.height
        print (percentage_difference, img_path1, img_path2, outfile)
        return self.assertLess(
            percentage_difference, threshold,
            msg='Image "%s" is not almost equal to "%s" (%d%% of pixels differ, >%d%%)' % (
                img_path1, img_path2, percentage_difference, threshold))
