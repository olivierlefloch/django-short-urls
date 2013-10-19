# coding=utf-8

"""Shared middleware for the Django Short Urls application"""

from __future__ import unicode_literals

# pylint: disable=W0511
# TODO: Move to a dedicated ServiceUnavailable app
from django.conf import settings

from django.utils.log import getLogger
import mongoengine

from django_short_urls.exceptions import DatabaseWriteDenied
from django_short_urls.w4l_http import reponse_service_unavailable


# pylint: disable=W0232, R0201, W0142
class ServiceUnavailableMiddleware:
    """
    Middleware to handle application settings disabling database write access or the entire website (maintenance mode)
    """

    def process_request(self, request):
        """
        Called for every request. If the website is unavailable, or a request.method that would modify the database is
        invoked, returns an HTTP Service Unavailable response.
        """

        if (
            settings.SERVICE_UNAVAILABLE
            or (settings.SITE_READ_ONLY and request.method not in ("GET", "HEAD"))
        ):
            # Can't use render because there is no context
            return reponse_service_unavailable()

    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        Called for every view, and catches database connection issues to serve the proper maintenance page.
        """
        try:
            return view_func(request, *view_args, **view_kwargs)
        except (mongoengine.connection.ConnectionError, DatabaseWriteDenied) as err:
            # TODO: Raise a DatabaseWriteDenied exception when trying to write to the database when in readonly mode.
            # Currently we rely on the developer checking settings.SITE_READ_ONLY in GET views.
            getLogger('app').error('Database access error: %s' % err)

            return reponse_service_unavailable()
