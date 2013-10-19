"""Urls for the django short urls application"""

from __future__ import unicode_literals

from django.conf.urls import patterns, url
from django.views.generic.base import TemplateView


# pylint: disable=C0103, E1120

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns(
    '',
    (r'^robots\.txt$', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),

    url(r'^api/v1/new$', 'django_short_urls.views.new', name='new'),
    url(r'^(.*)$', 'django_short_urls.views.main', name='main'),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
