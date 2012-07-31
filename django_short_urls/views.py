import json
from models import Link, User
from django.http import Http404, HttpResponseForbidden, HttpResponse
from django.shortcuts import redirect

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
        return HttpResponseForbidden(
            json.dumps({
                "error": True,
                "message": "Invalid credentials."
            }),
            mimetype="application/json"
        )

    long_url   = request.REQUEST['long_url']
    short_path = request.REQUEST['short_path']

    if '/' in short_path:
        return HttpResponseForbidden("short_path contains a '/'.")

    link = Link.shorten(long_url=long_url, short_path=short_path, creator=user.login)

    return HttpResponse(
        json.dumps({
            'short_path': short_path,
            'long_url': long_url
        }),
        mimetype="application/json"
    )
