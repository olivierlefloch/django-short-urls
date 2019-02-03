# coding: utf-8

"""
Utility methods to exploit python reflection.
HACKY! Try and use this only when absolutely necessary.
"""

from __future__ import unicode_literals

import inspect


def caller_qualname(skip=2):
    """
    From https://gist.github.com/techtonik/2151727 [Public Domain].
    See https://www.python.org/dev/peps/pep-3155/ for how to do this properly in
    python 3.3+.

    Get a name of a caller in the format module.class.method

    `skip` specifies how many levels of stack to skip while getting caller
    name. skip=1 means "who calls me", skip=2 "who calls my caller", etc.
    Default is '2' because you generally want to know who's calling your own
    method, not who's calling this (caller_name) method.

    An empty string is returned if skipped levels exceed stack height.
    """
    stack = inspect.stack()
    start = 0 + skip

    if len(stack) < start + 1:
        return ''

    parentframe = stack[start][0]

    name = []
    module = inspect.getmodule(parentframe)
    # `modname` can be None when frame is executed directly in console
    # TODO: consider using __main__
    if module:
        name.append(module.__name__)
    # detect classname
    if 'self' in parentframe.f_locals:
        # I don't know any way to detect call from the object method
        # XXX: there seems to be no way to detect static method call - it will be just a function call
        name.append(parentframe.f_locals['self'].__class__.__name__)
    codename = parentframe.f_code.co_name
    if codename != '<module>':
        # top level usually -> function or a method
        name.append(codename)

    del parentframe

    return ".".join(name)
