# coding=utf-8

"""
This module contains utility methods for mongo/mongoengine.
"""

from __future__ import unicode_literals

import mongoengine


def mongoengine_is_primary():
    """Checks if the current mongoengine connection is to a primary"""
    return mongoengine.connection.get_connection().is_primary
