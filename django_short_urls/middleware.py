# coding=utf-8

"""Shared middleware for the Django Short Urls application"""

from __future__ import unicode_literals

from logging import getLogger

from django.conf import settings
import mongoengine

from utils.mongo import mongoengine_is_primary

from django_short_urls.w4l_http import response_service_unavailable


class ServiceUnavailableMiddleware(object):  # pylint: disable=too-few-public-methods
    """
    Middleware to handle application settings disabling database write access or the entire website (maintenance mode)
    """

    def __init__(self, get_response):
        """One time configuration and initialization."""
        self.get_response = get_response

    def __call__(self, request):
        """
        Called for every request. If the website is unavailable, or a request.method that would modify the database is
        invoked without a connection to a primary, returns an HTTP Service Unavailable response.
        """

        if settings.SERVICE_UNAVAILABLE or (request.method not in ("GET", "HEAD") and not mongoengine_is_primary()):
            # Can't use render because there is no context
            return response_service_unavailable()

        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):  # pylint: disable=no-self-use
        """
        Called for every view, and catches database connection issues to serve the proper maintenance page.
        """
        try:
            return view_func(request, *view_args, **view_kwargs)
        except mongoengine.connection.MongoEngineConnectionError as err:
            getLogger('app').error('Database access error: %s', err)

            return response_service_unavailable()
