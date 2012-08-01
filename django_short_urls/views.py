from models import Link, User, ShortPathConflict

from django.shortcuts import redirect
from django.http import Http404

from w4l_http import response

def main(request, path):
    link = Link.find_by_short_path(short_path=path)

    # FIXME: Add tracking - WFU-1528

    if link is None:
        raise Http404

    return redirect(link.long_url)

def new(request):
    try:
        login   = request.REQUEST['login']
        api_key = request.REQUEST['api_key']

        user = User.objects(login=login, api_key=api_key).first()
    except KeyError:
        user = None

    if user is None:
        return response(status=HTTP_UNAUTHORIZED, message="Invalid credentials.")

    if 'long_url' in request.REQUEST:
        long_url = request.REQUEST['long_url']
    else:
        return response(
            status=HTTP_BAD_REQUEST,
            message="Missing parameter: 'long_url'")

    if 'short_path' in request.REQUEST:
        short_path = request.REQUEST['short_path']

        if '/' in short_path:
            return response(
                status=HTTP_BAD_REQUEST,
                message="short_path contains a '/'.")
    else:
        short_path = None

    if 'prefix' in request.REQUEST:
        prefix = request.REQUEST['prefix']

        if '/' in prefix:
            return response(
                status=HTTP_BAD_REQUEST,
                message="prefix contains a '/'.")
    else:
        prefix = ''

    params = {
        'long_url': long_url,
        'short_path': short_path,
        'prefix': prefix,
        'creator': user.login
    }

    try:
        link = Link.shorten(**params)
    except ShortPathConflict, e:
        return response(status=HTTP_CONFLICT, message=str(e), **params)

    params['short_path'] = link.short_path

    return response(**params)
