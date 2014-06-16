# coding=utf-8

'''
Views for Django Short Urls:

  - main is the redirect view
  - new is the API view to create shortened urls
'''

from __future__ import unicode_literals

from django.conf import settings
from django.http import Http404
from django.shortcuts import redirect
from django.utils.log import getLogger
from django.views.decorators.http import require_safe, require_POST
from statsd import statsd

from http.status import HTTP_UNAUTHORIZED, HTTP_BAD_REQUEST, HTTP_CONFLICT, HTTP_FORBIDDEN

import django_short_urls.suffix_catchall as suffix_catchall
from django_short_urls.models import Link, User
from django_short_urls.exceptions import ForbiddenKeyword, ShortPathConflict
from django_short_urls.w4l_http import (
    validate_url, url_append_parameters, response, proxy, get_browser, get_client_ip
)


REF_PARAM_NAME = 'ref'
REF_PARAM_DEFAULT_VALUE = 'shortener'

REDIRECT_PARAM_NAME = 'redirect_suffix'


# pylint: disable=E1101, W0511
@require_safe
def main(request, path):
    '''
    Search for a long link matching the `path` and redirect
    '''

    if len(path) and path[-1] == '/':
        # Removing trailing slash so "/jobs/" and "/jobs" redirect identically
        path = path[:-1]

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
    elif not settings.SITE_READ_ONLY:
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
    return (proxy if link.act_as_proxy else redirect)(target_url)


# pylint: disable=W0142
@require_POST
def new(request):
    '''
    Create a new short url based on the POST parameters
    '''

    if 'login' in request.REQUEST and 'api_key' in request.REQUEST:
        login = request.REQUEST['login']
        api_key = request.REQUEST['api_key']

        user = User.objects(login=login, api_key=api_key).first()
    else:
        user = None

    if user is None:
        return response(status=HTTP_UNAUTHORIZED, message="Invalid credentials.")

    params = {}

    if 'long_url' in request.REQUEST:
        params['long_url'] = request.REQUEST['long_url']

        (is_valid, error_message) = validate_url(params['long_url'])
    else:
        (is_valid, error_message) = (False, "Missing parameter: 'long_url'")

    if not is_valid:
        return response(status=HTTP_BAD_REQUEST, message=error_message)

    for key in ['short_path', 'prefix']:
        if key in request.REQUEST:
            params[key] = request.REQUEST[key]

            if '/' in params[key]:
                return response(
                    status=HTTP_BAD_REQUEST,
                    message="%s may not contain a '/' character." % key)

    try:
        link = Link.shorten(**params)

        getLogger('app').info('Successfully shortened %s into %s for user %s', link.long_url, link.hash, login)
    except ShortPathConflict, err:
        del params['short_path'], params['long_url']

        if 'prefix' in params:
            del params['prefix']

        params['hash'] = err.link.hash

        return response(status=HTTP_CONFLICT, message=str(err), **params)
    except ForbiddenKeyword, err:
        getLogger('app').warning('Attempt to use forbidden keyword "%s" in a short url.' % err.keyword)

        return response(status=HTTP_FORBIDDEN, message=str(err), **params)

    params['short_path'] = link.hash.split('/')[-1]

    params['short_url'] = link.build_absolute_uri(request)

    return response(**params)
