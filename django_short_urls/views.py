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
    user = User.objects(login=request.REQUEST['login'], api_key=request.REQUEST['api_key']).first()
    
    if user is None:
        return HttpResponseForbidden("Invalid credentials.")
    
    # FIXME: Also support passing data as REQUEST parameters? - WFU-1422
    short_path = request.REQUEST['short_path']
    long_url   = request.REQUEST['long_url']
    
    link = Link.new(short_path=short_path, long_url=long_url)
    
    return HttpResponse(
        json.dumps({
            'short_path': short_path,
            'long_url': long_url
        }),
        mimetype="application/json"
    )
