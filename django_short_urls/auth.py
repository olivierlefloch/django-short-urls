# coding=utf-8

"""Module to assist with authentication"""

from __future__ import unicode_literals

from decorator import decorator

from django.http import HttpResponse

from django_short_urls.models import User
from http.status import HTTP_UNAUTHORIZED


def _safe_base64_decode(encoded):
    """Method that base64 decodes a string, while gracefully handing insufficient padding.
    Returns unicode, assuming utf-8 charset"""
    try:
        # Add extra padding just in case, because python is very strict and it can't hurt
        # http://stackoverflow.com/a/9807138
        return (encoded + "===").decode('base_64').decode('utf8')
    except Exception as err:  # pylint: disable=broad-except
        if err.message == 'Incorrect padding':
            # Adding the extra padding failed, there's no way we'll decode this
            return ''
        else:
            raise err


@decorator
def login_with_basic_auth_required(view, request, *args, **kwargs):
    """
    Django view decorator that requires basic authentication
    and sets request.user to a Django-Short-Urls User if found.
    Raises proper HTTP exceptions otherwise.
    """
    user = None

    if 'HTTP_AUTHORIZATION' in request.META:
        method, _, auth = request.META['HTTP_AUTHORIZATION'].partition(' ')

        if method.lower() == 'basic':
            login, _, api_key = _safe_base64_decode(auth.strip()).partition(':')

            user = User.objects(login=login, api_key=api_key).first()  # pylint: disable=no-member

    if user is None:
        response = HttpResponse("Authorization Required", status=HTTP_UNAUTHORIZED, content_type="text/plain")

        response['WWW-Authenticate'] = "Basic realm=API"

        return response

    request.user = user

    return view(request, *args, **kwargs)
