"""Shared middleware for the Django Short Urls application"""

# FIXME: Move to a dedicated ServiceUnavailable app
from django.conf import settings

from django.utils.log import getLogger
import mongoengine

from exceptions import DatabaseWriteDenied
from w4l_http import reponse_service_unavailable


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
        except (mongoengine.connection.ConnectionError, DatabaseWriteDenied) as e:
            # FIXME: Raise a DatabaseWriteDenied exception when trying to write to the database when in readonly mode.
            # Currently we rely on the developer checking settings.SITE_READ_ONLY in GET views.
            getLogger('app').error('Database access error: %s' % e)

            return reponse_service_unavailable()
