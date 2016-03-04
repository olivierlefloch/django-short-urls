# coding=utf-8

"""Module to manipulate requests, HTML and HTTP concepts"""

from __future__ import unicode_literals

from collections import OrderedDict
import re
import urllib

from django.http import HttpResponse
from django.template import loader

from http.status import HTTP_SERVICE_UNAVAILABLE

_BROWSERS = OrderedDict((
    ('Opera', 'opera'),
    ('MSIE', 'ie'),
    ('Chrome', 'chrome'),
    ('Android', 'android'),
    ('iPhone', 'iphone'),
    ('iPad', 'ipad'),
    ('Safari', 'safari'),
    ('Firefox', 'firefox'),
    ('Googlebot', 'google'),
    ('Twitterbot', 'twitter'),
    ('facebookexternalhit', 'facebook'),
    ('LinkedInBot', 'linkedin'),
    ('Pingdom', 'pingdom'),
    ('default', 'unknown'),
))
_BROWSERS_REGEX = re.compile('|'.join(_BROWSERS.keys()))

URL_SAFE_FOR_PATH = urllib.always_safe + '/'


def response_service_unavailable():
    """Returns a 503 error based on a static template"""
    return HttpResponse(loader.render_to_string('503.html'), status=HTTP_SERVICE_UNAVAILABLE)


def get_browser(request):
    """Retrieve the browser name from a request object"""
    browser_match = _BROWSERS_REGEX.search(request.META['HTTP_USER_AGENT'] if 'HTTP_USER_AGENT' in request.META else '')

    if not browser_match:
        return _BROWSERS['default']

    return _BROWSERS[browser_match.group()]


def get_client_ip(request):
    """Retrieve the client's real IP (not the load balancer's :) )"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

    if x_forwarded_for:
        return x_forwarded_for.split(',')[-1].strip()

    return request.META.get('REMOTE_ADDR')
