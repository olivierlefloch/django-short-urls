from models import Link, User
from django.http import Http404, HttpResponseForbidden, HttpResponse
from django.shortcuts import redirect

def main(request, path):
    link = Link.objects(short_path=path).first()
    # link = Link.objects(short_path=path).first()
    
    if link is None:
        raise Http404
    
    return redirect(link.long_url)

def new(request):
    user = User.objects(login=request.POST['login'], api_key=request.POST['api_key']).first()
    
    if user is None:
        raise HttpResponseForbidden
    
    link = Link(short_path=request.POST['short_path'], long_url=request.POST['long_url']).save()
    
    return HttpResponse("%s -> %s\n" % (link.short_path, link.long_url))
