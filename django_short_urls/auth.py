# coding=utf-8

"""Module to assist with authentication"""

from __future__ import unicode_literals

from decorator import decorator

from django_short_urls.models import User
from http.status import HTTP_UNAUTHORIZED
from http.utils import response


@decorator
def login_with_basic_auth_required(view, request, *args, **kwargs):
    """
    Django view decorator that requires basic authentication
    and sets request.user to a Django-Short-Urls User if found.
    Raises proper HTTP exceptions otherwise.
    """
    user = None

    if 'HTTP_AUTHORIZATION' in request.META:
        method, auth = request.META['HTTP_AUTHORIZATION'].split(' ', 1)

        if method.lower() == 'basic':
            login, api_key = auth.strip().decode('base64').split(':', 1)

            user = User.objects(login=login, api_key=api_key).first()  # pylint: disable=no-member

    if user is None:
        return response(status=HTTP_UNAUTHORIZED, message="Invalid credentials.")

    request.user = user

    return view(request, *args, **kwargs)
