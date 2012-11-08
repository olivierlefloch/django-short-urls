from datetime import datetime

from django.shortcuts import redirect
from django.http import Http404
from django.utils.log import getLogger
logger = getLogger('app')

from w4l_http import *
from models import Link, User, Click, ShortPathConflict, ForbiddenKeyword

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

    return redirect(link.long_url)

def new(request):
    if request.method != 'PUT' and request.method != 'POST':
        # Support both 'PUT' and 'POST' as this is not truly a RESTful API, but definitely do not allow 'GET'
        return response(
            status=HTTP_BAD_REQUEST,
            message="The 'new' endpoint only accepts PUT or POST requests.")

    try:
        login   = request.REQUEST['login']
        api_key = request.REQUEST['api_key']

        user = User.objects(login=login, api_key=api_key).first()
    except KeyError:
        user = None

    if user is None:
        return response(status=HTTP_UNAUTHORIZED, message="Invalid credentials.")

    params = {
        'creator': user.login
    }

    try:
        params['long_url'] = request.REQUEST['long_url']

        (is_valid, error) = validate_url(params['long_url'])

        if not is_valid:
            return response(status=HTTP_BAD_REQUEST, message=message)
    except KeyError, e:
        return response(
            status=HTTP_BAD_REQUEST,
            message="Missing parameter: '%s'" % e.value)

    try:
        params['short_path'] = request.REQUEST['short_path']

        if '/' in params['short_path']:
            return response(
                status=HTTP_BAD_REQUEST,
                message="short_path may not contain a '/' character.")
    except KeyError:
        pass


    try:
        params['prefix'] = request.REQUEST['prefix']

        if '/' in params['prefix']:
            return response(
                status=HTTP_BAD_REQUEST,
                message="prefix may not contain a '/' character.")
    except KeyError:
        pass

    try:
        link = Link.shorten(**params)
    except ShortPathConflict, e:
        del params['short_path'], params['prefix'], params['long_url']
        params['hash'] = e.link.hash

        return response(status=HTTP_CONFLICT, message=str(e), **params)
    except ForbiddenKeyword, e:
        logger.warning('Attempt to use forbidden keyword "%s" in a short url.' % e.keyword)
        return response(status=HTTP_FORBIDDEN, message=str(e), **params)

    params['short_path'] = link.short_path

    params['short_url'] = request.build_absolute_uri("/%s%s" % (
        '%s/' % params['prefix'] if params['prefix'] else '',
        params['short_path']))

    return response(**params)
