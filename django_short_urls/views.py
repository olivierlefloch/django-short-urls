# coding=utf-8

'''
Views for Django Short Urls:

  - main is the redirect view
  - new is the API view to create shortened urls
'''

from __future__ import unicode_literals

from logging import getLogger
import re

from django.http import Http404
from django.shortcuts import redirect
from django.views.decorators.http import require_safe, require_POST
from statsd import statsd

from utils.mongo import mongoengine_is_primary
from http.status import HTTP_BAD_REQUEST, HTTP_CONFLICT, HTTP_FORBIDDEN
from http.utils import proxy, response, url_append_parameters, validate_url

import django_short_urls.suffix_catchall as suffix_catchall
from django_short_urls.models import Link
from django_short_urls.exceptions import InvalidHashException, ForbiddenKeyword, ShortPathConflict
from django_short_urls.auth import login_with_basic_auth_required
from django_short_urls.w4l_http import get_browser, get_client_ip, URL_SAFE_FOR_PATH


REF_PARAM_NAME = 'ref'
REF_PARAM_DEFAULT_VALUE = 'shortener'

REDIRECT_PARAM_NAME = 'redirect_suffix'

# This regex extracts the longest valid path in the url
_EXTRACT_VALID_PATH_RE = re.compile(r'^[%s]*' % URL_SAFE_FOR_PATH)


def _extract_valid_path(path):
    """Remove anything after the first non-URL_SAFE_FOR_PATH char as well as the last potential trailing '/',"""

    path = _EXTRACT_VALID_PATH_RE.match(path).group(0)

    if path[-1:] == '/':
        # This can't be done directly in the regex because of greediness issues (URL_SAFE_FOR_PATH includes '/')
        return path[:-1]

    return path


# pylint: disable=E1101, W0511
@require_safe
def main(request, path):
    '''Search for a long link matching the `path` and redirect'''

    path = _extract_valid_path(path)

    link = Link.find_by_hash(path)

    if link is None:
        # Try to find a matching short link by removing valid "catchall" suffixes
        path_prefix, redirect_suffix = suffix_catchall.get_hash_from(path)

        if redirect_suffix is not None:
            # If we found a suffix, we try to find a link again with the prefix
            link = Link.find_by_hash(path_prefix)
    else:
        redirect_suffix = None

    # Instrumentation
    prefix_tag = 'prefix:' + link.prefix if link else 'Http404'

    statsd.increment('workforus.clicks', tags=[prefix_tag])
    statsd.set('workforus.unique_links', link.hash if link else 'Http404', tags=[prefix_tag])
    statsd.set('workforus.unique_ips', get_client_ip(request), tags=['browser:' + get_browser(request)])

    # 404 if link not found or register a click if the DB is not in readonly mode
    if link is None:
        raise Http404
    elif mongoengine_is_primary():
        link.click()

    # Tweak the redirection link based on the query string, redirection suffix, etc.
    # FIXME: Handle multiple parameters with the same name in the `url`
    query = request.GET.copy()

    if redirect_suffix is not None:
        query[REDIRECT_PARAM_NAME] = redirect_suffix

    if bool(query) and REF_PARAM_NAME not in query:
        # If we specify a non empty query, indicate that the shortener tweaked the url
        query[REF_PARAM_NAME] = REF_PARAM_DEFAULT_VALUE

    target_url = url_append_parameters(
        link.long_url,
        params_to_replace=query,
        defaults={REF_PARAM_NAME: REF_PARAM_DEFAULT_VALUE}
    )

    # Either redirect the user, or load the target page and display it directly
    if link.act_as_proxy:
        return proxy(target_url)
    else:
        return redirect(target_url, permanent=True)


@require_POST
@login_with_basic_auth_required
def new(request):
    '''Create a new short url based on the POST parameters'''
    long_url = request.GET.get('long_url')

    if long_url is None:
        is_valid, error_message = False, "Missing GET parameter: 'long_url'"
    else:
        is_valid, error_message = validate_url(long_url)

    if not is_valid:
        return response(status=HTTP_BAD_REQUEST, message=error_message)

    params = {}

    for key in ['short_path', 'prefix']:
        params[key] = request.GET.get(key)

        if key == 'prefix' and 'allow_slashes_in_prefix' in request.GET:
            continue

        if params[key] is not None and '/' in params[key]:
            return response(
                status=HTTP_BAD_REQUEST,
                message="%s may not contain a '/' character." % key)

    statsd.increment(
        'workforus.new',
        tags=['prefix:' + unicode(params['prefix']), 'is_secure:' + unicode(request.is_secure())])

    try:
        link = Link.shorten(long_url, **params)

        getLogger('app').info(
            'Successfully shortened %s into %s for user %s',
            link.long_url, link.hash, request.user.login)
    except ShortPathConflict, err:
        del params['short_path'], long_url
        del params['prefix']

        params['hash'] = err.hash

        return response(status=HTTP_CONFLICT, message=str(err), **params)
    except InvalidHashException, err:
        getLogger('app').error(str(err))

        return response(
            status=HTTP_FORBIDDEN if isinstance(err, ForbiddenKeyword) else HTTP_BAD_REQUEST,
            message=str(err), **params)

    params['short_path'] = link.hash.split('/')[-1]

    params['short_url'] = link.build_absolute_uri(request)

    return response(**params)
