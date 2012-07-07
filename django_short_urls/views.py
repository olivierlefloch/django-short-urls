from models import Link
from django.http import Http404
from django.shortcuts import redirect

def main(request, path):
    # FIXME: Switch to proper logging
    print 'Path: %s' % path
    
    link = Link.objects.first()
    # link = Link.objects(short_path=path).first()
    
    if link is None:
        raise Http404
    
    return redirect(link.long_url)
