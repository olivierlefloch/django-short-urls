'''
Views for Django Short Urls:

  - main is the redirect view
  - new is the API view to create shortened urls
'''

from datetime import datetime

from django.conf import settings
from django.http import Http404
from django.shortcuts import redirect
from django.utils.log import getLogger
from django.views.decorators.http import require_safe, require_POST

import suffix_catchall
from w4l_http import *
from models import Link, User, Click
from exceptions import ForbiddenKeyword, ShortPathConflict


REF_PARAM_NAME  = 'ref'
REF_PARAM_DEFAULT_VALUE = 'shortener'

REDIRECT_PARAM_NAME = 'redirect_suffix'


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

    if not settings.SITE_READ_ONLY:
        Click(
            server="%s:%s" % (request.META['SERVER_NAME'], request.META['SERVER_PORT']),
            full_path=request.get_full_path(),
            link=link,
            created_at=datetime.utcnow(),
            ip=request.META['REMOTE_ADDR'],
            browser=(
                ''.join([x if ord(x) < 128 else '?' for x in request.META['HTTP_USER_AGENT']])
                    if 'HTTP_USER_AGENT' in request.META else None),
            referer=request.META['HTTP_REFERER'] if 'HTTP_REFERER' in request.META else None,
            lang=request.META['HTTP_ACCEPT_LANGUAGE'] if 'HTTP_ACCEPT_LANGUAGE' in request else None
        ).save()

    if link is None:
        raise Http404

    # Tweak the redirection link based on the query string, redirection suffix, etc.
    query = request.GET.copy()

    if redirect_suffix is not None:
        query[REDIRECT_PARAM_NAME] = redirect_suffix

    if bool(query) and REF_PARAM_NAME:
        # If we specify a non empty query, indicate that the shortener tweaked the url
        query[REF_PARAM_NAME] = REF_PARAM_DEFAULT_VALUE

    target_url = url_append_parameters(
        link.long_url,
        params_to_replace=query,
        defaults={REF_PARAM_NAME: REF_PARAM_DEFAULT_VALUE}
    )

    # Either redirect the user, or load the target page and display it directly
    return (proxy if link.act_as_proxy else redirect)(target_url)

@require_POST
def new(request):
    '''
    Create a new short url based on the POST parameters
    '''

    if 'login' in request.REQUEST and 'api_key' in request.REQUEST:
        login   = request.REQUEST['login']
        api_key = request.REQUEST['api_key']

        user = User.objects(login=login, api_key=api_key).first()
    else:
        user = None

    if user is None:
        return response(status=HTTP_UNAUTHORIZED, message="Invalid credentials.")

    params = {
        'creator': user.login
    }

    if 'long_url' in request.REQUEST:
        params['long_url'] = request.REQUEST['long_url']

        (is_valid, error_message) = validate_url(params['long_url'])

        if not is_valid:
            return response(status=HTTP_BAD_REQUEST, message=error_message)
    else:
        return response(
            status=HTTP_BAD_REQUEST,
            message="Missing parameter: 'long_url'")

    if 'short_path' in request.REQUEST:
        params['short_path'] = request.REQUEST['short_path']

        if '/' in params['short_path']:
            return response(
                status=HTTP_BAD_REQUEST,
                message="short_path may not contain a '/' character.")

    if 'prefix' in request.REQUEST:
        params['prefix'] = request.REQUEST['prefix']

        if '/' in params['prefix']:
            return response(
                status=HTTP_BAD_REQUEST,
                message="prefix may not contain a '/' character.")

    try:
        link = Link.shorten(**params)
    except ShortPathConflict, e:
        del params['short_path'], params['long_url']
        if 'prefix' in params:
            del params['prefix']
        params['hash'] = e.link.hash

        return response(status=HTTP_CONFLICT, message=str(e), **params)
    except ForbiddenKeyword, e:
        getLogger('app').warning('Attempt to use forbidden keyword "%s" in a short url.' % e.keyword)
        return response(status=HTTP_FORBIDDEN, message=str(e), **params)

    params['short_path'] = link.short_path

    params['short_url'] = link.build_absolute_uri(request)

    return response(**params)
