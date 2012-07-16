from models import Link, User
from django.http import Http404, HttpResponseForbidden, HttpResponse
from django.shortcuts import redirect

def main(request, path):
    link = Link.find_by_short_path(short_path=path)
    
    # FIXME: Add tracking
    
    if link is None:
        raise Http404
    
    return redirect(link.long_url)

def new(request):
    user = User.objects(login=request.POST['login'], api_key=request.POST['api_key']).first()
    
    if user is None:
        return HttpResponseForbidden()
    
    # FIXME: Also support passing data as GET parameters?
    link = Link.new(
        short_path=request.POST['short_path'],
        long_url=request.POST['long_url'])
    
    return HttpResponse("%s" % link)
