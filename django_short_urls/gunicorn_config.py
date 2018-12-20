# -*- coding: utf-8 -*-
"""
Defines the shortener / django-short-urls settings for gunicorn.
https://docs.gunicorn.org/en/19.9.0/settings.html
"""
# Sorry pylint, I know you don't like lowercase constants, but...
# pylint: disable=invalid-name

import os

# GENERAL / TUNING
proc_name = "shortener"

# Do start gunicorn from the virtualenv to make all 3rd-party pkgs available
pythonpath = os.path.dirname(os.path.abspath(__file__))

bind = "127.0.0.1:8000"

# Tuning: see http://docs.gunicorn.org/en/19.9.0/design.html
# Use async gevent workers; doesn't hurt, may help a little with DB I/O
worker_class = "gevent"

# Pass the numbers of `workers` using the WEB_CONCURRENCY envvar
threads = 0
max_requests = 100000
max_requests_jitter = 100

timeout = 10


# MONITORING
statsd_host = "localhost:8125"
statsd_prefix = ""
