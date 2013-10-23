# coding=utf-8

"""
This module contains utility methods such as path manipulation and temporary file generation.
"""

from __future__ import unicode_literals

import os


def get_root_dir():
    """Returns the absolute path to the work4core root directory"""
    return os.path.dirname(os.path.dirname(__file__))


def get_bin_dir():
    """Returns the absolute path to the work4core executables (/bin)"""
    return os.path.abspath(os.path.join(get_root_dir(), 'bin/'))
