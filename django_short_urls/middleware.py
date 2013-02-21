# FIXME: Move to a dedicated ServiceUnavailable app
from django.conf import settings

from django.utils.log import getLogger
import mongoengine

from exceptions import DatabaseWriteDenied
from w4l_http import reponse_service_unavailable

class ServiceUnavailableMiddleware:
    def process_request(self, request):
        if settings.SERVICE_UNAVAILABLE
            or (settings.SITE_READ_ONLY and request.method not in ("GET", "HEAD")):
            # Can't use render because there is no context
            return reponse_service_unavailable()

    def process_view(self, request, view_func, view_args, view_kwargs):
        try:
            return view_func(request, *view_args, **view_kwargs)
        except (mongoengine.connection.ConnectionError, DatabaseWriteDenied) as e:
            # FIXME: Raise a DatabaseWriteDenied exception when trying to write to the database when in readonly mode. Currently we rely on the developer checking settings.SITE_READ_ONLY in GET views.
            getLogger('app').error('Database access error: %s' % e)

            return reponse_service_unavailable()
