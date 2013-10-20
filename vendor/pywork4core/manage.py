#!/usr/bin/env python

'''Wrapper around django-admin.py, it will set the DJANGO_SETTING_MODULES environment variable.'''

from __future__ import unicode_literals

import os
import sys


if __name__ == "__main__":
    # we can not use setdefault since it will not work when calling from another python script
    os.environ['DJANGO_SETTINGS_MODULE'] = "django_app.settings"

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
