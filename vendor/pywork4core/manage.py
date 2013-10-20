#!/bin/bash

# coding=utf-8

"true" '''\' This shebang is here to ensure that we use the venv python in all cases.
# So we use bash as the base script, then figure out which python to use, and run
# this script again. We use the 'true' command because it ignores its argument.
exec "$(dirname $0)/venv/bin/python" "$0" "$@"
'''

from __future__ import unicode_literals

import os
import sys

# pylint: disable=W0622
# We need to override the docstring because the current value is the shebang
__doc__ = '''Wrapper around django-admin.py, it will set the DJANGO_SETTING_MODULES environment variable.'''

if __name__ == "__main__":
    # we can not use setdefault since it will not work when calling from another python script
    os.environ['DJANGO_SETTINGS_MODULE'] = "django_app.settings"

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
