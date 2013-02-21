from datetime import datetime

from django.shortcuts import redirect
from django.http import Http404
from django.utils.log import getLogger
from django.views.decorators.http import require_safe, require_POST
logger = getLogger('app')

from w4l_http import *
from models import Link, User, Click, ShortPathConflict, ForbiddenKeyword

@require_safe
def main(request, hash):
    link = Link.find_by_hash(hash)

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

    return (proxy if link.act_as_proxy else redirect)(link.long_url)

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

    if 'scheduler_url' in request.REQUEST:
        params['scheduler_url'] = request.REQUEST['scheduler_url']

        if 'prefix' in params:
            # Partially redundant with a similar check in Link.shorten, but avoids tight coupling between Model and View in order to get the appropriate error message returned.
            return response(
                status=HTTP_BAD_REQUEST,
                message="You may not provide a scheduler_url if you are generating a prefixed short url.")

        (is_valid, error_message) = validate_url(params['scheduler_url'])

        if not is_valid:
            return response(status=HTTP_BAD_REQUEST, message=error_message)

    try:
        link = Link.shorten(**params)
    except ShortPathConflict, e:
        del params['short_path'], params['long_url']
        if 'prefix' in params:
            del params['prefix']
        params['hash'] = e.link.hash

        return response(status=HTTP_CONFLICT, message=str(e), **params)
    except ForbiddenKeyword, e:
        logger.warning('Attempt to use forbidden keyword "%s" in a short url.' % e.keyword)
        return response(status=HTTP_FORBIDDEN, message=str(e), **params)

    params['short_path'] = link.short_path

    params['short_url'] = link.build_absolute_uri(request)

    if link.scheduler_link is not None:
        params['scheduler_short_url'] = link.scheduler_link.build_absolute_uri(request)

    return response(**params)
