from django.conf import settings

import logging
import mongoengine

from w4l_http import reponse_service_unavailable

class ServiceUnavailableMiddleware:
    def process_request(self, request):
        if settings.SERVICE_UNAVAILABLE:
            # Can't use render because there is no context
            return reponse_service_unavailable()

    def process_view(self, request, view_func, view_args, view_kwargs):
        try:
            return view_func(request, *view_args, **view_kwargs)
        except mongoengine.connection.ConnectionError, e:
            logging.error('MongoEngine ConnectionError: %s' % e)

            return reponse_service_unavailable()
