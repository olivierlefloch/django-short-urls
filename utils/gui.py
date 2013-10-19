# coding=utf-8

"""
This module contains utility methods such as temporary file generation or GUI manipulations.
"""

from __future__ import unicode_literals

import os
import subprocess

from .path import get_bin_dir


def open_file(filename):
    """
    Attempts to open file using the default application handling that file type.
    """
    subprocess.check_call([os.path.join(get_bin_dir(), 'open'), filename])
