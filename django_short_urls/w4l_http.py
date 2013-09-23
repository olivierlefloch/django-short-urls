from django.http import HttpResponse, QueryDict
from django.template import loader
import json
import requests
from urllib import urlencode
import urlparse

HTTP_OK                  = 200
HTTP_BAD_REQUEST         = 400
HTTP_UNAUTHORIZED        = 401
HTTP_FORBIDDEN           = 403
HTTP_CONFLICT            = 409
HTTP_SERVER_ERROR        = 500
HTTP_SERVICE_UNAVAILABLE = 503

def validate_url(url):
    parsed_url = urlparse.urlparse(url)

    if not parsed_url.netloc:
        return (False, "Url structure is invalid: '%s'" % url)

    if parsed_url.scheme not in ('http', 'https'):
        return (False, "Unsupported URL scheme: '%s'" % url)

    if parsed_url.password:
        return (False, "URLs containing passwords are not supported: '%s'" % url)

    return (True, None)


def url_append_parameters(url, params_to_replace, defaults):
    '''
    Appends the REDIRECT_PARAM_NAME param and the shorten's GET params
    to the long URL.
    Takes QueryDicts as parameters
    '''

    if not params_to_replace and not defaults:
        return url

    (scheme, netloc, path, params, link_query, fragment) = urlparse.urlparse(url)

    link_query = QueryDict(link_query).copy()

    for key, value in params_to_replace.iteritems():
        link_query[key] = value

    for key, value in defaults.iteritems():
        if key not in link_query:
            link_query[key] = value

    return urlparse.urlunparse((
        scheme, netloc, path, params,
        urlencode(link_query),
        fragment
    ))


def response(message=None, status=HTTP_OK, **kwargs):
    kwargs.update({
        "status_code": status,
        "error": status != HTTP_OK,
        "message": message
    })

    return HttpResponse(json.dumps(kwargs), status=status, mimetype="application/json")


def proxy(url):
    r = requests.get(url)

    return HttpResponse(
        r.content,
        status=r.status_code,
        mimetype=r.headers['Content-Type'])


def reponse_service_unavailable():
    return HttpResponse(loader.render_to_string('503.html'), status=HTTP_SERVICE_UNAVAILABLE)
