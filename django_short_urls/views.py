from models import Link, User, ShortPathConflict, Click

from datetime import datetime
from django.shortcuts import redirect
from django.http import Http404

from w4l_http import *

def main(request, hash):
    link = Link.find_by_hash(hash)

    Click(
        server="%s:%s" % (request.META['SERVER_NAME'], request.META['SERVER_PORT']),
        full_path=request.get_full_path(),
        link=link,
        created_at=datetime.utcnow(),
        ip=request.META['REMOTE_ADDR'],
        browser=request.META['HTTP_USER_AGENT'] if 'HTTP_USER_AGENT' in request.META else None,
        referer=request.META['HTTP_REFERER'] if 'HTTP_REFERER' in request.META else None,
        lang=request.META['HTTP_ACCEPT_LANGUAGE'] if 'HTTP_ACCEPT_LANGUAGE' in request else None
    ).save()

    if link is None:
        raise Http404

    return redirect(link.long_url)

def new(request):
    # FIXME: Require a POST request

    try:
        login   = request.REQUEST['login']
        api_key = request.REQUEST['api_key']

        user = User.objects(login=login, api_key=api_key).first()
    except KeyError:
        user = None

    if user is None:
        return response(status=HTTP_UNAUTHORIZED, message="Invalid credentials.")

    try:
        long_url = request.REQUEST['long_url']
    except KeyError, e:
        return response(
            status=HTTP_BAD_REQUEST,
            message="Missing parameter: '%s'" % e.value)

    try:
        short_path = request.REQUEST['short_path']
    except KeyError, e:
        short_path = None

    if '/' in short_path:
        return response(
            status=HTTP_BAD_REQUEST,
            message="short_path contains a '/'.")

    try:
        prefix = request.REQUEST['prefix']
    except KeyError:
        prefix = ''

    if '/' in prefix:
        return response(
            status=HTTP_BAD_REQUEST,
            message="prefix contains a '/'.")

    params = {
        'long_url': long_url,
        'short_path': short_path,
        'prefix': prefix,
        'creator': user.login
    }

    try:
        link = Link.shorten(**params)
    except ShortPathConflict, e:
        del params['short_path'], params['prefix'], params['long_url']
        params['hash'] = e.link.hash

        return response(status=HTTP_CONFLICT, message=str(e), **params)

    params['short_path'] = link.short_path

    return response(**params)
