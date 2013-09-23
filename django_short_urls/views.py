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
REF_PARAM_VALUE = 'shortener'

@require_safe
def main(request, path):
    if len(path) and path[-1] == '/':
        # Removing trailing slash so "/jobs/" and "/jobs" redirect identically
        path = path[:-1]

    link, redirect_target = Link.find_by_hash(path)
    query = request.GET.copy()
    if redirect_target is not None:
        query[suffix_catchall.REDIRECT_PARAM_NAME] = redirect_target

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

    if REF_PARAM_NAME not in query:
        query[REF_PARAM_NAME] = REF_PARAM_VALUE

    url = (
        link.long_url if redirect_target is None
        else suffix_catchall.url_append_parameters(link.long_url, shorten_query=query.urlencode())
    )

    return (proxy if link.act_as_proxy else redirect)(url)

@require_POST
def new(request):
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
