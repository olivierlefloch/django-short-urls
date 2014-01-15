# coding=utf-8

"""Module to manipulate requests, HTML and HTTP concepts"""

from __future__ import unicode_literals

from collections import OrderedDict
from django.http import HttpResponse, QueryDict
from django.template import loader
import json
import re
import requests
from urllib import urlencode
import urlparse

HTTP_OK = 200
HTTP_BAD_REQUEST = 400
HTTP_UNAUTHORIZED = 401
HTTP_FORBIDDEN = 403
HTTP_CONFLICT = 409
HTTP_SERVER_ERROR = 500
HTTP_SERVICE_UNAVAILABLE = 503

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


def validate_url(url):
    """Validates that a url has a valid structure"""

    parsed_url = urlparse.urlparse(url)

    if not parsed_url.netloc:
        return (False, "Url structure is invalid: '%s'" % url)

    if parsed_url.scheme not in ('http', 'https'):
        return (False, "Unsupported URL scheme: '%s'" % url)

    if parsed_url.password:
        return (False, "URLs containing passwords are not supported: '%s'" % url)

    return (True, None)


def url_append_parameters(url, params_to_replace, defaults):
    '''
    Appends the REDIRECT_PARAM_NAME param and the shorten's GET params
    to the long URL.
    Takes QueryDicts as parameters
    '''

    if not params_to_replace and not defaults:
        return url

    # pylint: disable=W0633
    (scheme, netloc, path, params, link_query, fragment) = urlparse.urlparse(url)

    link_query = QueryDict(link_query).copy()

    for key, value in params_to_replace.iteritems():
        link_query[key] = value

    for key, value in defaults.iteritems():
        if key not in link_query:
            link_query[key] = value

    return urlparse.urlunparse((
        scheme, netloc, path, params,
        urlencode(link_query),
        fragment
    ))


def response(message=None, status=HTTP_OK, **kwargs):
    """Builds a json response with the kwargs object and some additional standardized fields"""
    kwargs.update({
        "status_code": status,
        "error": status != HTTP_OK,
        "message": message
    })

    return HttpResponse(json.dumps(kwargs), status=status, mimetype="application/json")


def proxy(url):
    """Loads url and returns its contents as a proxied web page"""
    resp = requests.get(url)

    return HttpResponse(
        resp.content,
        status=resp.status_code,
        mimetype=resp.headers['Content-Type'])


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
