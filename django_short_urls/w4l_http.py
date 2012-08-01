from django.http import HttpResponse
import json

HTTP_OK           = 200
HTTP_BAD_REQUEST  = 400
HTTP_UNAUTHORIZED = 401
HTTP_CONFLICT     = 409

def response(message=None, status=HTTP_OK, **kwargs):
    kwargs.update({
        "status_code": status,
        "error": status != HTTP_OK,
        "message": message
    })

    return HttpResponse(json.dumps(kwargs), status=status, mimetype="application/json")
