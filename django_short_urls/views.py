from models import Link, User, ShortPathConflict

from django.shortcuts import redirect
from django.http import Http404

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

    for param in ('long_url', 'short_path'):
        if param not in request.REQUEST:
            return response(
                status=HTTP_BAD_REQUEST,
                message="Missing parameter: '%s'" % param)

    long_url   = request.REQUEST['long_url']
    short_path = request.REQUEST['short_path']

    if '/' in short_path:
        return response(status=HTTP_BAD_REQUEST, message="short_path contains a '/'.")

    try:
        link = Link.shorten(long_url=long_url, short_path=short_path, creator=user.login)
    except ShortPathConflict, e:
        return response(status=HTTP_CONFLICT, message=str(e), short_path=short_path)

    return response(short_path=short_path, long_url=long_url)

# TODO: Move the following code to a seperate file

from django.http import HttpResponse
import json

HTTP_OK           = 200
HTTP_BAD_REQUEST  = 400
HTTP_UNAUTHORIZED = 401
HTTP_CONFLICT     = 409

def response(message=None, status=HTTP_OK, **kwargs):
    kwargs.update({
        "error": status != HTTP_OK,
        "message": message
    })

    return HttpResponse(json.dumps(kwargs), status=status, mimetype="application/json")
