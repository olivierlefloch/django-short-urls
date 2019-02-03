# coding=utf-8

"""
This module contains utility methods for common programming patterns
"""

from __future__ import unicode_literals


class Singleton(type):
    """
    Singleton Metaclass, usage:

    >>> class MyClass(object):
    >>>     __metaclass__ = Singleton
    >>> MyClass() is MyClass()
        True
    """
    def __init__(cls, name, bases, dict_):
        super(Singleton, cls).__init__(name, bases, dict_)
        cls.instance = None

    def __call__(cls, *args, **kw):
        if cls.instance is None:
            cls.instance = super(Singleton, cls).__call__(*args, **kw)
        return cls.instance
