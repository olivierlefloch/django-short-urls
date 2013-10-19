"""Urls for the django short urls application"""

from django.conf.urls import patterns, url
from django.views.generic.simple import direct_to_template

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns(
    '',
    (r'^robots\.txt$', direct_to_template,
        {'template': 'robots.txt', 'mimetype': 'text/plain'}),

    url(r'^api/v1/new$', 'django_short_urls.views.new', name='new'),
    url(r'^(.*)$', 'django_short_urls.views.main', name='main'),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
