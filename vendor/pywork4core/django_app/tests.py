# coding=utf-8

"""
This file instructs the projects "manage.py tests" command to run tests stored
one level higher. This way when we run the projects test suite, the PyWork4Core
tests get included.
"""

from __future__ import unicode_literals

# pylint: disable=W0401,W0614
from pywork4core.tests import *
