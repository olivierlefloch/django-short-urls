# coding=utf-8

"""
This module contains utility methods to easily generate temporary files.
"""

from __future__ import unicode_literals

import os
from tempfile import mkstemp

from django.conf import settings


def get_temp_filename(suffix=''):
    """Returns the full path to a new temporary file who's name ends with `suffix`."""
    (handle, filename) = mkstemp(suffix=suffix, dir=settings.TEMP_DIR)
    os.close(handle)

    return filename
