# coding=utf-8
'''A little helper allowing to mock requests very effectively for tests'''

from __future__ import unicode_literals

import functools
import json
from contextlib import contextmanager
import logging

import requests
from mock import patch, MagicMock


@contextmanager
def patch_requests(mapping):
    """
        mapping is a dict of str => data
        so that "toto" => {"response" =>{"success" : 1}, "json" => True/False} means that
        any url called with *toto* will return {"success" : 1}
        json part is optional
    """

    def _request_response_from_query(_, url, **kwargs):  # pylint: disable=C0111,W0613
        return _response(url)

    def _other_response_from_query(url, **kwargs):  # pylint: disable=C0111,W0613
        return _response(url)

    def _response(url):
        '''
        If the requested URL is found in the mapping, returns the mocked response as configured
        '''
        logging.info("mocking %s", url)
        for (token, config) in mapping.iteritems():
            if token in url:
                resp = requests.Response()
                resp.url = url
                resp.status_code = config.get('http_code', 200)
                if config.get("json", False):
                    resp._content = json.dumps(config["response"])  # pylint: disable=W0212
                else:
                    # str: Requests uses str as bytes internally, at least on Python 2
                    resp._content = str(config["response"])  # pylint: disable=W0212
                if config.get('headers'):
                    resp.headers = config.get('headers')
                return resp
        raise Exception("Requests mock called with unexpected URL, nothing in the mapping for %s" % url)

    methods_map = {
        'request': MagicMock(side_effect=_request_response_from_query),
        'get': MagicMock(side_effect=_other_response_from_query),
        'post': MagicMock(side_effect=_other_response_from_query),
        'put': MagicMock(side_effect=_other_response_from_query),
        'head': MagicMock(side_effect=_other_response_from_query),
        'patch': MagicMock(side_effect=_other_response_from_query),
        'options': MagicMock(side_effect=_other_response_from_query),
        'delete': MagicMock(side_effect=_other_response_from_query),
    }

    with patch.multiple('requests', **methods_map):
        yield {k: getattr(requests, k) for k in methods_map}


def patch_requests_decorator(mapping):
    """
    Use patch_requests as decorator.
    """
    def decorator(func):  # pylint: disable=C0111
        @functools.wraps(func)
        def inner(*args, **kwargs):  # pylint: disable=C0111
            with patch_requests(mapping):
                return func(*args, **kwargs)
        return inner
    return decorator
