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

    def assertImageAlmostEqual(self, img_path1, img_path2,  # pylint: disable=invalid-name,too-many-arguments
                               threshold=1, diff_file=None, strict=True):
        """
        Threshold is the percentage of pixels that may differ between the two images.
        Tweak it for your test based on how different the rendered images end up
        being on your various build platforms.
        """
        diff = ImageChops.difference(Image.open(img_path1), Image.open(img_path2))

        if diff_file is not None:
            diff.save(diff_file)
            saved_to_text = "\nDiff saved to: %s" % diff_file
        else:
            saved_to_text = ''

        nb_bands = len(diff.getbands())

        histogram = diff.histogram()

        nb_colors = int(len(histogram) / nb_bands)

        average_zeroes = sum([histogram[pos * nb_colors] for pos in xrange(nb_bands)]) / nb_bands

        percentage_difference = (1 - average_zeroes / (diff.height * diff.width)) * 100

        assert_func = self.assertLess if strict else self.assertLessEqual
        return assert_func(
            percentage_difference, threshold,
            msg='Image "%s" is not almost equal to "%s" (%d%% of pixels differ, >%d%%)%s' % (
                img_path1, img_path2, percentage_difference, threshold, saved_to_text))

    def assertImageEqual(self, img_path1, img_path2, diff_file=None):  # pylint: disable=invalid-name
        """
        Asserts that two images are the same, Accepts the same arguments as
        `assertImageAlmostEqual` except for the `threshold`.
        """
        return self.assertImageAlmostEqual(
            img_path1, img_path2, threshold=0,
            diff_file=diff_file, strict=False
        )
